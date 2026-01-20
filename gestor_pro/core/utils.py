import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    """
    Converte URLs (como /static/img.png) em caminhos absolutos do disco.
    Versão corrigida para evitar erros de 'SuspiciousFileOperation' no Windows.
    """
    sUrl = settings.STATIC_URL        # /static/
    mUrl = settings.MEDIA_URL         # /media/
    mRoot = settings.MEDIA_ROOT       # .../media
    sRoot = settings.STATIC_ROOT      # .../static_root

    # 1. Se for arquivo de MEDIA (Uploads)
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    
    # 2. Se for arquivo STATIC (CSS, Logo, Favicon)
    elif uri.startswith(sUrl):
        # Remove o '/static/' do início
        spath = uri.replace(sUrl, "")
        
        # [IMPORTANTE] Remove barras iniciais para evitar ir para C:\
        spath = spath.lstrip('/').lstrip('\\')

        # Tenta encontrar usando o sistema do Django (finders)
        # Isso funciona bem no Windows/Desenvolvimento
        path = finders.find(spath)
        
        # Se o finders não achar (ou estivermos em Produção sem finders)
        if not path:
            if not sRoot:
                # Se STATIC_ROOT não estiver definido, usa a pasta static local
                sRoot = os.path.join(settings.BASE_DIR, 'core', 'static')
            
            path = os.path.join(sRoot, spath)

    else:
        # Se for caminho absoluto local ou outra coisa, mantém
        path = uri

    # Segurança final: garante que o caminho não é None e o arquivo existe
    if not path or not os.path.isfile(path):
        # Retorna None para que o PDF seja gerado SEM a imagem (em vez de dar erro)
        return None 

    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="recibo.pdf"' # Para baixar direto
    response['Content-Disposition'] = 'filename="recibo.pdf"' # Para abrir no navegador
    
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)

    if pisa_status.err:
       return HttpResponse('Erro ao gerar PDF: <pre>' + html + '</pre>')
    return response