from django.http import HttpResponse
from django.template.loader import render_to_string
import os
import base64
from weasyprint import HTML, CSS
from .models import DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS, RECONOCIMIENTOS, PRODUCTOSACADEMICOS, PRODUCTOSLABORALES, VENTAS


def descargar_cv_pdf(request):
    # Obtener datos
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
    reconocimientos = RECONOCIMIENTOS.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
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
    
    # Convertir foto a base64
    foto_base64 = None
    foto_mime_type = 'image/jpeg'
    
    if datos and datos.foto:
        try:
            foto_path = datos.foto.path
            
            # Detectar tipo de archivo
            extension = foto_path.lower().split('.')[-1]
            if extension == 'png':
                foto_mime_type = 'image/png'
            elif extension == 'gif':
                foto_mime_type = 'image/gif'
            elif extension in ['jpg', 'jpeg']:
                foto_mime_type = 'image/jpeg'
            
            # Verificar si el archivo existe
            if os.path.exists(foto_path):
                with open(foto_path, 'rb') as f:
                    foto_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"Error al cargar foto: {e}")
            foto_base64 = None
    
    # Convertir certificados a base64
    for c in cursos:
        if c.archivo_certificado:
            try:
                cert_path = c.archivo_certificado.path
                if os.path.exists(cert_path):
                    extension = cert_path.lower().split('.')[-1]
                    
                    if extension == 'pdf':
                        # Convertir PDF a imagen usando PyMuPDF
                        try:
                            import fitz
                            import io
                            
                            # Abrir PDF y convertir primera página a imagen
                            doc = fitz.open(cert_path)
                            if doc.page_count > 0:
                                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom 2x para mejor calidad
                                img_data = pix.tobytes("png")
                                c.certificado_base64 = base64.b64encode(img_data).decode()
                                c.certificado_mime_type = 'image/png'
                                doc.close()
                            else:
                                c.certificado_base64 = None
                        except Exception as e:
                            print(f"Error convirtiendo PDF a imagen con PyMuPDF: {e}")
                            c.certificado_base64 = None
                    else:
                        # Para imágenes directas
                        with open(cert_path, 'rb') as f:
                            c.certificado_base64 = base64.b64encode(f.read()).decode()
                            if extension in ['jpg', 'jpeg']:
                                c.certificado_mime_type = 'image/jpeg'
                            elif extension == 'png':
                                c.certificado_mime_type = 'image/png'
                            else:
                                c.certificado_mime_type = 'application/octet-stream'
                else:
                    c.certificado_base64 = None
            except Exception as e:
                print(f"Error cargando certificado de curso: {e}")
                c.certificado_base64 = None
    
    # Convertir certificados de reconocimientos a base64
    for r in reconocimientos:
        if r.archivo_certificado:
            try:
                cert_path = r.archivo_certificado.path
                if os.path.exists(cert_path):
                    extension = cert_path.lower().split('.')[-1]
                    
                    if extension == 'pdf':
                        # Convertir PDF a imagen usando PyMuPDF
                        try:
                            import fitz
                            import io
                            
                            # Abrir PDF y convertir primera página a imagen
                            doc = fitz.open(cert_path)
                            if doc.page_count > 0:
                                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom 2x para mejor calidad
                                img_data = pix.tobytes("png")
                                r.certificado_base64 = base64.b64encode(img_data).decode()
                                r.certificado_mime_type = 'image/png'
                                doc.close()
                            else:
                                r.certificado_base64 = None
                        except Exception as e:
                            print(f"Error convirtiendo PDF a imagen con PyMuPDF: {e}")
                            r.certificado_base64 = None
                    else:
                        # Para imágenes directas
                        with open(cert_path, 'rb') as f:
                            r.certificado_base64 = base64.b64encode(f.read()).decode()
                            if extension in ['jpg', 'jpeg']:
                                r.certificado_mime_type = 'image/jpeg'
                            elif extension == 'png':
                                r.certificado_mime_type = 'image/png'
                            else:
                                r.certificado_mime_type = 'application/octet-stream'
                else:
                    r.certificado_base64 = None
            except Exception as e:
                print(f"Error cargando certificado de reconocimiento: {e}")
                r.certificado_base64 = None
    
    # Convertir imágenes de ventas a base64
    for v in ventas:
        if v.imagen:
            try:
                img_path = v.imagen.path
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        v.imagen_base64 = base64.b64encode(f.read()).decode()
                else:
                    v.imagen_base64 = None
            except Exception as e:
                print(f"Error cargando imagen de venta: {e}")
                v.imagen_base64 = None
    
    # Preparar contexto
    base_url = request.build_absolute_uri('/')
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
        'base_url': base_url,
    }
    
    # Renderizar HTML
    html_string = render_to_string("hojavida/mi_hoja_vida_pdf.html", context)
    
    # Convertir a PDF usando WeasyPrint
    try:
       html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
       pdf_file = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 0.5in; margin-right: 0.5in; margin-bottom: 0.5in; margin-left: 0.5in; encoding: UTF-8; enable-local-file-access: None}')])

       response = HttpResponse(pdf_file, content_type='application/pdf')
       response['Content-Disposition'] = 'attachment; filename="Hoja_de_Vida.pdf"'
       return response
    except Exception as e:
       print(f"Error generando PDF: {e}")
       return HttpResponse(f"Error generando PDF: {str(e)}", status=500)