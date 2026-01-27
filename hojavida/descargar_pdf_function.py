from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from cloudinary.utils import cloudinary_url
from .models import (
    DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS, RECONOCIMIENTOS, 
    PRODUCTOSACADEMICOS, PRODUCTOSLABORALES, VENTAS
)

def descargar_cv_pdf(request):
    # Obtener datos del perfil activo
    datos = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    if not datos:
        return HttpResponse("No hay datos para descargar", status=400)

    experiencias = EXPERIENCIALABORAL.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    cursos = CURSOSREALIZADOS.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    for c in cursos:
        c.certificado_img_url = None
        if c.archivo_certificado:
            url, _ = cloudinary_url(
                c.archivo_certificado.public_id,
                format='jpg',
                transformation=[{'page': 1}]
            )
            c.certificado_img_url = url

    reconocimientos = RECONOCIMIENTOS.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    for r in reconocimientos:
        r.certificado_img_url = None
        if r.archivo_certificado:
            url, _ = cloudinary_url(
                r.archivo_certificado.public_id,
                format='jpg',
                transformation=[{'page': 1}]
            )
            r.certificado_img_url = url

    productos_academicos = PRODUCTOSACADEMICOS.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    productos_laborales = PRODUCTOSLABORALES.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    ventas = VENTAS.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )

    # Contexto para renderizar el HTML
    context = {
        'datos': datos,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas': ventas,
        'es_pdf': True,
    }

    # Renderizar HTML
    html_string = render_to_string('hojavida/mi_hoja_vida_pdf.html', context)

    try:
        # Generar PDF con WeasyPrint
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Hoja_de_Vida.pdf"'
        return response

    except Exception as e:
        print(f"✗ Error generando PDF con WeasyPrint: {e}")
        return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
