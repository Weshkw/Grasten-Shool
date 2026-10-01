from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("news/", views.news, name="news"),
    path("fees-structure/", views.fees_structure, name="fees_structure"),
    path("account-help/", views.account_help, name="account_help"),
    path("resources/", views.educational_resources, name="educational_resources"),
    path("results/", views.student_results, name="student_results"),
    path("fees/", views.fee_payments, name="fee_payments"),
    path("search/", views.search, name="search"),
]
