import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    """
    Converte URLs de HTML em caminhos absolutos do sistema para o xhtml2pdf.
    Compatível com Windows, Linux (PythonAnywhere) e StaticFiles.
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Geralmente /static/
        sRoot = settings.STATIC_ROOT      # Caminho físico da pasta static
        mUrl = settings.MEDIA_URL         # Geralmente /media/
        mRoot = settings.MEDIA_ROOT       # Caminho físico da pasta media

        # Se for um arquivo de MEDIA (Uploads)
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        
        # Se for um arquivo STATIC (CSS, Imagens do sistema)
        elif uri.startswith(sUrl):
            # Remove o /static/ do início da URL
            path_relativo = uri.replace(sUrl, "")
            
            # Tenta encontrar primeiro via finders (Desenvolvimento/Windows)
            path = finders.find(path_relativo)
            
            # Se não encontrar (ou se estiver em Produção e o finders falhar)
            if not path:
                # Garante que sRoot existe (evita erro se STATIC_ROOT não estiver configurado)
                if not sRoot:
                    sRoot = os.path.join(settings.BASE_DIR, 'static')
                
                path = os.path.join(sRoot, path_relativo)

        else:
            return uri

    # Verificação final de segurança
    if not path or not os.path.isfile(path):
        # Se não achou a imagem, retorna None para não quebrar o PDF (apenas a imagem falha)
        return None 
        
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    # Para forçar download, descomente a linha abaixo:
    # response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'
    response['Content-Disposition'] = 'filename="recibo.pdf"'
    
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)

    if pisa_status.err:
       return HttpResponse('Ocorreu um erro ao gerar o PDF: <pre>' + html + '</pre>')
    return response