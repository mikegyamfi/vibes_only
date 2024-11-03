from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
from .auth import authViews
from .shop import shopViews

urlpatterns = [
    path('', views.home, name="home"),
    path('services', views.services, name='services'),
    path('services/mtn', views.mtn, name='mtn'),
    path('services/airtel-tigo/', views.airtel_tigo, name='airtel-tigo'),
    path('services/mtn/', views.mtn, name='mtn'),
    path('services/telecel/', views.telecel, name='telecel'),
    path('services/big_time/', views.big_time, name='big_time'),
    path('services/afa/', views.afa_registration, name='afa'),
    path('history/airtel-tigo', views.history, name='history'),
    path('history/mtn', views.mtn_history, name="mtn-history"),
    path('history/telecel', views.telecel_history, name="telecel-history"),
    path('history/big_time', views.big_time_history, name="bt-history"),
    path('history/afa', views.afa_history, name="afa-history"),

    path('pay_with_wallet/', views.pay_with_wallet, name='pay_with_wallet'),
    path('mtn_pay_with_wallet/', views.mtn_pay_with_wallet, name='mtn_pay_with_wallet'),
    path('telecel_pay_with_wallet/', views.telecel_pay_with_wallet, name='telecel_pay_with_wallet'),
    path('big_time_pay_with_wallet/', views.big_time_pay_with_wallet, name='big_time_pay_with_wallet'),
    path('afa_pay_with_wallet/', views.afa_registration_wallet, name='afa_pay_with_wallet'),

    path('topup-info', views.topup_info, name='topup-info'),
    path("request_successful/<str:reference>", views.request_successful, name='request_successful'),
    path('elevated/topup-list', views.topup_list, name="topup_list"),
    # path('credit/<str:reference>', views.credit_user_from_list, name='credit'),
    #
    # path('import_thing', views.populate_custom_users_from_excel, name="import_users"),
    # path('delete', views.delete_custom_users, name='delete'),

    path('login', authViews.login_page, name='login'),
    path('signup', authViews.sign_up, name='signup'),
    path('logout', authViews.logout_user, name="logout"),

    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),
    path('paystack_webhook', views.paystack_webhook, name='paystack_webhook'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
