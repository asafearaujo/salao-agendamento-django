from django.urls import path
from . import views  # Importa o arquivo views inteiro de uma vez

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/<int:servico_id>/', views.agendar, name='agendar'),
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('ocultar/<int:agendamento_id>/', views.esconder_agendamento, name='esconder_agendamento'),
    path('limpar-historico/', views.limpar_historico_geral, name='limpar_historico_geral'),  # <- E ASSIM
]