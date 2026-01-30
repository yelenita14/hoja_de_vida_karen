import os
import base64
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from datetime import datetime
from django.contrib import messages
from .models import DatosPersonales, ExperienciaLaboral, CursosRealizados, Reconocimientos, ProductosAcademicos, ProductosLaborales, VentaGarage

# Vista para mostrar la hoja de vida sin iniciar sesión
def mi_hoja_vida(request):
    # Intentamos traer el perfil marcado como activo
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    # Si no hay uno activo, traemos el último registro creado para que NO salga vacío
    if not datos:
        datos = DatosPersonales.objects.order_by('-idperfil').first()
    
    # Si la base de datos está totalmente vacía, mostramos un mensaje amigable
    if not datos:
        return render(request, 'hojavida/mi_hoja_vida.html', {
            'mensaje_error': 'Todavía no se han cargado datos en el sistema.'
        })

    # Traemos la información relacionada usando el objeto 'datos' directamente
    # Quitamos el filtro de 'activarparaqueseveaenfront' temporalmente para asegurar que veas algo
    experiencias = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=datos)
    cursos = CursosRealizados.objects.filter(idperfilconqueestaactivo=datos)
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=datos)
    productos_academicos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=datos)
    productos_laborales = ProductosLaborales.objects.filter(idperfilconqueestaactivo=datos)
    ventas = VentaGarage.objects.filter(idperfilconqueestaactivo=datos)

    return render(request, 'hojavida/mi_hoja_vida.html', {
        'datos': datos,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas': ventas
    })

# Vista para login
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get('next')
            return redirect(next_url or 'panel_admin')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'hojavida/login.html')


# Vista para logout
def logout_view(request):
    logout(request)
    return redirect('mi_hoja_vida')

# Vista para el panel de administración, solo accesible para el admin
@login_required
def panel_admin(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    experiencias = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idexperiencialaboral') if perfil else []
    cursos = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idcursorealizado') if perfil else []
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idreconocimiento') if perfil else []
    productos_academicos = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idproductoacademico') if perfil else []
    productos_laborales = ProductosLaborales.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idproductoslaborales') if perfil else []
    ventas = VentaGarage.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idventagarage') if perfil else []
    
    return render(request, 'hojavida/panel_admin.html', {
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas': ventas
    })

# Vistas para Agregar
@login_required
def agregar_datos(request):
    if request.method == 'POST':
        fechanacimiento_str = request.POST.get('fechanacimiento')
        cedula = request.POST.get('numerocedula', '')
        error = None

        # 1. Validación de fecha
        if fechanacimiento_str:
            try:
                fechanacimiento = datetime.strptime(fechanacimiento_str, '%Y-%m-%d').date()
                if fechanacimiento > timezone.now().date():
                    error = 'La fecha de nacimiento no puede ser en el futuro.'
            except ValueError:
                error = 'Formato de fecha inválido.'

        if error:
            return render(request, 'hojavida/agregar_datos.html', {'error': error})

        # 2. Intento de guardado con manejo de duplicados
        try:
            nuevo_perfil = DatosPersonales(
                nombres=request.POST.get('nombres', ''),
                apellidos=request.POST.get('apellidos', ''),
                nacionalidad=request.POST.get('nacionalidad', ''),
                lugarnacimiento=request.POST.get('lugarnacimiento', ''),
                fechanacimiento=fechanacimiento_str or None,
                numerocedula=cedula,
                sexo=request.POST.get('sexo', 'H'),
                estadocivil=request.POST.get('estadocivil', ''),
                licenciaconducir=request.POST.get('licenciaconducir', ''),
                telefonofijo=request.POST.get('telefonofijo', ''),
                direcciondomiciliaria=request.POST.get('direcciondomiciliaria', ''),
                mostrar_experiencia=1 if request.POST.get('mostrar_experiencia') else 0,
                mostrar_cursos=1 if request.POST.get('mostrar_cursos') else 0,
                mostrar_reconocimientos=1 if request.POST.get('mostrar_Reconocimientos') else 0,
                mostrar_productos_academicos=1 if request.POST.get('mostrar_productos_academicos') else 0,
                mostrar_productos_laborales=1 if request.POST.get('mostrar_productos_laborales') else 0,
                mostrar_venta_garage=1 if request.POST.get('mostrar_VentaGarage') else 0,
                perfilactivo=1
            )

            if 'foto' in request.FILES:
                nuevo_perfil.foto_perfil = request.FILES['foto'] # OJO: Verifica si es .foto o .foto_perfil según tu models.py

            nuevo_perfil.save()
            messages.success(request, "Datos personales guardados con éxito.")
            return redirect('panel_admin')

        except IntegrityError:
            # AQUÍ SE CORRIGE EL ERROR DE LA IMAGEN
            error = f"El número de cédula '{cedula}' ya está registrado. Si desea actualizar sus datos, utilice la opción de editar."
            return render(request, 'hojavida/agregar_datos.html', {
                'error': error,
                'datos_previos': request.POST # Para que el usuario no pierda lo que escribió
            })

    return render(request, 'hojavida/agregar_datos.html')

@login_required
def agregar_experiencia(request):
    if request.method == 'POST':
        ExperienciaLaboral.objects.create(
            perfil_id=request.POST.get('perfil_id'),
            nombrempresa=request.POST.get('nombrempresa'),
            cargodesempenado=request.POST.get('cargodesempenado'),
            descripcionfunciones=request.POST.get('descripcionfunciones'),
            fechainicio=request.POST.get('fechainicio'),
            fechafin=request.POST.get('fechafin'),
        )
        return redirect('panel_admin')

    return render(request, 'hojavida/agregar_experiencia.html')

@login_required
def agregar_curso(request):
    if request.method == 'POST':
        perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
        if perfil:
            curso = CursosRealizados(
                idperfilconqueestaactivo=perfil,
                nombrecurso=request.POST.get('nombrecurso', ''),
                entidadpatrocinadora=request.POST.get('entidadpatrocinadora', ''),
                fechainicio=request.POST.get('fechainicio') or None,
                fechafin=request.POST.get('fechafin') or None,
                descripcioncurso=request.POST.get('descripcion', ''),
                activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
            )
            if 'archivo_certificado' in request.FILES:
                curso.rutacertificado = request.FILES['archivo_certificado']
            curso.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_curso.html')

@login_required
def agregar_producto_academico(request):
    if request.method == 'POST':
        perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
        if perfil:
            producto = ProductosAcademicos(
                idperfilconqueestaactivo=perfil,
                nombrerecurso=request.POST.get('nombreproducto', ''),
                clasificador=request.POST.get('tiposproducto', ''),
                fecha_registro=request.POST.get('fechapublicacion') or None,
                descripcion=request.POST.get('descripcion', ''),
                link=request.POST.get('enlace', ''),
                activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
            )
            if 'archivo' in request.FILES:
                producto.archivo = request.FILES['archivo']
            producto.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_producto_academico.html')

@login_required
def agregar_reconocimiento(request):
    if request.method == 'POST':
        perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
        if perfil:
            reconocimiento = Reconocimientos(
                idperfilconqueestaactivo=perfil,
                tiporeconocimiento=request.POST.get('tiporeconocimiento', ''),
                entidadpatrocinadora=request.POST.get('entidadpatrocinadora', ''),
                fechareconocimiento=request.POST.get('fechareconocimiento') or None,
                descripcionreconocimiento=request.POST.get('descripcionreconocimiento', ''),
                nombrecontactoauspicia=request.POST.get('nombrecontactoauspicia', ''),
                telefonocontactoauspicia=request.POST.get('telefonocontactoauspicia', ''),
                activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
            )
            if 'archivo_certificado' in request.FILES:
                reconocimiento.rutacertificado = request.FILES['archivo_certificado']
            reconocimiento.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_reconocimiento.html')

# Vistas para Editar
@login_required
def editar_datos(request):
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()

    if request.method == 'POST':
        from django.utils import timezone
        from datetime import datetime

        fechanacimiento_str = request.POST.get('fechanacimiento')
        error = None

        if fechanacimiento_str:
            fechanacimiento = datetime.strptime(fechanacimiento_str, '%Y-%m-%d').date()
            if fechanacimiento > timezone.now().date():
                error = 'La fecha de nacimiento no puede ser en el futuro.'

        if error:
            return render(request, 'hojavida/editar_datos.html', {'datos': datos, 'error': error})

        if datos:
            datos.nombres = request.POST.get('nombres', datos.nombres)
            datos.apellidos = request.POST.get('apellidos', datos.apellidos)
            datos.nacionalidad = request.POST.get('nacionalidad', datos.nacionalidad)
            datos.lugarnacimiento = request.POST.get('lugarnacimiento', datos.lugarnacimiento)

            if fechanacimiento_str and not datos.fechanacimiento:
                datos.fechanacimiento = fechanacimiento_str

            datos.numerocedula = request.POST.get('numerocedula', datos.numerocedula)
            datos.sexo = request.POST.get('sexo', datos.sexo)
            datos.estadocivil = request.POST.get('estadocivil', datos.estadocivil)
            datos.licenciaconducir = request.POST.get('licenciaconducir', datos.licenciaconducir)
            datos.telefonofijo = request.POST.get('telefonofijo', datos.telefonofijo)
            datos.direcciondomiciliaria = request.POST.get('direcciondomiciliaria', datos.direcciondomiciliaria)

            if 'foto' in request.FILES:
                datos.foto = request.FILES['foto']

            datos.save()

        return redirect('panel_admin')

    return render(request, 'hojavida/editar_datos.html', {'datos': datos})

@login_required
def editar_experiencia(request, experiencia_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    experiencia = ExperienciaLaboral.objects.filter(idexperiencialaboral=experiencia_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not experiencia:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        from django.utils import timezone
        from datetime import datetime
        
        # Validar fechas
        fechainicio_str = request.POST.get('fechainicio')
        fechafin_str = request.POST.get('fechafin')
        error = None
        
        if fechainicio_str:
            fechainicio = datetime.strptime(fechainicio_str, '%Y-%m-%d').date()
            if fechainicio > timezone.now().date():
                error = 'La fecha de inicio no puede ser en el futuro.'
        
        if fechafin_str and not error:
            fechafin = datetime.strptime(fechafin_str, '%Y-%m-%d').date()
            if fechafin > timezone.now().date():
                error = 'La fecha de fin no puede ser en el futuro.'
            if fechainicio_str:
                fechainicio = datetime.strptime(fechainicio_str, '%Y-%m-%d').date()
                if fechainicio > fechafin:
                    error = 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'
        
        if error:
            return render(request, 'hojavida/editar_experiencia_laboral.html', {'experiencia': experiencia, 'error': error})
        
        experiencia.nombrempresa = request.POST.get('empresa', experiencia.nombrempresa)
        experiencia.cargodesempenado = request.POST.get('cargo', experiencia.cargodesempenado)
        experiencia.fechainiciogestion = fechainicio_str or experiencia.fechainiciogestion
        experiencia.fechafingestion = fechafin_str or experiencia.fechafingestion
        experiencia.descripcionfunciones = request.POST.get('descripcion', experiencia.descripcionfunciones)
        experiencia.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        experiencia.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_experiencia_laboral.html', {'experiencia': experiencia})

@login_required
def editar_curso(request, curso_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    curso = CursosRealizados.objects.filter(idcursorealizado=curso_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not curso:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        curso.nombrecurso = request.POST.get('nombrecurso', curso.nombrecurso)
        curso.entidadpatrocinadora = request.POST.get('entidadpatrocinadora', curso.entidadpatrocinadora)
        curso.fechainicio = request.POST.get('fechainicio') or curso.fechainicio
        curso.fechafin = request.POST.get('fechafin') or curso.fechafin
        curso.descripcioncurso = request.POST.get('descripcion', curso.descripcioncurso)
        if 'archivo_certificado' in request.FILES:
            curso.rutacertificado = request.FILES['archivo_certificado']
        curso.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        curso.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_curso.html', {'curso': curso})

@login_required
def editar_producto_academico(request, producto_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    producto = ProductosAcademicos.objects.filter(idproductoacademico=producto_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not producto:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        producto.nombrerecurso = request.POST.get('nombreproducto', producto.nombrerecurso)
        producto.clasificador = request.POST.get('tiposproducto', producto.clasificador)
        producto.fecha_registro = request.POST.get('fechapublicacion') or producto.fecha_registro
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.link = request.POST.get('enlace', producto.link)
        if 'archivo' in request.FILES:
            producto.archivo = request.FILES['archivo']
        producto.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        producto.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_producto_academico.html', {'producto': producto})

@login_required
def editar_reconocimiento(request, reconocimiento_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    reconocimiento = Reconocimientos.objects.filter(idreconocimiento=reconocimiento_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not reconocimiento:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        reconocimiento.tiporeconocimiento = request.POST.get('tiporeconocimiento', reconocimiento.tiporeconocimiento)
        reconocimiento.entidadpatrocinadora = request.POST.get('entidadpatrocinadora', reconocimiento.entidadpatrocinadora)
        reconocimiento.fechareconocimiento = request.POST.get('fechareconocimiento') or reconocimiento.fechareconocimiento
        reconocimiento.descripcionreconocimiento = request.POST.get('descripcionreconocimiento', reconocimiento.descripcionreconocimiento)
        reconocimiento.nombrecontactoauspicia = request.POST.get('nombrecontactoauspicia', reconocimiento.nombrecontactoauspicia)
        reconocimiento.telefonocontactoauspicia = request.POST.get('telefonocontactoauspicia', reconocimiento.telefonocontactoauspicia)
        if 'archivo_certificado' in request.FILES:
            reconocimiento.rutacertificado = request.FILES['archivo_certificado']
        reconocimiento.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        reconocimiento.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_reconocimiento.html', {'reconocimiento': reconocimiento})

@login_required
def agregar_producto_laboral(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        ProductosLaborales.objects.create(
            idperfilconqueestaactivo=perfil,
            nombreproducto=request.POST.get('nombreproducto'),
            descripcion=request.POST.get('descripcion', ''),
            link=request.POST.get('enlace', ''),
            archivo=request.FILES.get('archivo'),
            fechaproducto=request.POST.get('fechaproducto') or None,
            activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
        )
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_producto_laboral.html')

@login_required
def agregar_venta(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        venta = VentaGarage(
            idperfilconqueestaactivo=perfil,
            nombreproducto=request.POST.get('nombreproducto'),
            descripcion=request.POST.get('descripcion', ''),
            valordelbien=request.POST.get('valordelbien') or None,
            estadoproducto=request.POST.get('estadoproducto', ''),
            # fecha_publicacion se gestiona automáticamente en el modelo
            activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
        )
        if 'imagen' in request.FILES:
            venta.imagen_producto = request.FILES['imagen']
        venta.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_venta.html')

@login_required
def editar_producto_laboral(request, producto_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    producto = ProductosLaborales.objects.filter(idproductoslaborales=producto_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not producto:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.link = request.POST.get('enlace', producto.link)
        if 'archivo' in request.FILES:
            producto.archivo = request.FILES['archivo']
        producto.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        producto.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_producto_laboral.html', {'producto': producto})

@login_required
def editar_venta(request, venta_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    venta = VentaGarage.objects.filter(idventagarage=venta_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not venta:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        venta.nombreproducto = request.POST.get('nombreproducto', venta.nombreproducto)
        venta.descripcion = request.POST.get('descripcion', venta.descripcion)
        venta.valordelbien = request.POST.get('valordelbien') or venta.valordelbien
        venta.estadoproducto = request.POST.get('estadoproducto', venta.estadoproducto)
        # fecha_publicacion es automática; actualizar imagen si está presente
        if 'imagen' in request.FILES:
            venta.imagen_producto = request.FILES['imagen']
        venta.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        venta.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_venta.html', {'venta': venta})

# Vista para descargar el PDF de la hoja de vida 
def descargar_cv_pdf(request):
    # Obtener datos
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not datos:
        return HttpResponse("No hay datos para descargar", status=400)
    
    experiencias = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    cursos = CursosRealizados.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    Reconocimientos = Reconocimientos.objects.filter(
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
    VentaGarage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=datos.idperfil,
        activarparaqueseveaenfront=1
    )
    # Importar librerías pesadas de forma perezosa
    try:
        import pymupdf as fitz
    except Exception:
        fitz = None
    try:
        from weasyprint import HTML, CSS
    except Exception:
        HTML = None
        CSS = None
    
    # Convertir foto a base64
    foto_base64 = None
    foto_mime_type = 'image/jpeg'
    
    if datos and datos.foto:
        try:
            # Manejar tanto archivos locales como URLs de Cloudinary
            if hasattr(datos.foto, 'path'):
                # Archivo local
                foto_path = datos.foto.path
                extension = foto_path.lower().split('.')[-1]
                if extension == 'png':
                    foto_mime_type = 'image/png'
                elif extension == 'gif':
                    foto_mime_type = 'image/gif'
                elif extension in ['jpg', 'jpeg']:
                    foto_mime_type = 'image/jpeg'
                
                if os.path.exists(foto_path):
                    with open(foto_path, 'rb') as f:
                        foto_base64 = base64.b64encode(f.read()).decode()
            else:
                # URL de Cloudinary o similar
                import urllib.request
                foto_url = datos.foto.url
                try:
                    with urllib.request.urlopen(foto_url) as response:
                        foto_data = response.read()
                        foto_base64 = base64.b64encode(foto_data).decode()
                        # Detectar tipo MIME
                        content_type = response.headers.get('Content-Type', 'image/jpeg')
                        if 'png' in content_type:
                            foto_mime_type = 'image/png'
                        elif 'gif' in content_type:
                            foto_mime_type = 'image/gif'
                except Exception as url_error:
                    print(f"Error al descargar foto de URL: {url_error}")
                    foto_base64 = None
        except Exception as e:
            print(f"Error al cargar foto: {e}")
            foto_base64 = None
    
    # Convertir certificados a base64
    for c in cursos:
        if c.archivo_certificado:
            try:
                # Manejar tanto archivos locales como URLs de Cloudinary
                if hasattr(c.archivo_certificado, 'path'):
                    cert_path = c.archivo_certificado.path
                    if os.path.exists(cert_path):
                        extension = cert_path.lower().split('.')[-1]
                        
                        if extension == 'pdf':
                            # Convertir PDF a imagen usando PyMuPDF
                            try:
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
                else:
                    # URL de Cloudinary
                    import urllib.request
                    cert_url = c.archivo_certificado.url
                    try:
                        # Descargar archivo de Cloudinary
                        with urllib.request.urlopen(cert_url) as response:
                            cert_data = response.read()
                            content_type = response.headers.get('Content-Type', 'application/octet-stream')
                            
                            # Detectar extensión desde URL o Content-Type
                            if 'pdf' in content_type or cert_url.lower().endswith('.pdf'):
                                # Para PDFs, intentar convertir a imagen con PyMuPDF
                                try:
                                    import io
                                    doc = fitz.open(stream=io.BytesIO(cert_data), filetype='pdf')
                                    if doc.page_count > 0:
                                        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                                        img_data = pix.tobytes("png")
                                        c.certificado_base64 = base64.b64encode(img_data).decode()
                                        c.certificado_mime_type = 'image/png'
                                        doc.close()
                                    else:
                                        c.certificado_base64 = None
                                except Exception as e:
                                    print(f"Error convirtiendo PDF a imagen: {e}")
                                    c.certificado_base64 = None
                            else:
                                # Para imágenes
                                c.certificado_base64 = base64.b64encode(cert_data).decode()
                                c.certificado_mime_type = content_type
                    except Exception as url_error:
                        print(f"Error descargando certificado de URL: {url_error}")
                        c.certificado_base64 = None
            except Exception as e:
                print(f"Error cargando certificado de curso: {e}")
                c.certificado_base64 = None
    
    # Convertir certificados de Reconocimientos a base64
    for r in Reconocimientos:
        if r.archivo_certificado:
            try:
                # Manejar tanto archivos locales como URLs de Cloudinary
                if hasattr(r.archivo_certificado, 'path'):
                    cert_path = r.archivo_certificado.path
                    if os.path.exists(cert_path):
                        extension = cert_path.lower().split('.')[-1]
                        
                        if extension == 'pdf':
                            # Convertir PDF a imagen usando PyMuPDF
                            try:
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
                else:
                    # URL de Cloudinary
                    import urllib.request
                    cert_url = r.archivo_certificado.url
                    try:
                        # Descargar archivo de Cloudinary
                        with urllib.request.urlopen(cert_url) as response:
                            cert_data = response.read()
                            content_type = response.headers.get('Content-Type', 'application/octet-stream')
                            
                            # Detectar tipo desde URL o Content-Type
                            if 'pdf' in content_type or cert_url.lower().endswith('.pdf'):
                                # Para PDFs, intentar convertir a imagen con PyMuPDF
                                try:
                                    import io
                                    doc = fitz.open(stream=io.BytesIO(cert_data), filetype='pdf')
                                    if doc.page_count > 0:
                                        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                                        img_data = pix.tobytes("png")
                                        r.certificado_base64 = base64.b64encode(img_data).decode()
                                        r.certificado_mime_type = 'image/png'
                                        doc.close()
                                    else:
                                        r.certificado_base64 = None
                                except Exception as e:
                                    print(f"Error convirtiendo PDF a imagen: {e}")
                                    r.certificado_base64 = None
                            else:
                                # Para imágenes
                                r.certificado_base64 = base64.b64encode(cert_data).decode()
                                r.certificado_mime_type = content_type
                    except Exception as url_error:
                        print(f"Error descargando certificado de URL: {url_error}")
                        r.certificado_base64 = None
            except Exception as e:
                print(f"Error cargando certificado de reconocimiento: {e}")
                r.certificado_base64 = None
    
    # Convertir imágenes de VentaGarage a base64
    for v in VentaGarage:
        if v.imagen:
            try:
                # Manejar tanto archivos locales como URLs de Cloudinary
                if hasattr(v.imagen, 'path'):
                    img_path = v.imagen.path
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            v.imagen_base64 = base64.b64encode(f.read()).decode()
                    else:
                        v.imagen_base64 = None
                else:
                    # URL de Cloudinary
                    import urllib.request
                    img_url = v.imagen.url
                    try:
                        with urllib.request.urlopen(img_url) as response:
                            img_data = response.read()
                            v.imagen_base64 = base64.b64encode(img_data).decode()
                    except Exception as url_error:
                        print(f"Error descargando imagen de venta de URL: {url_error}")
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
        'Reconocimientos': Reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'VentaGarage': VentaGarage,
        'es_pdf': True,
        'foto_base64': foto_base64,
        'foto_mime_type': foto_mime_type,
        'base_url': base_url,
    }
    
    # Renderizar HTML
    html_string = render_to_string("hojavida/mi_hoja_vida_pdf.html", context)
    
    # Convertir a PDF usando pdfkit
    try:
       html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
       pdf_file = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 0.5in; margin-right: 0.5in; margin-bottom: 0.5in; margin-left: 0.5in; encoding: UTF-8; enable-local-file-access: None}')])

       response = HttpResponse(pdf_file, content_type='application/pdf')
       response['Content-Disposition'] = 'inline; filename="Hoja_de_Vida.pdf"'
       return response
    except Exception as e:
       print(f"Error generando PDF: {e}")
       return HttpResponse(f"Error generando PDF: {str(e)}", status=500)

# Vistas para descargar certificados
def descargar_certificado_curso(request, curso_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    curso = CursosRealizados.objects.filter(idcursorealizado=curso_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not curso or not curso.archivo_certificado:
        return HttpResponse("Certificado no encontrado", status=404)
    
    try:
        cert_path = curso.archivo_certificado.path
        if not os.path.exists(cert_path):
            return HttpResponse("Archivo no encontrado", status=404)
        
        with open(cert_path, 'rb') as f:
            file_data = f.read()
        
        extension = cert_path.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        content_type = mime_types.get(extension, 'application/octet-stream')
        filename = f"Certificado_{curso.nombrecurso}.{extension}"
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        print(f"Error descargando certificado: {e}")
        return HttpResponse(f"Error descargando certificado: {str(e)}", status=500)


def descargar_certificado_reconocimiento(request, reconocimiento_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    reconocimiento = Reconocimientos.objects.filter(idreconocimiento=reconocimiento_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not reconocimiento or not reconocimiento.archivo_certificado:
        return HttpResponse("Certificado no encontrado", status=404)
    
    try:
        cert_path = reconocimiento.archivo_certificado.path
        if not os.path.exists(cert_path):
            return HttpResponse("Archivo no encontrado", status=404)
        
        with open(cert_path, 'rb') as f:
            file_data = f.read()
        
        extension = cert_path.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        content_type = mime_types.get(extension, 'application/octet-stream')
        filename = f"Certificado_{reconocimiento.tiporeconocimiento}.{extension}"
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        print(f"Error descargando certificado: {e}")
        return HttpResponse(f"Error descargando certificado: {str(e)}", status=500)
