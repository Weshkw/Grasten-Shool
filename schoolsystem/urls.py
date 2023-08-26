from django.urls import path
from . import views




urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('resetpassword/', views.reset_password, name='reset_password'),
    path('news/',views.news, name='news'),
    path('fees-structure/', views.fees_structure_detail, name='fees_structure'),
    path('view_fee_payments/', views.view_fee_payments, name='view_fee_payments'),
    path('educational_resources/', views.educational_resources, name='educational_resources'),
    path('all_resources/', views.all_resources_view, name='all_resources'),
    path('student_results/', views.view_student_results, name='studentresult'),
    path('search/', views.search_results_view, name='search_results'),
    
]