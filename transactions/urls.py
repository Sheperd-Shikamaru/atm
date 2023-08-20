from django.urls import path
from . import views
from .views import DepositMoneyView, WithdrawMoneyView, TransactionRepostView


app_name = 'transactions'


urlpatterns = [
    path("fingerprint_register/", views.fingerprint_register, name="fingerprint_register"),
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("report/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("fingerprint/", views.fingerprint_auth, name='fingerprint')

]
