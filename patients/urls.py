from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('records/', views.my_records, name='my_records'),
    path('records/<uuid:record_id>/', views.record_detail, name='record_detail'),
    path('qr-card/', views.my_qr_card, name='my_qr_card'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
]
