from django.urls import path
from .views import home, agendar,meus_agendamentos

urlpatterns = [
    path('', home, name='home'),
    path('agendar/<int:servico_id>/', agendar, name='agendar'),
    path('meus-agendamentos/', meus_agendamentos, name='meus_agendamentos'),  # Nova rota aqui
]