from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Aluno, Matricula, Presenca, Pagamento, Plano
from .forms import AlunoForm, PlanoForm
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.db.models import Sum
import calendar
from datetime import date
from .utils import render_to_pdf

@login_required
def lista_alunos(request):
    # 1. Lógica de Busca (Mantém igual)
    termo_busca = request.GET.get('busca')
    if termo_busca:
        alunos = Aluno.objects.filter(
            Q(nome_completo__icontains=termo_busca) |
            Q(cpf__icontains=termo_busca)
        ).order_by('nome_completo')
    else:
        alunos = Aluno.objects.all().order_by('nome_completo')

    # --- NOVO: Descobrir quem já veio hoje ---
    hoje = timezone.now().date()
    
    # Pega a lista de IDs de alunos que têm presença HOJE
    ids_presentes_hoje = Presenca.objects.filter(data_aula=hoje).values_list('aluno_id', flat=True)
    
    # Adiciona uma "etiqueta" temporária em cada aluno da lista
    for aluno in alunos:
        aluno.treinou_hoje = aluno.id in ids_presentes_hoje

    # 2. Estatísticas (Mantém igual)
    total_alunos = Aluno.objects.count()
    alunos_em_dia = Matricula.objects.filter(ativo=True, data_vencimento__gte=hoje).count()
    alunos_vencidos = Matricula.objects.filter(ativo=True, data_vencimento__lt=hoje).count()

    context = {
        'alunos': alunos,
        'termo_busca': termo_busca,
        'total_alunos': total_alunos,
        'alunos_em_dia': alunos_em_dia,
        'alunos_vencidos': alunos_vencidos,
    }
    return render(request, 'core/lista_alunos.html', context)

@login_required
def editar_aluno(request, id):
    aluno = get_object_or_404(Aluno, pk=id)
    matricula = aluno.matricula_set.first()
    pagamentos = aluno.pagamento_set.all().order_by('-data_pagamento')[:5]
    todos_planos = Plano.objects.all()

    # --- LÓGICA DO CALENDÁRIO ---
    hoje = timezone.now()
    ano = hoje.year
    mes = hoje.month
    
    # 1. Pega todas as datas que o aluno veio neste mês/ano
    dias_presenca = Presenca.objects.filter(
        aluno=aluno,
        data_aula__year=ano, 
        data_aula__month=mes
    ).values_list('data_aula', flat=True)
    
    # Converte para um conjunto de números (ex: {5, 12, 14}) para ser rápido de buscar
    dias_presenca_set = {d.day for d in dias_presenca}

    # 2. Gera o calendário do mês (matriz de semanas)
    cal = calendar.Calendar(firstweekday=6) # 6 = Domingo
    dias_do_mes = cal.monthdayscalendar(ano, mes)
    
    # 3. Cria uma lista estruturada para o HTML
    calendario_html = []
    for semana in dias_do_mes:
        semana_html = []
        for dia in semana:
            if dia == 0:
                semana_html.append(None) # Dia de outro mês
            else:
                semana_html.append({
                    'dia': dia,
                    'presente': dia in dias_presenca_set, # True ou False
                    'hoje': (dia == hoje.day)
                })
        calendario_html.append(semana_html)

    # --- FIM LOGICA CALENDÁRIO ---

    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AlunoForm(instance=aluno)

    context = {
        'form': form,
        'aluno': aluno,
        'matricula': matricula,
        'pagamentos': pagamentos,
        'todos_planos': todos_planos,
        # Enviamos o calendário pronto
        'calendario': calendario_html,
        'mes_atual_nome': hoje.strftime('%B/%Y')
    }
    return render(request, 'core/editar_aluno.html', context)

@login_required
def renovar_matricula(request, id_aluno):
    if request.method == 'POST':
        aluno = get_object_or_404(Aluno, pk=id_aluno)
        matricula = aluno.matricula_set.first()
        
        # 1. Pega os dados que vieram do formulário (Modal)
        novo_plano_id = request.POST.get('plano_id')
        valor_pago = request.POST.get('valor') # Aqui entra o desconto
        
        # Converte o valor para número (substitui vírgula por ponto se necessário)
        valor_final = float(valor_pago.replace(',', '.'))

        if matricula:
            # 2. Atualiza o Plano (se tiver mudado)
            if novo_plano_id:
                novo_plano = get_object_or_404(Plano, pk=novo_plano_id)
                matricula.plano = novo_plano

            # 3. Atualiza a Data (+30 dias)
            hoje = timezone.now().date()
            if not matricula.data_vencimento or matricula.data_vencimento < hoje:
                matricula.data_vencimento = hoje + timedelta(days=30)
            else:
                matricula.data_vencimento = matricula.data_vencimento + timedelta(days=30)
            
            matricula.save()

            # 4. Grava o Pagamento com o Valor (com desconto ou não)
            Pagamento.objects.create(
                aluno=aluno,
                valor=valor_final,
                descricao=f"Renovação: {matricula.plano.nome}"
            )
            
    return redirect('editar_aluno', id=id_aluno)

@login_required
def renovar_matricula(request, id_aluno):
    aluno = get_object_or_404(Aluno, pk=id_aluno)
    matricula = aluno.matricula_set.first()
    
    if matricula:
        # 1. Atualiza a Data de Vencimento (Lógica que já tínhamos)
        hoje = timezone.now().date()
        if not matricula.data_vencimento or matricula.data_vencimento < hoje:
            matricula.data_vencimento = hoje + timedelta(days=30)
        else:
            matricula.data_vencimento = matricula.data_vencimento + timedelta(days=30)
        
        matricula.save()

        # 2. GRAVA O PAGAMENTO NO HISTÓRICO (NOVO)
        # Pegamos o preço atual do plano para registrar
        Pagamento.objects.create(
            aluno=aluno,
            valor=matricula.plano.preco,
            descricao=f"Renovação: {matricula.plano.nome}"
        )
            
    return redirect('editar_aluno', id=aluno.id)

@login_required
def registrar_presenca(request, id_aluno):
    aluno = get_object_or_404(Aluno, pk=id_aluno)
    hoje = timezone.now().date()
    
    # --- CORREÇÃO: Verifica se já existe ---
    if Presenca.objects.filter(aluno=aluno, data_aula=hoje).exists():
        messages.warning(request, f'O aluno {aluno.nome_completo} JÁ treinou hoje!')
    else:
        Presenca.objects.create(aluno=aluno, data_aula=hoje)
        messages.success(request, f'Presença confirmada: {aluno.nome_completo} ✅')
        
    return redirect('home')

@login_required
def excluir_pagamento(request, id_pagamento):
    # 1. Busca o pagamento (ou dá erro 404 se não existir)
    pagamento = get_object_or_404(Pagamento, pk=id_pagamento)
    
    # Guarda quem é o aluno para redirecionar depois
    aluno = pagamento.aluno
    matricula = aluno.matricula_set.first()
    
    # 2. Reverte a Data (Subtrai 30 dias)
    if matricula and matricula.data_vencimento:
        # Tira os 30 dias que foram adicionados por engano
        matricula.data_vencimento = matricula.data_vencimento - timedelta(days=30)
        matricula.save()
        
    # 3. Apaga o registo do dinheiro
    pagamento.delete()
    
    # Volta para a tela do aluno
    return redirect('editar_aluno', id=aluno.id)

@login_required
def alterar_data_vencimento(request, id_aluno):
    if request.method == 'POST':
        aluno = get_object_or_404(Aluno, pk=id_aluno)
        matricula = aluno.matricula_set.first()
        
        nova_data = request.POST.get('nova_data')
        
        if matricula and nova_data:
            matricula.data_vencimento = nova_data
            matricula.save()
            
    return redirect('editar_aluno', id=id_aluno)

@login_required
def trancar_destrancar_matricula(request, id_aluno):
    aluno = get_object_or_404(Aluno, pk=id_aluno)
    matricula = aluno.matricula_set.first()
    
    if matricula:
        # INVERTE O STATUS (Se é True vira False, se é False vira True)
        matricula.trancada = not matricula.trancada
        matricula.save()
        
    return redirect('editar_aluno', id=id_aluno)

@login_required
def relatorio_financeiro(request):
    hoje = timezone.now()
    
    # 1. Filtra pagamentos DESTE MÊS e DESTE ANO
    pagamentos_mes = Pagamento.objects.filter(
        data_pagamento__month=hoje.month,
        data_pagamento__year=hoje.year
    ).order_by('-data_pagamento')
    
    # 2. Soma o valor total
    # O resultado vem como {'valor__sum': 1500.00}
    total_mes = pagamentos_mes.aggregate(Sum('valor'))['valor__sum'] or 0
    
    # 3. Pega os últimos 50 pagamentos para histórico geral
    todos_pagamentos = Pagamento.objects.all().order_by('-data_pagamento')[:50]

    context = {
        'pagamentos_mes': pagamentos_mes,
        'total_mes': total_mes,
        'todos_pagamentos': todos_pagamentos,
        'mes_atual': hoje.strftime('%B/%Y') # Ex: Janeiro/2026
    }
    
    return render(request, 'core/financeiro.html', context)

# --- GESTÃO DE PLANOS ---

@login_required
def lista_planos(request):
    planos = Plano.objects.all()
    return render(request, 'core/lista_planos.html', {'planos': planos})

@login_required
def criar_plano(request):
    if request.method == 'POST':
        form = PlanoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_planos')
    else:
        form = PlanoForm()
    
    return render(request, 'core/form_plano.html', {'form': form, 'titulo': 'Novo Plano'})

@login_required
def editar_plano(request, id):
    plano = get_object_or_404(Plano, pk=id)
    if request.method == 'POST':
        form = PlanoForm(request.POST, instance=plano)
        if form.is_valid():
            form.save()
            return redirect('lista_planos')
    else:
        form = PlanoForm(instance=plano)
        
    return render(request, 'core/form_plano.html', {'form': form, 'titulo': 'Editar Plano'})

@login_required
def excluir_plano(request, id):
    plano = get_object_or_404(Plano, pk=id)
    try:
        plano.delete()
    except:
        # Se o plano estiver em uso por alunos, pode dar erro (proteção do banco)
        pass 
    return redirect('lista_planos')

@login_required
def contratar_plano(request, id_aluno):
    if request.method == 'POST':
        aluno = get_object_or_404(Aluno, pk=id_aluno)
        
        # 1. Pega os dados do formulário
        plano_id = request.POST.get('plano_id')
        valor = request.POST.get('valor')
        
        # Tratamento do valor (troca vírgula por ponto)
        valor_final = float(valor.replace(',', '.'))
        
        plano = get_object_or_404(Plano, pk=plano_id)
        
        # 2. Cria a nova Matrícula
        hoje = timezone.now().date()
        vencimento = hoje + timedelta(days=30)
        
        # Verifica se já existe alguma matrícula antiga e desativa (só por segurança)
        Matricula.objects.filter(aluno=aluno).update(ativo=False)
        
        Matricula.objects.create(
            aluno=aluno,
            plano=plano,
            data_inicio=hoje,
            data_vencimento=vencimento,
            ativo=True,
            trancada=False
        )
        
        # 3. Registra o Pagamento Inicial
        Pagamento.objects.create(
            aluno=aluno,
            valor=valor_final,
            descricao=f"Matrícula Inicial: {plano.nome}"
        )
        
    return redirect('editar_aluno', id=id_aluno)

@login_required
def criar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES)
        if form.is_valid():
            aluno = form.save()
            # Redireciona direto para a página de contratação de plano
            return redirect('editar_aluno', id=aluno.id)
    else:
        form = AlunoForm()
    
    return render(request, 'core/form_aluno.html', {'form': form})

@login_required
def gerar_recibo(request, id_pagamento):
    pagamento = get_object_or_404(Pagamento, pk=id_pagamento)

    # Dados que vão aparecer no PDF
    context = {
        'pagamento': pagamento,
        'aluno': pagamento.aluno,
        'data_geracao': timezone.now()
    }

    return render_to_pdf('core/recibo_pdf.html', context)