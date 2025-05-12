from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Danh sách nhân viên
    path('', views.StaffListView.as_view(), name='list'),
    
    # Chi tiết nhân viên
    path('<int:pk>/', views.StaffDetailView.as_view(), name='detail'),
    
    # Thêm nhân viên mới
    path('add/', views.StaffCreateView.as_view(), name='create'),
    
    # Chỉnh sửa thông tin nhân viên
    path('<int:pk>/edit/', views.StaffUpdateView.as_view(), name='update'),
    
    # Thêm lịch làm việc cho nhân viên
    path('<int:staff_id>/schedule/add/', views.StaffScheduleCreateView.as_view(), name='add_schedule'),
    
    # Thêm hiệu suất cho nhân viên
    path('<int:staff_id>/performance/add/', views.PerformanceCreateView.as_view(), name='add_performance'),
    
    # API lấy dữ liệu hiệu suất
    path('api/performance/<int:staff_id>/', views.staff_performance_api, name='performance_api'),
] 