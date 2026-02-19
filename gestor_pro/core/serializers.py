from rest_framework import serializers
from .models import Gasto, ContaFixa, FaturaMensal, CategoriaGasto, Aluno, Aviso, Matricula

class CategoriaGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaGasto
        fields = '__all__'

class GastoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.ReadOnlyField(source='categoria.nome')

    class Meta:
        model = Gasto
        fields = '__all__'
        extra_kwargs = {'categoria': {'required': False}}

class ContaFixaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaFixa
        fields = '__all__'

class FaturaMensalSerializer(serializers.ModelSerializer):
    conta_nome = serializers.ReadOnlyField(source='conta_fixa.nome')

    class Meta:
        model = FaturaMensal
        fields = '__all__'

# --- NOVOS SERIALIZERS (ALUNOS E AVISOS) ---

class MatriculaSerializer(serializers.ModelSerializer):
    plano_nome = serializers.ReadOnlyField(source='plano.nome')
    status_formatado = serializers.ReadOnlyField(source='aluno.get_situacao')

    class Meta:
        model = Matricula
        fields = ['id', 'plano', 'plano_nome', 'data_vencimento', 'ativo', 'trancada', 'status_formatado']

class AlunoSerializer(serializers.ModelSerializer):
    matricula = serializers.SerializerMethodField()
    
    class Meta:
        model = Aluno
        fields = ['id', 'nome_completo', 'telefone', 'cpf', 'graduacao', 'foto', 'matricula']

    def get_matricula(self, obj):
        # Pega a matrícula ativa (ou a última)
        mat = obj.matricula_set.last()
        if mat:
            return MatriculaSerializer(mat).data
        return None

class AvisoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.ReadOnlyField(source='aluno.nome_completo')

    class Meta:
        model = Aviso
        fields = '__all__'
