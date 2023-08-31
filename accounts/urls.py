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
        ),
    
    path(
        "get_status_on_login/", views.get_status_on_login,
        name="get_status_on_login"
    ),
    
    path(
        "view_all_users/", views.view_all_users,
        name="view_all_users"
    )
]
