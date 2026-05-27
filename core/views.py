from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Servico, Agendamento, Profissional
from datetime import datetime, timedelta, time

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


@login_required  
def agendar(request, servico_id):
    servicio = get_object_or_404(Servico, id=servico_id)
    profissionais = Profissional.objects.filter(ativo=True)
    
    # Variáveis de controle para a tela
    horarios_disponiveis = []
    data_selecionada = request.GET.get('data')
    profissional_selecionado = request.GET.get('profissional')
    erro = None

    # 🆕 LÓGICA DO CARROSSEL: Gerar os próximos 14 dias a partir de hoje (pulando domingos)
    proximos_dias = []
    dias_da_semana_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    data_atual_loop = datetime.now()
    # Se o cliente entrar no salão domingo, começamos a listar a partir de segunda
    if data_atual_loop.weekday() == 6:
        data_atual_loop += timedelta(days=1)

    while len(proximos_dias) < 14:
        if data_atual_loop.weekday() != 6:  # Pula o domingo (6)
            proximos_dias.append({
                'id_data': data_atual_loop.strftime('%Y-%m-%d'),
                'dia_nome': dias_da_semana_pt[data_atual_loop.weekday()],
                'dia_numero': data_atual_loop.strftime('%d'),
                'mes_nome': data_atual_loop.strftime('%b').lower()
            })
        data_atual_loop += timedelta(days=1)

    # FASE 1 (GET): Calcular horários se barbeiro e data forem escolhidos
    if data_selecionada and profissional_selecionado:
        try:
            data_foco = datetime.strptime(data_selecionada, '%Y-%m-%d').date()
            
            if data_foco.weekday() == 6:
                erro = "O salão não abre aos domingos!"
            elif data_foco < datetime.now().date():
                erro = "Você não pode escolher uma data que já passou!"
            else:
                # 1. Buscar horários ocupados
                agendamentos_do_dia = Agendamento.objects.filter(
                    profissional_id=profissional_selecionado,
                    data_hora__date=data_foco
                ).exclude(status='CANCELADO')

                horas_ocupadas = [agendamento.data_hora.time() for agendamento in agendamentos_do_dia]

                # 2. Gerar slots de 30 em 30 min (08h às 20h)
                hora_atual = datetime.combine(data_foco, time(8, 0))
                hora_fim = datetime.combine(data_foco, time(20, 0))

                while hora_atual < hora_fim:
                    slot_time = hora_atual.time()
                    if slot_time not in horas_ocupadas:
                        if data_foco > datetime.now().date() or hora_atual > datetime.now():
                            horarios_disponiveis.append(slot_time.strftime('%H:%M'))
                    hora_atual += timedelta(minutes=30)
                    
                if not horarios_disponiveis and not erro:
                    erro = "Não há mais horários disponíveis para esta data."
                    
        except ValueError:
            erro = "Data inválida."

    # FASE 2 (POST): Confirmar agendamento
    if request.method == 'POST':
        data_str = request.POST.get('data')
        hora_str = request.POST.get('hora')
        profissional_id = request.POST.get('profissional')

        if data_str and hora_str and profissional_id:
            data_hora_final = datetime.strptime(f"{data_str} {hora_str}", '%Y-%m-%d %H:%M')
            
            if data_hora_final.hour < 8 or data_hora_final.hour >= 20:
                erro = "Horário inválido!"
            else:
                conflito = Agendamento.objects.filter(
                    profissional_id=profissional_id,
                    data_hora=data_hora_final
                ).exclude(status='CANCELADO').exists()

                if conflito:
                    erro = "Este horário já foi preenchido por outro cliente!"
                
                if not erro:
                    profissional_escolhido = get_object_or_404(Profissional, id=profissional_id)
                    Agendamento.objects.create(
                        cliente=request.user,
                        servico=servicio,
                        profissional=profissional_escolhido,
                        data_hora=data_hora_final,
                        status='AGENDADO'
                    )
                    return redirect('meus_agendamentos')

    return render(request, 'core/agendar.html', {
        'servicio': servicio, 
        'profissionais': profissionais,
        'horarios_disponiveis': horarios_disponiveis,
        'data_selecionada': data_selecionada,
        'profissional_selecionado': profissional_selecionado,
        'proximos_dias': proximos_dias, # 🆕 Lista de dias horizontais
        'erro': erro
    })