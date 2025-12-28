"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.web_views import home,login_view, register_view,logout_view,dashboard,transactions_page, delete_transaction,profile_view
from django.contrib.auth import views as auth_views
from users.web_views import export_transactions_csv

urlpatterns = [
    path("", home, name="home"),
    path('admin/', admin.site.urls),
     path('api/auth/', include('users.urls')),  # register/

    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include("expenses.urls")),
    #frontend login and sign up
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("transactions/", transactions_page, name="transactions"),
    path("transactions/delete/<int:pk>/", delete_transaction),
    path("profile/", profile_view, name="profile"),
    path(
  "password-change/",
  auth_views.PasswordChangeView.as_view(
      template_name="password_change.html",
      success_url="/password-change-done/"
  ),
  name="password_change",
),

path(
  "password-change-done/",
  auth_views.PasswordChangeDoneView.as_view(
      template_name="password_change_done.html"
  ),
  name="password_change_done",
),
path("transactions/export/", export_transactions_csv, name="transactions_export"),

]
