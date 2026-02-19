
import json
from datetime import datetime
from core.models import Gasto, ContaFixa, CategoriaGasto
from django.utils import timezone

# Dados do JSON (Hardcoded para facilitar a injeção via shell)
dados = {
  "gastos_avulsos": [
    {"data": "2026-02-01", "descricao": "Adilson Alves Da Silva", "valor": 14.00, "categoria": "Outros"},
    {"data": "2026-02-01", "descricao": "Tuna Pagamentos", "valor": 150.79, "categoria": "Outros"},
    {"data": "2026-02-03", "descricao": "Aplicação em CDB", "valor": 78.00, "categoria": "Investimento"},
    {"data": "2026-02-03", "descricao": "Katia De Almeida Lima De Feira De Santana", "valor": 6.24, "categoria": "Outros"},
    {"data": "2026-02-03", "descricao": "Aplicação em CDB", "valor": 50.00, "categoria": "Investimento"},
    {"data": "2026-02-03", "descricao": "Companhia De Eletricidade Do Estado Da Bahia", "valor": 162.82, "categoria": "Contas Fixas"},
    {"data": "2026-02-04", "descricao": "DL*GOOGLE YouTub", "valor": 26.90, "categoria": "Serviços Digitais"},
    {"data": "2026-02-05", "descricao": "Aplicação em CDB", "valor": 150.00, "categoria": "Investimento"},
    {"data": "2026-02-06", "descricao": "Maridalva Lima Dos Santos", "valor": 22.00, "categoria": "Outros"},
    {"data": "2026-02-06", "descricao": "Mauro De Oliveira", "valor": 850.00, "categoria": "Transferência"},
    {"data": "2026-02-06", "descricao": "Delicatessen Panipao Ltda", "valor": 13.00, "categoria": "Alimentação"},
    {"data": "2026-02-07", "descricao": "Lauri Germano Ongaratto", "valor": 28.00, "categoria": "Outros"},
    {"data": "2026-02-09", "descricao": "Maria Clarete De Oliveira", "valor": 1200.00, "categoria": "Transferência"},
    {"data": "2026-02-09", "descricao": "Mauro De Oliveira", "valor": 500.00, "categoria": "Transferência"},
    {"data": "2026-02-09", "descricao": "Delicatessen Panipao Ltda", "valor": 6.00, "categoria": "Alimentação"},
    {"data": "2026-02-10", "descricao": "Delicatessen Panipao Ltda", "valor": 16.00, "categoria": "Alimentação"},
    {"data": "2026-02-10", "descricao": "Hinova Payments", "valor": 182.00, "categoria": "Outros"},
    {"data": "2026-02-10", "descricao": "Eduardo De Oliveira", "valor": 1000.00, "categoria": "Transferência"},
    {"data": "2026-02-10", "descricao": "Aplicação em CDB", "valor": 78.00, "categoria": "Investimento"},
    {"data": "2026-02-11", "descricao": "Mauro De Oliveira", "valor": 850.00, "categoria": "Transferência"},
    {"data": "2026-02-11", "descricao": "Fsl Supermercado Ltda", "valor": 33.95, "categoria": "Mercado"},
    {"data": "2026-02-12", "descricao": "DL*GOOGLE YouTub", "valor": 2.00, "categoria": "Serviços Digitais"},
    {"data": "2026-02-12", "descricao": "Barbara Jeane De Souza Soares", "valor": 6.00, "categoria": "Outros"},
    {"data": "2026-02-12", "descricao": "Delicatessen Panipao Ltda", "valor": 6.00, "categoria": "Alimentação"},
    {"data": "2026-02-13", "descricao": "Claro Flex", "valor": 39.99, "categoria": "Contas Fixas"},
    {"data": "2026-02-13", "descricao": "Maria Clarete De Oliveira", "valor": 850.00, "categoria": "Transferência"},
    {"data": "2026-02-13", "descricao": "Fsl Supermercado Ltda", "valor": 35.94, "categoria": "Mercado"},
    {"data": "2026-02-14", "descricao": "Alfa Comércio De Alimentos Ltda", "valor": 175.45, "categoria": "Mercado"},
    {"data": "2026-02-15", "descricao": "Santa Maria - Comercial De Combustiveis", "valor": 20.00, "categoria": "Transporte"},
    {"data": "2026-02-16", "descricao": "Manoel Lopes De Oliveira", "valor": 120.00, "categoria": "Transferência"},
    {"data": "2026-02-16", "descricao": "Salem Delicatessen", "valor": 50.61, "categoria": "Alimentação"},
    {"data": "2026-02-17", "descricao": "Barbara Jeane De Souza Soares", "valor": 31.00, "categoria": "Outros"}
  ],
  "contas_fixas": [
    {"nome": "Aluguel", "valor": 1500, "dia_vencimento": 20},
    {"nome": "Cartão Mercado Pago", "valor": 412.24, "dia_vencimento": 20},
    {"nome": "Água (Embasa)", "valor": 225.00, "dia_vencimento": 11}
  ]
}

print("Iniciando importação...")

# 1. Importar Contas Fixas
for conta in dados['contas_fixas']:
    obj, created = ContaFixa.objects.get_or_create(
        nome=conta['nome'],
        defaults={
            'valor_previsto': conta['valor'],
            'dia_vencimento': conta['dia_vencimento'],
            'ativa': True
        }
    )
    if created:
        print(f"Conta Fixa Criada: {conta['nome']}")
    else:
        print(f"Conta Fixa já existia: {conta['nome']}")

# 2. Importar Gastos Avulsos
count_gastos = 0
for gasto in dados['gastos_avulsos']:
    # Cria a categoria se não existir
    cat_obj, _ = CategoriaGasto.objects.get_or_create(nome=gasto['categoria'])
    
    # Converte data string para objeto date
    data_obj = datetime.strptime(gasto['data'], "%Y-%m-%d").date()
    
    # Evita duplicidade checando se já existe gasto igual no mesmo dia
    if not Gasto.objects.filter(descricao=gasto['descricao'], data=data_obj, valor=gasto['valor']).exists():
        Gasto.objects.create(
            descricao=gasto['descricao'],
            valor=gasto['valor'],
            data=data_obj,
            categoria=cat_obj,
            pago=True
        )
        count_gastos += 1

print(f"Sucesso! {count_gastos} novos gastos importados.")
