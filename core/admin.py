from django.contrib import admin
from .models import Servico, Agendamento

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao_minutos')
    search_fields = ('nome',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servico', 'data_hora', 'status')
    list_filter = ('status', 'data_hora')  # Cria filtros na lateral direita do painel
    search_fields = ('cliente__username', 'servico__nome')