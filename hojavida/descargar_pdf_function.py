import os
import base64
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from .models import (
    DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS,
    RECONOCIMIENTOS, PRODUCTOSACADEMICOS, PRODUCTOSLABORALES, VENTAS
)

def descargar_cv_pdf(request):
    # 1. Obtener datos del perfil activo
    datos = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    if not datos:
        return HttpResponse("No hay datos para descargar", status=400)

    # Filtro común para todas las consultas
    filtros = {
        'idperfilconqueestaactivo': datos.idperfil,
        'activarparaqueseveaenfront': 1
    }

    experiencias = EXPERIENCIALABORAL.objects.filter(**filtros)
    cursos = CURSOSREALIZADOS.objects.filter(**filtros)
    reconocimientos = RECONOCIMIENTOS.objects.filter(**filtros)
    
    # CORRECCIÓN DE NOMBRES (Ahora coinciden con el import)
    productos_academicos = PRODUCTOSACADEMICOS.objects.filter(**filtros)
    productos_laborales = PRODUCTOSLABORALES.objects.filter(**filtros)
    ventas = VENTAS.objects.filter(**filtros)

    # 2. Procesar Foto de Perfil (Base64)
    foto_base64 = None
    foto_mime_type = 'image/jpeg'
    
    if datos.foto_perfil:
        try:
            # Intentamos abrir el archivo directamente. 
            # Esto es mejor que usar os.path.exists(datos.foto_perfil.path) en servidores efímeros
            with datos.foto_perfil.open('rb') as f:
                foto_base64 = base64.b64encode(f.read()).decode()
                ext = datos.foto_perfil.name.lower().split('.')[-1]
                if ext == 'png': foto_mime_type = 'image/png'
                elif ext == 'gif': foto_mime_type = 'image/gif'
        except Exception as e:
            print(f"Aviso: No se pudo cargar la foto del perfil: {e}")

    # 3. Convertir certificados de cursos a base64
    for c in cursos:
        c.certificado_base64 = None
        if c.archivo_certificado:
            try:
                with c.archivo_certificado.open('rb') as f:
                    c.certificado_base64 = base64.b64encode(f.read()).decode()
                    ext = c.archivo_certificado.name.lower().split('.')[-1]
                    c.certificado_mime_type = 'application/pdf' if ext == 'pdf' else f'image/{ext}'
            except: pass

    # 4. Convertir certificados de reconocimientos
    for r in reconocimientos:
        r.certificado_base64 = None
        if r.archivo_certificado:
            try:
                with r.archivo_certificado.open('rb') as f:
                    r.certificado_base64 = base64.b64encode(f.read()).decode()
                    ext = r.archivo_certificado.name.lower().split('.')[-1]
                    r.certificado_mime_type = 'application/pdf' if ext == 'pdf' else f'image/{ext}'
            except: pass

    # 5. Convertir imágenes de ventas
    for v in ventas:
        v.imagen_base64 = None
        if v.imagen:
            try:
                with v.imagen.open('rb') as f:
                    v.imagen_base64 = base64.b64encode(f.read()).decode()
            except: pass

    context = {
        'datos': datos,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas': ventas,
        'es_pdf': True,
        'foto_base64': foto_base64,
        'foto_mime_type': foto_mime_type,
    }

    # 6. Generar PDF
    html_string = render_to_string('hojavida/mi_hoja_vida_pdf.html', context)

    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CV_{datos.apellidos}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error crítico al generar PDF: {str(e)}", status=500)