from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Importamos TODAS as funções do views.py
from core.views import (
    lista_alunos, 
    editar_aluno, 
    renovar_matricula, 
    registrar_presenca,
    excluir_pagamento,
    alterar_data_vencimento,
    trancar_destrancar_matricula,
    relatorio_financeiro  # <--- Esta era a que faltava!
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
    path('financeiro/', relatorio_financeiro, name='relatorio_financeiro'), # <--- Rota nova
]

# Configuração de Imagens
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)