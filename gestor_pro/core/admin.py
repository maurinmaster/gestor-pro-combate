from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Aluno, Plano, Matricula

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('mostrar_foto', 'nome_completo', 'graduacao', 'telefone')
    search_fields = ('nome_completo', 'cpf')
    list_filter = ('graduacao',)

    def mostrar_foto(self, obj):
        if obj.foto:
            # Aqui também ajustei para usar a sintaxe correta com {}
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />',
                obj.foto.url
            )
        return "-"
    mostrar_foto.short_description = 'Foto'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'plano', 'data_vencimento', 'status_pagamento')
    list_filter = ('ativo', 'plano')
    search_fields = ('aluno__nome_completo',)

    def status_pagamento(self, obj):
        if not obj.data_vencimento:
            return "-"

        hoje = timezone.now().date()
        vencimento = obj.data_vencimento

        # Tratamento seguro para garantir que é data e não datetime
        if hasattr(vencimento, 'date'):
             vencimento = vencimento.date()

        if vencimento < hoje:
            # CORREÇÃO AQUI: Usamos {} e passamos o texto como argumento
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                '⚠️ VENCIDO'
            )
        else:
            # CORREÇÃO AQUI: Usamos {} e passamos o texto como argumento
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                '✅ EM DIA'
            )

    status_pagamento.short_description = 'Situação'

admin.site.register(Plano)