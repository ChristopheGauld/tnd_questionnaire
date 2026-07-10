from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('questionnaire/<uuid:public_id>/', views.questionnaire_start, name='questionnaire_start'),
    path(
        'questionnaire/<uuid:public_id>/page/<int:page_number>/',
        views.questionnaire_page,
        name='questionnaire_page',
    ),
    path('merci/', views.thank_you, name='thank_you'),
    path('export/<int:questionnaire_id>/xlsx/', views.export_xlsx, name='export_xlsx'),
]
