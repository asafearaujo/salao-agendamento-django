from django.contrib import admin
from .models import Servico, Agendamento, Profissional

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao_minutos')
    search_fields = ('nome',)


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    # Mostra o nome do barbeiro e se ele está ativo na listagem
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    # Adicionado o 'profissional' na listagem para o dono do salão saber quem vai atender
    list_display = ('cliente', 'servico', 'profissional', 'data_hora', 'status')
    list_filter = ('status', 'data_hora', 'profissional')  # Filtra também por barbeiro
    search_fields = ('cliente__username', 'servico__nome', 'profissional__nome')