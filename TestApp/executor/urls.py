from django.urls import path
import executor.views as views

app_name = 'executor'
urlpatterns = [
    path('start_workflow/<int:pk>', views.start_workflow, name='start_workflow'),
    path('assign_add/', views.assign_role, name='role_assign_add'),
    path('next_task/<int:pk>', views.next_task, name='next_task'),
    path('load-roles/', views.load_roles, name='ajax_load_roles'),
    path('specify-workflow/', views.specify_workflow, name='specify_workflow'),
    path('worklist/', views.show_worklist, name='worklist'),
]
