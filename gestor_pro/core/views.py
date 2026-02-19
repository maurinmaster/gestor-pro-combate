
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all().order_by('nome_completo')
    serializer_class = AlunoSerializer
    filterset_fields = ['nome_completo', 'cpf']

class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all().order_by('-data_envio')
    serializer_class = AvisoSerializer
    filterset_fields = ['aluno', 'tipo', 'canal']
