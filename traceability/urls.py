from django.urls import path
from . import views

app_name = 'traceability'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('admin/', views.admin_screen, name='admin_screen'),
    path('user/', views.user_screen, name='user_screen'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_tracing/', views.add_tracing, name='add_tracing'),
    path('add_tracing_action/', views.add_tracing_action, name='add_tracing_action'),
    path('view_tracing/', views.view_tracing, name='view_tracing'),
    path('update_tracing/', views.update_tracing, name='update_tracing'),
]
