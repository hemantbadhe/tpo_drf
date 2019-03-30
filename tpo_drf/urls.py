from django.urls import path, include
from rest_framework import routers

from tpo_drf import views

router = routers.DefaultRouter()
router.register('college_user', views.CollegeUserViewSet, 'college_user')
router.register('create_student', views.CreateStudentViewSet, 'create_student')
router.register('user', views.UserViewSet, 'user')
router.register('user_list', views.UserListViewSet, 'user_list')
router.register('login', views.LoginViewSet, 'login')
router.register('drives', views.DriveViewSet, 'drives')
router.register('placed_student', views.PlacedStudentViewSet, 'placed_student')

#
router.register('college_student', views.CollegeStudentViewSet, 'college_student')
router.register('college_teacher', views.CollegeTeacherViewSet, 'college_teacher')

router.register('tpo_student', views.TpoStudentViewSet, 'tpo_student')
router.register('tpo_teacher', views.TpoTeacherViewSet, 'tpo_teacher')

# chat message list and create chat message
router.register('chat', views.ChatViewSet, 'chat')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout_view),
    path('dashboard/', views.dashboard),
    path('send_notification/', views.send_notification),

]
