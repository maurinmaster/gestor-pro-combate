import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    """
    Converte URLs de HTML em caminhos absolutos do sistema para o xhtml2pdf
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
        sUrl = settings.STATIC_URL        # Tipicamente /static/
        sRoot = settings.STATIC_ROOT      # Tipicamente /home/user/projeto/static/
        mUrl = settings.MEDIA_URL         # Tipicamente /media/
        mRoot = settings.MEDIA_ROOT       # Tipicamente /home/user/projeto/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # Garante que o arquivo existe
    if not os.path.isfile(path):
            raise Exception(f'media URI must start with {sUrl} or {mUrl}')
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    # Se quiser baixar direto, descomente a linha abaixo:
    # response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'
    response['Content-Disposition'] = 'filename="recibo.pdf"'
    
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)

    if pisa_status.err:
       return HttpResponse('Ocorreu um erro ao gerar o PDF: <pre>' + html + '</pre>')
    return response