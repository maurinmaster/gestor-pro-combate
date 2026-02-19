from django.db import models
from django.utils import timezone
from datetime import timedelta 
from urllib.parse import quote # <--- Serve para transformar espaços em códigos de internet (%20)


class Plano(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Plano")
    preco = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço Mensal")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Aluno(models.Model):
    nome_completo = models.CharField(max_length=150)
    data_nascimento = models.DateField()
    

    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CPF")   
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20)
    graduacao = models.CharField(max_length=50, default="Iniciante", verbose_name="Faixa/Graduação")
    foto = models.ImageField(upload_to='alunos_fotos', blank=True, null=True, verbose_name="Foto do Aluno") 
    data_cadastro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome_completo

    @property
    def get_situacao(self):
        matricula = self.matricula_set.last() # Pega a última (mesmo que inativa)
        
        info = {
            'status': 'sem_matricula', 
            'cor': 'secondary', 
            'texto': 'Sem Matrícula', 
            'plano': '-',
            'link_whatsapp': ''
        }

        if matricula and matricula.ativo:
            info['plano'] = matricula.plano.nome
            
            # --- NOVA LÓGICA DE TRANCAMENTO ---
            if matricula.trancada:
                info['status'] = 'trancado'
                info['cor'] = 'info' # Azul claro
                info['texto'] = 'TRANCADO'
                # Mensagem específica para destrancar
                msg = f"Olá {self.nome_completo}, tudo bem? Quando pretende retornar aos treinos?"
            
            # --- LÓGICA NORMAL (SE NÃO TIVER TRANCADA) ---
            elif matricula.data_vencimento:
                hoje = timezone.now().date()
                info['data_venc'] = matricula.data_vencimento.strftime('%d/%m/%Y')
                
                if matricula.data_vencimento < hoje:
                    info['status'] = 'vencido'
                    info['cor'] = 'danger'
                    info['texto'] = 'VENCIDO'
                    msg = f"Olá {self.nome_completo}, sua mensalidade venceu dia {info['data_venc']}."
                else:
                    info['status'] = 'em_dia'
                    info['cor'] = 'success'
                    info['texto'] = 'EM DIA'
                    msg = f"Olá {self.nome_completo}, bora treinar hoje?"
            else:
                 msg = "Olá..." # Fallback

            # Gera o link do zap (código igual ao anterior)
            phone = ''.join(filter(str.isdigit, self.telefone))
            if len(phone) < 12 and not phone.startswith('55'): phone = f"55{phone}"
            info['link_whatsapp'] = f"https://wa.me/{phone}?text={quote(msg)}"

        return info

    def get_presencas_mes(self):
        hoje = timezone.now()
        # Conta quantas presenças este aluno teve no mês e ano atuais
        return self.presenca_set.filter(
            data_aula__month=hoje.month, 
            data_aula__year=hoje.year
        ).count()

# --- NOVA TABELA ---
class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    data_aula = models.DateField(default=timezone.now)
    
    class Meta:
        # Impede que o mesmo aluno tenha 2 presenças no mesmo dia (evita clique duplo)
        unique_together = ('aluno', 'data_aula')

    def __str__(self):
        return f"{self.aluno.nome_completo} - {self.data_aula}"

class Matricula(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True)
    data_inicio = models.DateField(default=timezone.now)
    trancada = models.BooleanField(default=False)
    
    # Data de Vencimento (pode ficar vazio, pois será preenchido automático)
    data_vencimento = models.DateField(null=True, blank=True)
    
    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Se não houver data de vencimento definida, calcula +30 dias da data de início
        if not self.data_vencimento:
            self.data_vencimento = self.data_inicio + timedelta(days=30)
        
        # Executa o salvamento normal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.aluno.nome_completo} - Vence: {self.data_vencimento}"

class Pagamento(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    # Guardamos o valor fixo, pois o preço do plano pode mudar no futuro
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    data_pagamento = models.DateTimeField(default=timezone.now)
    descricao = models.CharField(max_length=100, blank=True) # Ex: "Mensalidade Maio"

    def __str__(self):
        return f"{self.aluno} - R$ {self.valor}"


# --- NOVOS MODELOS FINANCEIROS ---

class CategoriaGasto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    cor_hex = models.CharField(max_length=7, default="#CCCCCC", help_text="Cor em Hexadecimal (ex: #FF0000)")

    def __str__(self):
        return self.nome

class Gasto(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    data = models.DateField(default=timezone.now, verbose_name="Data do Gasto")
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    pago = models.BooleanField(default=True, verbose_name="Pago?")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

class ContaFixa(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Conta")
    valor_previsto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Previsto (R$)")
    dia_vencimento = models.PositiveIntegerField(verbose_name="Dia de Vencimento (1-31)")
    ativa = models.BooleanField(default=True, verbose_name="Conta Ativa?")
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - Dia {self.dia_vencimento}"

class FaturaMensal(models.Model):
    """
    Representa a fatura de uma ContaFixa em um mês específico.
    Ex: Aluguel (ContaFixa) -> Fatura Janeiro/2026 (FaturaMensal)
    """
    conta_fixa = models.ForeignKey(ContaFixa, on_delete=models.CASCADE, related_name="faturas")
    mes_referencia = models.DateField(verbose_name="Mês de Referência (Dia 1)")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Real")
    pago = models.BooleanField(default=False, verbose_name="Pago?")
    data_pagamento = models.DateField(null=True, blank=True)
    comprovante = models.FileField(upload_to="comprovantes/", null=True, blank=True)

    class Meta:
        unique_together = ('conta_fixa', 'mes_referencia')

    def __str__(self):
        return f"{self.conta_fixa.nome} - {self.mes_referencia.strftime('%m/%Y')}"

class Aviso(models.Model):
    TIPO_CHOICES = [
        ('cobranca', 'Cobrança'),
        ('presenca', 'Falta/Presença'),
        ('aviso_geral', 'Aviso Geral'),
        ('parabens', 'Parabéns/Graduação'),
    ]
    
    CANAL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="avisos")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='cobranca')
    mensagem = models.TextField()
    data_envio = models.DateTimeField(default=timezone.now)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='whatsapp')
    
    enviado_por = models.CharField(max_length=100, default='Jarbas', help_text="Quem enviou (Jarbas ou Sistema)")

    def __str__(self):
        return f"Aviso para {self.aluno.nome_completo} - {self.get_tipo_display()} ({self.data_envio.strftime('%d/%m/%Y')})"
