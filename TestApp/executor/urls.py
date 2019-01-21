from django.urls import path
import executor.views as views

app_name = 'executor'
urlpatterns = [
    # ex: /executor/
    # path('findMissing', findMissing, name='find-missing'),
    # path('results', results, name='myresults'),
    # # ex: /blog/dusan
    # path('helprequests', help_requests, name='help-requests'),
    path('start_workflow/<int:pk>', views.start_workflow, name='start_workflow'),
    path('assign_add/', views.assign_role, name='role_assign_add'),
    path('next_task/<int:pk>', views.next_task, name='next_task'),
    path('load-roles/', views.load_roles, name='ajax_load_roles'),
    # # path('',accept_volunteering, name='accept_volunteering')
    # # path('',reject_volunteering, name='reject_volunteering')
    # # ex: /blog/post/5/
    # path('post/<int:pk>/', PostView.as_view(), name='post'),
    # # ex: /blog/post/5/comment/
    # path('post/<int:pk>/comment/', CommentCreate.as_view(), name='create_comment')
]
