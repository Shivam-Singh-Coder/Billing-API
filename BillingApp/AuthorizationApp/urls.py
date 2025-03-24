from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from AuthorizationApp import views as auth_views

urlpatterns = [
    path("login/", auth_views.CustomLoginView.as_view(), name="login"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token-refresh"),
    path("company/create/", auth_views.CompanyCreateView.as_view(), name="company-create"),
    path("company/list/", auth_views.CompanyListView.as_view(), name="company-list"),
    path("company/detail/<int:company_id>/", auth_views.CompanyDetailView.as_view(), name="company-detail"),
    path("company/edit/<int:company_id>/", auth_views.CompanyUpdateView.as_view(), name="company-edit"),
    path("company/delete/<int:company_id>/", auth_views.CompanyDeleteView.as_view(), name="company-delete"),
    path("software-type/create/", auth_views.SoftwareTypeCreateView.as_view(), name="software-type-create"),
    path("software-type/list/", auth_views.SoftwareTypeListView.as_view(), name="software-type-list"),
    path("software-type/detail/<int:software_id>/", auth_views.SoftwareTypeDetailView.as_view(), name="software-type-detail"),
    path("software-type/edit/<int:software_id>/", auth_views.SoftwareTypeUpdateView.as_view(), name="software-type-edit"),
    path("software-type/delete/<int:software_id>/", auth_views.SoftwareTypeDeleteView.as_view(), name="software-type-delete"),
    # path("register/", TokenRefreshView.as_view(), name="garments_token_refresh"),
]
