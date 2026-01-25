# Función para descargar CV en PDF
def descargar_cv_pdf(request):
    import pdfkit
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from .models import (DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS, 
                         RECONOCIMIENTOS, ProductosAcademicos, ProductosLaborales, Ventas)
    import base64
    import os
    
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
    productos_academicos = ProductosAcademicos.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    productos_laborales = ProductosLaborales.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    ventas = Ventas.objects.filter(
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
                    print(f"✓ Foto cargada, tamaño base64: {len(foto_base64)}")
            else:
                print(f"✗ Archivo de foto no encontrado: {foto_path}")
        except Exception as e:
            print(f"✗ Error al cargar foto: {e}")
            foto_base64 = None
    
    # Convertir certificados a base64
    for c in cursos:
        if c.archivo_certificado:
            try:
                cert_path = c.archivo_certificado.path
                if os.path.exists(cert_path):
                    with open(cert_path, 'rb') as f:
                        c.certificado_base64 = base64.b64encode(f.read()).decode()
                        # Detectar tipo
                        extension = cert_path.lower().split('.')[-1]
                        if extension == 'pdf':
                            c.certificado_mime_type = 'application/pdf'
                        elif extension in ['jpg', 'jpeg']:
                            c.certificado_mime_type = 'image/jpeg'
                        elif extension == 'png':
                            c.certificado_mime_type = 'image/png'
                        else:
                            c.certificado_mime_type = 'application/octet-stream'
                        print(f"✓ Certificado cargado: {cert_path}")
            except Exception as e:
                print(f"✗ Error cargando certificado: {e}")
                c.certificado_base64 = None
    
    # Convertir certificados de reconocimientos a base64
    for r in reconocimientos:
        if r.archivo_certificado:
            try:
                cert_path = r.archivo_certificado.path
                if os.path.exists(cert_path):
                    with open(cert_path, 'rb') as f:
                        r.certificado_base64 = base64.b64encode(f.read()).decode()
                        extension = cert_path.lower().split('.')[-1]
                        if extension == 'pdf':
                            r.certificado_mime_type = 'application/pdf'
                        elif extension in ['jpg', 'jpeg']:
                            r.certificado_mime_type = 'image/jpeg'
                        elif extension == 'png':
                            r.certificado_mime_type = 'image/png'
                        else:
                            r.certificado_mime_type = 'application/octet-stream'
            except Exception as e:
                print(f"✗ Error cargando certificado reconocimiento: {e}")
                r.certificado_base64 = None
    
    # Preparar contexto
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
    
    # Renderizar HTML - El template ya tiene los estilos CSS inline
    html_string = render_to_string('hojavida/mi_hoja_vida_pdf.html', context)
    
    # Convertir a PDF usando pdfkit
    try:
        options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None,
        }
        
        pdf = pdfkit.from_string(html_string, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Hoja_de_Vida.pdf"'
        return response
    except Exception as e:
        print(f"✗ Error en pdfkit: {e}")
        return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)
