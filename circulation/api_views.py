from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (CatalogContractError, as_payload, borrow, get_book_model,
                       is_staff_operator, renew, return_book,
                       require_circulation_contract)

User = get_user_model()


class CirculationView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def catalog_error(error):
        return Response({"detail": str(error)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LoanListView(CirculationView):
    def get(self, request):
        try:
            model = get_book_model()
            require_circulation_contract(model)
        except CatalogContractError as error:
            return self.catalog_error(error)
        queryset = model.objects.filter(borrower__isnull=False).select_related("book")
        if not is_staff_operator(request.user):
            queryset = queryset.filter(borrower=request.user)
        return Response([as_payload(instance) for instance in queryset.order_by("due_back")])


class BorrowView(CirculationView):
    def post(self, request):
        if not is_staff_operator(request.user):
            return Response({"detail": "Librarian or Admin permission required"}, status=status.HTTP_403_FORBIDDEN)
        member_id = request.data.get("member_id")
        book_instance_id = request.data.get("book_instance_id")
        if not member_id or not book_instance_id:
            return Response({"detail": "member_id and book_instance_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member_id = int(member_id)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid member_id format. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = User.objects.get(pk=member_id, is_active=True)
        except User.DoesNotExist:
            return Response({"detail": "Member does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance = borrow(book_instance_id, member)
        except CatalogContractError as error:
            return self.catalog_error(error)
        except (ValueError, KeyError) as e:
            return Response({"detail": f"Book instance is unavailable: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            model = get_book_model()
            if isinstance(error, model.DoesNotExist):
                return Response({"detail": "Book instance does not exist"}, status=status.HTTP_404_NOT_FOUND)
            raise
        return Response(as_payload(instance), status=status.HTTP_201_CREATED)


class RenewView(CirculationView):
    def patch(self, request, pk):
        if not is_staff_operator(request.user):
            return Response({"detail": "Librarian or Admin permission required"}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = renew(pk, date.fromisoformat(request.data["due_back"]))
        except (KeyError, ValueError):
            return Response({"detail": "due_back must be a later ISO date"}, status=status.HTTP_400_BAD_REQUEST)
        except CatalogContractError as error:
            return self.catalog_error(error)
        return Response(as_payload(instance))


class ReturnView(CirculationView):
    def post(self, request, pk):
        if not is_staff_operator(request.user):
            return Response({"detail": "Librarian or Admin permission required"}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = return_book(pk)
        except ValueError:
            return Response({"detail": "Book instance cannot be returned"}, status=status.HTTP_400_BAD_REQUEST)
        except CatalogContractError as error:
            return self.catalog_error(error)
        return Response(as_payload(instance))
