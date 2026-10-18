from django.urls import path

from .api_views import BorrowView, LoanListView, RenewView, ReturnView

urlpatterns = [
    path("loans/", LoanListView.as_view(), name="circulation-loans"),
    path("loans/borrow/", BorrowView.as_view(), name="circulation-borrow"),
    path("loans/<uuid:pk>/renew/", RenewView.as_view(), name="circulation-renew"),
    path("loans/<uuid:pk>/return/", ReturnView.as_view(), name="circulation-return"),
]
