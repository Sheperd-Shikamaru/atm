from django.urls import path
from . import views
from .views import UserRegistrationView, LogoutView, UserLoginView


app_name = 'accounts'

urlpatterns = [
    # path(
    #     "login/", UserLoginView.as_view(),
    #     name="user_login"
    # ),
    path(
        "logout/", LogoutView.as_view(),
        name="user_logout"
    ),
    path(
        "register/", UserRegistrationView.as_view(),
        name="user_registration"
    ),
    
    path(
        "login/", views.custom_login, 
        name="user_login"
        )
]
