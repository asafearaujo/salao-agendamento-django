from django.db import models
from django.contrib.auth.models import User

class Servico(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Serviço")
    descricao = models.TextField(verbose_name="Descrição")
    preco = models.DecimalField(max_length=10, decimal_places=2, max_digits=10, verbose_name="Preço")
    duracao_minutos = models.IntegerField(verbose_name="Duração (minutos)")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"


# 🆕 NOVO MODELO: Adicione esta classe aqui
class Profissional(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Barbeiro")
    ativo = models.BooleanField(default=True, verbose_name="Disponível para Agendamentos")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
        ('CONCLUIDO', 'Concluído'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Cliente")
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, verbose_name="Serviço")
    
    # 🆕 ATUALIZAÇÃO: Vamos conectar o agendamento ao profissional escolhido
    profissional = models.ForeignKey(Profissional, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Barbeiro")
    
    data_hora = models.DateTimeField(verbose_name="Data e Horário")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO', verbose_name="Status")
    visivel_para_o_cliente = models.BooleanField(default=True, verbose_name="Visível para o cliente")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data do Agendamento")

    def __str__(self):
        return f"{self.cliente.username} - {self.servico.nome} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"