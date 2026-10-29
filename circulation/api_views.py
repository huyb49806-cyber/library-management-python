from datetime import date

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    CatalogContractError,
    as_payload,
    borrow,
    get_book_model,
    is_staff_operator,
    renew,
    return_book,
    require_circulation_contract,
    status_value,
)

User = get_user_model()


class CirculationView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def catalog_error(error):
        return Response(
            {"detail": str(error)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class LoanListView(CirculationView):
    def get(self, request):
        try:
            model = get_book_model()
            require_circulation_contract(model)
        except CatalogContractError as error:
            return self.catalog_error(error)

        queryset = model.objects.filter(
            borrower__isnull=False,
            status=status_value(model, "on_loan"),
        ).select_related("book")

        if not is_staff_operator(request.user):
            queryset = queryset.filter(borrower=request.user)

        return Response([
            as_payload(instance)
            for instance in queryset.order_by("due_back")
        ])


class BorrowView(CirculationView):
    def post(self, request):
        if not is_staff_operator(request.user):
            return Response(
                {"detail": "Librarian or Admin permission required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        raw_member_id = request.data.get("member_id")
        raw_book_instance_id = request.data.get("book_instance_id")

        if not raw_member_id or not raw_book_instance_id:
            return Response(
                {"detail": "Vui lòng cung cấp thông tin độc giả (member_id) và bản sao sách (book_instance_id)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member_str = str(raw_member_id).strip()
        member = None
        if member_str.isdigit():
            member = User.objects.filter(pk=int(member_str), is_active=True).first()
        if not member:
            member = User.objects.filter(username__iexact=member_str, is_active=True).first()
        if not member:
            member = User.objects.filter(email__iexact=member_str, is_active=True).first()
        if not member:
            member = User.objects.filter(profile__student_code__iexact=member_str, is_active=True).first()

        if not member:
            return Response(
                {"detail": f"Không tìm thấy độc giả với thông tin: '{raw_member_id}'. Vui lòng nhập đúng ID hoặc Tên đăng nhập."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model = get_book_model()
        require_circulation_contract(model)

        inst_str = str(raw_book_instance_id).strip()
        target_instance_id = None

        # 1. Tìm trực tiếp theo UUID của BookInstance
        try:
            matched_inst = model.objects.filter(pk=inst_str).first()
            if matched_inst:
                if matched_inst.status == status_value(model, "available"):
                    target_instance_id = matched_inst.pk
                else:
                    # Bản sao này đang bận, tự động lấy bản sao khác có sẵn của cùng đầu sách
                    other_inst = model.objects.filter(
                        book_id=matched_inst.book_id,
                        status=status_value(model, "available")
                    ).first()
                    if other_inst:
                        target_instance_id = other_inst.pk
                    else:
                        return Response(
                            {"detail": f"Bản sao '{inst_str}' ({matched_inst.book.title}) hiện không có sẵn (đang mượn hoặc bảo trì) và đầu sách này đã hết bản sao sẵn có trong kho."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
        except (ValueError, ValidationError):
            target_instance_id = None

        # 2. Nếu không phải UUID, tìm theo Book ID (số nguyên)
        if not target_instance_id and inst_str.isdigit():
            matched_inst = model.objects.filter(
                book_id=int(inst_str),
                status=status_value(model, "available")
            ).first()
            if matched_inst:
                target_instance_id = matched_inst.pk
            else:
                if model.objects.filter(book_id=int(inst_str)).exists():
                    return Response(
                        {"detail": f"Đầu sách #{inst_str} hiện đã hết bản sao sẵn có trong kho."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # 3. Tìm theo Tên sách hoặc Mã ISBN
        if not target_instance_id:
            matched_inst = model.objects.filter(
                Q(book__title__iexact=inst_str) | Q(book__isbn=inst_str),
                status=status_value(model, "available")
            ).first()
            if matched_inst:
                target_instance_id = matched_inst.pk
            elif model.objects.filter(Q(book__title__iexact=inst_str) | Q(book__isbn=inst_str)).exists():
                return Response(
                    {"detail": f"Sách '{inst_str}' hiện đã hết bản sao sẵn có trong kho."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not target_instance_id:
            return Response(
                {"detail": f"Không tìm thấy bản sao sách với thông tin: '{raw_book_instance_id}'. Vui lòng chọn bản sao có sẵn hoặc nhập đúng UUID / ID sách."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instance = borrow(target_instance_id, member)
        except CatalogContractError as error:
            return self.catalog_error(error)
        except (ValueError, KeyError) as error:
            return Response(
                {"detail": f"Không thể lập lượt mượn: {error}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            if isinstance(error, (model.DoesNotExist, ValidationError)):
                return Response(
                    {"detail": "Bản sao sách không tồn tại hoặc không hợp lệ."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            raise

        return Response(
            as_payload(instance),
            status=status.HTTP_201_CREATED,
        )


class RenewView(CirculationView):
    def patch(self, request, pk):
        if not is_staff_operator(request.user):
            return Response(
                {"detail": "Librarian or Admin permission required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            raw_due_back = request.data["due_back"]
            if not isinstance(raw_due_back, str):
                raise ValueError

            new_due_back = date.fromisoformat(raw_due_back)
            instance = renew(pk, new_due_back)
        except (KeyError, TypeError, ValueError):
            return Response(
                {"detail": "due_back must be a later ISO date"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CatalogContractError as error:
            return self.catalog_error(error)
        except Exception as error:
            model = get_book_model()
            if isinstance(error, (model.DoesNotExist, ValidationError)):
                return Response(
                    {"detail": "Book instance does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            raise

        return Response(as_payload(instance))


class ReturnView(CirculationView):
    def post(self, request, pk):
        if not is_staff_operator(request.user):
            return Response(
                {"detail": "Librarian or Admin permission required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            instance = return_book(pk)
        except ValueError:
            return Response(
                {"detail": "Book instance cannot be returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CatalogContractError as error:
            return self.catalog_error(error)
        except Exception as error:
            model = get_book_model()
            if isinstance(error, (model.DoesNotExist, ValidationError)):
                return Response(
                    {"detail": "Book instance does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            raise

        return Response(as_payload(instance))