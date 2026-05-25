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
    # Busca os agendamentos onde o cliente é o usuário logado, ordenando pelos mais recentes
    agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('-data_hora')
    return render(request, 'core/meus_agendamentos.html', {'agendamentos': agendamentos})