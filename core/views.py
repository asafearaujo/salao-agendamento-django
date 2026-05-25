from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Servico, Agendamento

def home(request):
    servicos = Servico.objects.all()
    return render(request, 'core/home.html', {'servicos': servicos})

@login_required  # Só usuários logados podem acessar essa tela de agendamento
def agendar(request, servico_id):
    # Busca o serviço pelo ID ou dá erro 404 caso o ID não exista
    servicio = get_object_or_404(Servico, id=servico_id)
    
    if request.method == 'POST':
        data_hora = request.POST.get('data_hora')
        
        # Cria o agendamento associando o cliente logado, o serviço e a data escolhida
        Agendamento.objects.create(
            cliente=request.user,
            servico=servicio,
            data_hora=data_hora,
            status='AGENDADO'
        )
        # Por enquanto, após agendar, redireciona de volta para a Home
        return redirect('meus_agendamentos')

    return render(request, 'core/agendar.html', {'servicio': servicio})

@login_required
def meus_agendamentos(request):
    # ATUALIZADO: Filtra apenas os agendamentos ativos na tela do cliente
    agendamentos = Agendamento.objects.filter(
        cliente=request.user,
        visivel_para_o_cliente=True
    ).order_by('-data_hora')
    return render(request, 'core/meus_agendamentos.html', {'agendamentos': agendamentos})


@login_required
def cancelar_agendamento(request, agendamento_id):
    # Busca o agendamento pelo ID, garantindo que ele pertence ao usuário logado
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user)
    
    # Se o agendamento ainda estiver como marcado, muda para cancelado
    if agendamento.status == 'AGENDADO':
        agendamento.status = 'CANCELADO'
        agendamento.save()
        
    # Redireciona o usuário de volta para a página de listagem
    return redirect('meus_agendamentos')


# ADICIONA ESTA NOVA FUNÇÃO COMPLETA NO FINAL DO ARQUIVO:
@login_required
def esconder_agendamento(request, agendamento_id):
    # Busca o agendamento do cliente logado
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user)
    
    # Modifica a flag de visibilidade para esconder da listagem do cliente
    agendamento.visivel_para_o_cliente = False
    agendamento.save()
    
    return redirect('meus_agendamentos')


@login_required
def limpar_historico_geral(request):
    # Pega todos os agendamentos do usuário que NÃO estão com status 'AGENDADO'
    # e muda a visibilidade deles para False de uma vez só
    Agendamento.objects.filter(
        cliente=request.user
    ).exclude(
        status='AGENDADO'
    ).update(visivel_para_o_cliente=False)
    
    return redirect('meus_agendamentos')