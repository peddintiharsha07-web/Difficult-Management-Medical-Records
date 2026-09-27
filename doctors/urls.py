from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('search-patient/', views.search_patient, name='search_patient'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('patient/<str:medical_id>/', views.patient_detail, name='patient_detail'),
    path('patient/<str:medical_id>/create-record/', views.create_record, name='create_record'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/<uuid:appointment_id>/status/', views.update_appointment_status,
         name='update_appointment_status'),
]
