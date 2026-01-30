import os
import base64
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from .models import DatosPersonales, ExperienciaLaboral, CursosRealizados, Reconocimientos, ProductosAcademicos, ProductosLaborales, VentaGarage

# Vista para mostrar la hoja de vida sin iniciar sesión
def mi_hoja_vida(request):
    # Intentamos traer el perfil marcado como activo
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    # Si no hay uno activo, traemos el último registro creado
    if not datos:
        datos = DatosPersonales.objects.order_by('-idperfil').first()
    
    # Si la base de datos está totalmente vacía
    if not datos:
        return render(request, 'hojavida/mi_hoja_vida.html', {
            'mensaje_error': 'Todavía no se han cargado datos en el sistema.'
        })

    # Traemos la información relacionada
    experiencias = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechainiciogestion')
    
    cursos = CursosRealizados.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechainicio')
    
    reconocimientos = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechareconocimiento')
    
    productos_academicos = ProductosAcademicos.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fecha_registro')
    
    productos_laborales = ProductosLaborales.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechaproducto')
    
    ventas = VentaGarage.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fecha_publicacion')

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

# Vista para el panel de administración
@login_required
def panel_admin(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    experiencias = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fechainiciogestion') if perfil else []
    
    cursos = CursosRealizados.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fechainicio') if perfil else []
    
    reconocimientos = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fechareconocimiento') if perfil else []
    
    productos_academicos = ProductosAcademicos.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fecha_registro') if perfil else []
    
    productos_laborales = ProductosLaborales.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fechaproducto') if perfil else []
    
    ventas = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil
    ).order_by('-fecha_publicacion') if perfil else []
    
    return render(request, 'hojavida/panel_admin.html', {
        'perfil': perfil,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas': ventas
    })

# ============================================
# VISTAS PARA AGREGAR
# ============================================

@login_required
def agregar_datos(request):
    if request.method == 'POST':
        fechanacimiento_str = request.POST.get('fechanacimiento')
        cedula = request.POST.get('numerocedula', '')
        error = None

        # Validación de fecha
        if fechanacimiento_str:
            try:
                fechanacimiento = datetime.strptime(fechanacimiento_str, '%Y-%m-%d').date()
                if fechanacimiento > timezone.now().date():
                    error = 'La fecha de nacimiento no puede ser en el futuro.'
            except ValueError:
                error = 'Formato de fecha inválido.'

        if error:
            return render(request, 'hojavida/agregar_datos.html', {'error': error})

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
                mostrar_experiencia=True if request.POST.get('mostrar_experiencia') else False,
                mostrar_cursos=True if request.POST.get('mostrar_cursos') else False,
                mostrar_reconocimientos=True if request.POST.get('mostrar_reconocimientos') else False,
                mostrar_productos_academicos=True if request.POST.get('mostrar_productos_academicos') else False,
                mostrar_productos_laborales=True if request.POST.get('mostrar_productos_laborales') else False,
                mostrar_venta_garage=True if request.POST.get('mostrar_ventas') else False,
                perfilactivo=1
            )

            if 'foto' in request.FILES:
                nuevo_perfil.foto_perfil = request.FILES['foto']

            nuevo_perfil.save()
            messages.success(request, "Datos personales guardados con éxito.")
            return redirect('panel_admin')

        except IntegrityError:
            error = f"El número de cédula '{cedula}' ya está registrado. Si desea actualizar sus datos, utilice la opción de editar."
            return render(request, 'hojavida/agregar_datos.html', {
                'error': error,
                'datos_previos': request.POST
            })

    return render(request, 'hojavida/agregar_datos.html')

@login_required
def agregar_experiencia(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        fechainicio = request.POST.get('fechainicio')
        fechafin = request.POST.get('fechafin') or None
        error = None

        # Validación de fechas
        if fechainicio:
            try:
                fecha_inicio_obj = datetime.strptime(fechainicio, '%Y-%m-%d').date()
                if fecha_inicio_obj > timezone.now().date():
                    error = 'La fecha de inicio no puede ser en el futuro.'
            except ValueError:
                error = 'Formato de fecha de inicio inválido.'

        if fechafin:
            try:
                fecha_fin_obj = datetime.strptime(fechafin, '%Y-%m-%d').date()
                if fecha_fin_obj > timezone.now().date():
                    error = 'La fecha de fin no puede ser en el futuro.'
                elif fechainicio and fecha_fin_obj < fecha_inicio_obj:
                    error = 'La fecha de fin no puede ser anterior a la fecha de inicio.'
            except ValueError:
                error = 'Formato de fecha de fin inválido.'

        if error:
            return render(request, 'hojavida/agregar_experiencia.html', {'error': error})

        try:
            ExperienciaLaboral.objects.create(
                idperfilconqueestaactivo=perfil,
                nombrempresa=request.POST.get('empresa', ''),
                cargodesempenado=request.POST.get('cargo', ''),
                descripcionfunciones=request.POST.get('descripcion', ''),
                fechainiciogestion=fechainicio,
                fechafingestion=fechafin,
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )
            messages.success(request, "Experiencia laboral agregada exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            return render(request, 'hojavida/agregar_experiencia.html', {'error': str(e)})

    return render(request, 'hojavida/agregar_experiencia.html')

@login_required
def agregar_curso(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            nuevo_curso = CursosRealizados(
                idperfilconqueestaactivo=perfil,
                nombrecurso=request.POST.get('nombrecurso', ''),
                entidadpatrocinadora=request.POST.get('entidadpatrocinadora', ''),
                fechainicio=request.POST.get('fechainicio') or None,
                fechafin=request.POST.get('fechafin') or None,
                descripcioncurso=request.POST.get('descripcion', ''),
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )

            if 'archivo_certificado' in request.FILES:
                nuevo_curso.rutacertificado = request.FILES['archivo_certificado']

            nuevo_curso.save()
            messages.success(request, "Curso agregado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al agregar curso: {str(e)}")

    return render(request, 'hojavida/agregar_curso.html')

@login_required
def agregar_producto_academico(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            nuevo_producto = ProductosAcademicos(
                idperfilconqueestaactivo=perfil,
                nombrerecurso=request.POST.get('nombreproducto', ''),
                clasificador=request.POST.get('tiposproducto', 'Artículo'),
                descripcion=request.POST.get('descripcion', ''),
                link=request.POST.get('enlace', ''),
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )

            if request.POST.get('fechapublicacion'):
                nuevo_producto.fecha_registro = request.POST.get('fechapublicacion')

            if 'archivo' in request.FILES:
                nuevo_producto.archivo = request.FILES['archivo']

            nuevo_producto.save()
            messages.success(request, "Producto académico agregado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al agregar producto académico: {str(e)}")

    return render(request, 'hojavida/agregar_producto_academico.html')

@login_required
def agregar_producto_laboral(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            # Validar que se proporcione fecha
            fecha = request.POST.get('fechaproducto')
            if not fecha:
                fecha = timezone.now().date()

            nuevo_producto = ProductosLaborales(
                idperfilconqueestaactivo=perfil,
                nombreproducto=request.POST.get('nombreproducto', ''),
                fechaproducto=fecha,
                descripcion=request.POST.get('descripcion', ''),
                link=request.POST.get('enlace', ''),
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )

            if 'archivo' in request.FILES:
                nuevo_producto.archivo = request.FILES['archivo']

            nuevo_producto.save()
            messages.success(request, "Producto laboral agregado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al agregar producto laboral: {str(e)}")

    return render(request, 'hojavida/agregar_producto_laboral.html')

@login_required
def agregar_reconocimiento(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            # Validar fecha si se proporciona
            fecha = request.POST.get('fechareconocimiento')
            if not fecha:
                fecha = timezone.now().date()

            nuevo_reconocimiento = Reconocimientos(
                idperfilconqueestaactivo=perfil,
                tiporeconocimiento=request.POST.get('tiporeconocimiento', ''),
                entidadpatrocinadora=request.POST.get('entidadpatrocinadora', ''),
                fechareconocimiento=fecha,
                descripcionreconocimiento=request.POST.get('descripcionreconocimiento', ''),
                nombrecontactoauspicia=request.POST.get('nombrecontactoauspicia', ''),
                telefonocontactoauspicia=request.POST.get('telefonocontactoauspicia', ''),
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )

            if 'archivo_certificado' in request.FILES:
                nuevo_reconocimiento.rutacertificado = request.FILES['archivo_certificado']

            nuevo_reconocimiento.save()
            messages.success(request, "Reconocimiento agregado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al agregar reconocimiento: {str(e)}")

    return render(request, 'hojavida/agregar_reconocimiento.html')

@login_required
def agregar_venta(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        messages.error(request, "Primero debe crear un perfil activo.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            # Validar que haya imagen
            if 'imagen' not in request.FILES:
                messages.error(request, "Debe subir una imagen del producto.")
                return render(request, 'hojavida/agregar_venta.html')

            nueva_venta = VentaGarage(
                idperfilconqueestaactivo=perfil,
                nombreproducto=request.POST.get('nombreproducto', ''),
                estadoproducto=request.POST.get('estadoproducto', 'Bueno'),
                valordelbien=request.POST.get('valordelbien', 0),
                descripcion=request.POST.get('descripcion', ''),
                imagen_producto=request.FILES['imagen'],
                activarparaqueseveaenfront=True if request.POST.get('activarparaqueseveaenfront') else False
            )

            nueva_venta.save()
            messages.success(request, "Venta agregada exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al agregar venta: {str(e)}")

    return render(request, 'hojavida/agregar_venta.html')

# ============================================
# VISTAS PARA EDITAR
# ============================================

@login_required
def editar_datos(request):
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()
    
    if not datos:
        messages.error(request, "No hay datos personales para editar.")
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        try:
            datos.nombres = request.POST.get('nombres', datos.nombres)
            datos.apellidos = request.POST.get('apellidos', datos.apellidos)
            datos.nacionalidad = request.POST.get('nacionalidad', datos.nacionalidad)
            datos.lugarnacimiento = request.POST.get('lugarnacimiento', datos.lugarnacimiento)
            datos.numerocedula = request.POST.get('numerocedula', datos.numerocedula)
            datos.sexo = request.POST.get('sexo', datos.sexo)
            datos.estadocivil = request.POST.get('estadocivil', datos.estadocivil)
            datos.licenciaconducir = request.POST.get('licenciaconducir', datos.licenciaconducir)
            datos.telefonofijo = request.POST.get('telefonofijo', datos.telefonofijo)
            datos.direcciondomiciliaria = request.POST.get('direcciondomiciliaria', datos.direcciondomiciliaria)
            datos.sitioweb = request.POST.get('sitioweb', datos.sitioweb)
            
            # Checkboxes de visibilidad
            datos.mostrar_experiencia = True if request.POST.get('mostrar_experiencia') else False
            datos.mostrar_cursos = True if request.POST.get('mostrar_cursos') else False
            datos.mostrar_reconocimientos = True if request.POST.get('mostrar_reconocimientos') else False
            datos.mostrar_productos_academicos = True if request.POST.get('mostrar_productos_academicos') else False
            datos.mostrar_productos_laborales = True if request.POST.get('mostrar_productos_laborales') else False
            datos.mostrar_venta_garage = True if request.POST.get('mostrar_ventas') else False

            if 'foto' in request.FILES:
                datos.foto_perfil = request.FILES['foto']

            datos.save()
            messages.success(request, "Datos personales actualizados exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            return render(request, 'hojavida/editar_datos.html', {
                'datos': datos,
                'error': str(e)
            })

    return render(request, 'hojavida/editar_datos.html', {'datos': datos})

@login_required
def editar_experiencia(request, experiencia_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    experiencia = get_object_or_404(ExperienciaLaboral, 
                                    idexperiencialaboral=experiencia_id, 
                                    idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            experiencia.nombrempresa = request.POST.get('empresa', experiencia.nombrempresa)
            experiencia.cargodesempenado = request.POST.get('cargo', experiencia.cargodesempenado)
            experiencia.fechainiciogestion = request.POST.get('fechainicio', experiencia.fechainiciogestion)
            experiencia.fechafingestion = request.POST.get('fechafin') or None
            experiencia.descripcionfunciones = request.POST.get('descripcion', experiencia.descripcionfunciones)
            experiencia.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            experiencia.save()
            messages.success(request, "Experiencia laboral actualizada exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            return render(request, 'hojavida/editar_experiencia_laboral.html', {
                'experiencia': experiencia,
                'error': str(e)
            })

    return render(request, 'hojavida/editar_experiencia_laboral.html', {'experiencia': experiencia})

@login_required
def editar_curso(request, curso_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    curso = get_object_or_404(CursosRealizados, 
                              idcursorealizado=curso_id, 
                              idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            curso.nombrecurso = request.POST.get('nombrecurso', curso.nombrecurso)
            curso.entidadpatrocinadora = request.POST.get('entidadpatrocinadora', curso.entidadpatrocinadora)
            curso.fechainicio = request.POST.get('fechainicio', curso.fechainicio)
            curso.fechafin = request.POST.get('fechafin') or None
            curso.totalhoras = request.POST.get('totalhoras') or None
            curso.descripcioncurso = request.POST.get('descripcion', curso.descripcioncurso)
            curso.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            if 'archivo_certificado' in request.FILES:
                curso.rutacertificado = request.FILES['archivo_certificado']

            curso.save()
            messages.success(request, "Curso actualizado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al actualizar curso: {str(e)}")

    return render(request, 'hojavida/editar_curso.html', {'curso': curso})

@login_required
def editar_producto_academico(request, producto_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    producto = get_object_or_404(ProductosAcademicos, 
                                 idproductoacademico=producto_id, 
                                 idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            producto.nombrerecurso = request.POST.get('nombreproducto', producto.nombrerecurso)
            producto.clasificador = request.POST.get('tiposproducto', producto.clasificador)
            producto.descripcion = request.POST.get('descripcion', producto.descripcion)
            producto.link = request.POST.get('enlace', producto.link)
            producto.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            if request.POST.get('fechapublicacion'):
                producto.fecha_registro = request.POST.get('fechapublicacion')

            if 'archivo' in request.FILES:
                producto.archivo = request.FILES['archivo']

            producto.save()
            messages.success(request, "Producto académico actualizado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al actualizar producto académico: {str(e)}")

    return render(request, 'hojavida/editar_producto_academico.html', {'producto': producto})

@login_required
def editar_producto_laboral(request, producto_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    producto = get_object_or_404(ProductosLaborales, 
                                 idproductoslaborales=producto_id, 
                                 idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
            producto.descripcion = request.POST.get('descripcion', producto.descripcion)
            producto.link = request.POST.get('enlace', producto.link)
            producto.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            if 'archivo' in request.FILES:
                producto.archivo = request.FILES['archivo']

            producto.save()
            messages.success(request, "Producto laboral actualizado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al actualizar producto laboral: {str(e)}")

    return render(request, 'hojavida/editar_producto_laboral.html', {'producto': producto})

@login_required
def editar_reconocimiento(request, reconocimiento_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    reconocimiento = get_object_or_404(Reconocimientos, 
                                       idreconocimiento=reconocimiento_id, 
                                       idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            reconocimiento.tiporeconocimiento = request.POST.get('tiporeconocimiento', reconocimiento.tiporeconocimiento)
            reconocimiento.entidadpatrocinadora = request.POST.get('entidadpatrocinadora', reconocimiento.entidadpatrocinadora)
            reconocimiento.fechareconocimiento = request.POST.get('fechareconocimiento', reconocimiento.fechareconocimiento)
            reconocimiento.descripcionreconocimiento = request.POST.get('descripcionreconocimiento', reconocimiento.descripcionreconocimiento)
            reconocimiento.nombrecontactoauspicia = request.POST.get('nombrecontactoauspicia', reconocimiento.nombrecontactoauspicia)
            reconocimiento.telefonocontactoauspicia = request.POST.get('telefonocontactoauspicia', reconocimiento.telefonocontactoauspicia)
            reconocimiento.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            if 'archivo_certificado' in request.FILES:
                reconocimiento.rutacertificado = request.FILES['archivo_certificado']

            reconocimiento.save()
            messages.success(request, "Reconocimiento actualizado exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al actualizar reconocimiento: {str(e)}")

    return render(request, 'hojavida/editar_reconocimiento.html', {'reconocimiento': reconocimiento})

@login_required
def editar_venta(request, venta_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    venta = get_object_or_404(VentaGarage, 
                              idventagarage=venta_id, 
                              idperfilconqueestaactivo=perfil)
    
    if request.method == 'POST':
        try:
            venta.nombreproducto = request.POST.get('nombreproducto', venta.nombreproducto)
            venta.estadoproducto = request.POST.get('estadoproducto', venta.estadoproducto)
            venta.valordelbien = request.POST.get('valordelbien', venta.valordelbien)
            venta.descripcion = request.POST.get('descripcion', venta.descripcion)
            venta.activarparaqueseveaenfront = True if request.POST.get('activarparaqueseveaenfront') else False

            if 'imagen' in request.FILES:
                venta.imagen_producto = request.FILES['imagen']

            venta.save()
            messages.success(request, "Venta actualizada exitosamente.")
            return redirect('panel_admin')
        except Exception as e:
            messages.error(request, f"Error al actualizar venta: {str(e)}")

    return render(request, 'hojavida/editar_venta.html', {'venta': venta})

# ============================================
# VISTA PARA DESCARGAR CV EN PDF
# ============================================

def descargar_cv_pdf(request):
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        return HttpResponse("WeasyPrint no está instalado. Instale con: pip install weasyprint", status=500)

    # Obtener datos del perfil activo
    datos = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not datos:
        return HttpResponse("No hay datos para descargar", status=400)

    # Obtener datos relacionados
    experiencias = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechainiciogestion')
    
    cursos = CursosRealizados.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechainicio')
    
    reconocimientos = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechareconocimiento')
    
    productos_academicos = ProductosAcademicos.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fecha_registro')
    
    productos_laborales = ProductosLaborales.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fechaproducto')
    
    ventas = VentaGarage.objects.filter(
        idperfilconqueestaactivo=datos,
        activarparaqueseveaenfront=True
    ).order_by('-fecha_publicacion')

    # Procesar foto de perfil a base64
    foto_base64 = None
    foto_mime_type = 'image/jpeg'
    
    if datos.foto_perfil:
        try:
            with datos.foto_perfil.open('rb') as f:
                foto_base64 = base64.b64encode(f.read()).decode()
                ext = datos.foto_perfil.name.lower().split('.')[-1]
                if ext == 'png':
                    foto_mime_type = 'image/png'
                elif ext == 'gif':
                    foto_mime_type = 'image/gif'
        except Exception as e:
            print(f"Error cargando foto: {e}")

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

    # Generar PDF
    try:
        html_string = render_to_string('hojavida/mi_hoja_vida_pdf.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CV_{datos.apellidos}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error generando PDF: {str(e)}", status=500)

# ============================================
# VISTAS PARA DESCARGAR CERTIFICADOS
# ============================================

def descargar_certificado_curso(request, curso_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    curso = get_object_or_404(CursosRealizados, 
                              idcursorealizado=curso_id, 
                              idperfilconqueestaactivo=perfil)
    
    if not curso.rutacertificado:
        return HttpResponse("Certificado no encontrado", status=404)
    
    try:
        # Para Cloudinary, redirigir a la URL
        if hasattr(curso.rutacertificado, 'url'):
            return redirect(curso.rutacertificado.url)
        else:
            return HttpResponse("Certificado no disponible", status=404)
    except Exception as e:
        return HttpResponse(f"Error descargando certificado: {str(e)}", status=500)

def descargar_certificado_reconocimiento(request, reconocimiento_id):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    reconocimiento = get_object_or_404(Reconocimientos, 
                                       idreconocimiento=reconocimiento_id, 
                                       idperfilconqueestaactivo=perfil)
    
    if not reconocimiento.rutacertificado:
        return HttpResponse("Certificado no encontrado", status=404)
    
    try:
        # Para Cloudinary, redirigir a la URL
        if hasattr(reconocimiento.rutacertificado, 'url'):
            return redirect(reconocimiento.rutacertificado.url)
        else:
            return HttpResponse("Certificado no disponible", status=404)
    except Exception as e:
        return HttpResponse(f"Error descargando certificado: {str(e)}", status=500)