
from core.models import Aluno, Aviso
from django.utils import timezone

# Dados das mensagens enviadas hoje
mensagens = [
    {
        "nome": "Wendy",
        "tipo": "presenca",
        "msg": "Sawadee kha, Wendy! O Mestre Mauro e eu estamos sentindo sua falta no tatame!..."
    },
    {
        "nome": "Weber Bastos",
        "tipo": "presenca",
        "msg": "Sawadee Krap, Weber! O Mestre Mauro tá de olho na sua frequência... Desse jeito a graduação vai ficar longe..."
    },
    {
        "nome": "Murilo de Almeida",
        "tipo": "presenca",
        "msg": "Sawadee Krap, Murilo! Tatame vazio não forma campeão! Sua presença é fundamental..."
    }
]

print("Registrando avisos...")

for item in mensagens:
    # Busca o aluno pelo nome (flexível)
    aluno = Aluno.objects.filter(nome_completo__icontains=item['nome']).first()
    
    if aluno:
        Aviso.objects.create(
            aluno=aluno,
            tipo=item['tipo'],
            mensagem=item['msg'],
            canal='whatsapp',
            enviado_por='Jarbas'
        )
        print(f"✅ Aviso registrado para: {aluno.nome_completo}")
    else:
        # Wendy não tem cadastro, então não dá pra vincular (mas o script não quebra)
        print(f"⚠️ Aluno não encontrado para vincular aviso: {item['nome']} (Provavelmente a Wendy que ainda não tem cadastro)")

print("Concluído.")
