from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Importamos TODAS as funções do views.py
from core.views import (
lista_alunos, 
    editar_aluno, 
    renovar_matricula, 
    contratar_plano,            
    registrar_presenca,
    excluir_pagamento,
    alterar_data_vencimento,
    trancar_destrancar_matricula,
    relatorio_financeiro,
    lista_planos,
    criar_plano,
    editar_plano,
    excluir_plano,
    criar_aluno,
    gerar_recibo,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard (Home)
    path('', lista_alunos, name='home'),
    
    # Gestão de Aluno
    path('editar/<int:id>/', editar_aluno, name='editar_aluno'),
    path('renovar/<int:id_aluno>/', renovar_matricula, name='renovar_matricula'),
    path('alterar_data/<int:id_aluno>/', alterar_data_vencimento, name='alterar_data_vencimento'),
    path('trancar/<int:id_aluno>/', trancar_destrancar_matricula, name='trancar_matricula'),
    
    # Operacional
    path('presenca/<int:id_aluno>/', registrar_presenca, name='registrar_presenca'),
    path('excluir_pagamento/<int:id_pagamento>/', excluir_pagamento, name='excluir_pagamento'),
    
    # Financeiro
    path('financeiro/', relatorio_financeiro, name='relatorio_financeiro'),
    
    # Gestão de Planos
    path('planos/', lista_planos, name='lista_planos'),
    path('plano/criar/', criar_plano, name='criar_plano'),
    path('plano/editar/<int:id>/', editar_plano, name='editar_plano'),
    path('plano/excluir/<int:id>/', excluir_plano, name='excluir_plano'),
    path('contratar_plano/<int:id_aluno>/', contratar_plano, name='contratar_plano'),
    path('aluno/novo/', criar_aluno, name='criar_aluno'),
    path('recibo/<int:id_pagamento>/', gerar_recibo, name='gerar_recibo'),
]

# Configuração de Imagens
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)