import os
import tempfile
import pymupdf as fitz
from cloudinary.utils import cloudinary_url
from weasyprint import HTML, CSS
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from datetime import datetime
from django.contrib import messages
from .models import DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS, RECONOCIMIENTOS, PRODUCTOSACADEMICOS, PRODUCTOSLABORALES, VENTAS

# Vista para mostrar la hoja de vida sin iniciar sesión
def mi_hoja_vida(request):
    # Primero intenta buscar un perfil activo
    datos = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    
    # Si no hay perfil activo, busca el último perfil creado
    if not datos:
        datos = DATOSPERSONALES.objects.order_by('-idperfil').first()
    
    # Si definitivamente no hay ningún perfil en la base de datos
    if not datos:
        return render(request, 'hojavida/mi_hoja_vida.html', {
            'mensaje': 'No hay datos de perfil. Por favor, crea uno primero.'
        })

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
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    
    experiencias = EXPERIENCIALABORAL.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idexperiencia') if perfil else []
    cursos = CURSOSREALIZADOS.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idcurso') if perfil else []
    reconocimientos = RECONOCIMIENTOS.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idreconocimiento') if perfil else []
    productos_academicos = PRODUCTOSACADEMICOS.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idproducto') if perfil else []
    productos_laborales = PRODUCTOSLABORALES.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idproducto') if perfil else []
    ventas = VENTAS.objects.filter(idperfilconqueestaactivo=perfil).order_by('-idventa') if perfil else []
    
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
        from django.utils import timezone
        from datetime import datetime
        
        # Validar fecha de nacimiento
        fechanacimiento_str = request.POST.get('fechanacimiento')
        error = None
        
        if fechanacimiento_str:
            fechanacimiento = datetime.strptime(fechanacimiento_str, '%Y-%m-%d').date()
            if fechanacimiento > timezone.now().date():
                error = 'La fecha de nacimiento no puede ser en el futuro.'
        
        if error:
            return render(request, 'hojavida/agregar_datos.html', {'error': error})
        
        nuevo_perfil = DATOSPERSONALES(
            nombres=request.POST.get('nombres', ''),
            apellidos=request.POST.get('apellidos', ''),
            nacionalidad=request.POST.get('nacionalidad', ''),
            lugarnacimiento=request.POST.get('lugarnacimiento', ''),
            fechanacimiento=fechanacimiento_str or None,
            numerocedula=request.POST.get('numerocedula', ''),
            sexo=request.POST.get('sexo', 'H'),
            estadocivil=request.POST.get('estadocivil', ''),
            licenciaconducir=request.POST.get('licenciaconducir', ''),
            telefonofijo=request.POST.get('telefonofijo', ''),
            direcciondomiciliaria=request.POST.get('direcciondomiciliaria', ''),
            mostrar_experiencia=1 if request.POST.get('mostrar_experiencia') else 0,
            mostrar_cursos=1 if request.POST.get('mostrar_cursos') else 0,
            mostrar_reconocimientos=1 if request.POST.get('mostrar_reconocimientos') else 0,
            mostrar_productos_academicos=1 if request.POST.get('mostrar_productos_academicos') else 0,
            mostrar_productos_laborales=1 if request.POST.get('mostrar_productos_laborales') else 0,
            mostrar_ventas=1 if request.POST.get('mostrar_ventas') else 0,
            perfilactivo=1
        )
        if 'foto' in request.FILES:
            nuevo_perfil.foto = request.FILES['foto']
        nuevo_perfil.save()
        return redirect('panel_admin')

    return render(request, 'hojavida/agregar_datos.html')

@login_required
def agregar_experiencia(request):
    if request.method == 'POST':
        from django.utils import timezone
        from datetime import datetime
        
        perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
        if perfil:
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
                return render(request, 'hojavida/agregar_experiencia.html', {'error': error})
            
            EXPERIENCIALABORAL.objects.create(
                idperfilconqueestaactivo=perfil,
                empresa=request.POST.get('empresa', ''),
                cargo=request.POST.get('cargo', ''),
                fechainicio=fechainicio_str or None,
                fechafin=fechafin_str or None,
                descripcion=request.POST.get('descripcion', ''),
                activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
            )
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_experiencia.html')

@login_required
def agregar_curso(request):
    if request.method == 'POST':
        perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
        if perfil:
            curso = CURSOSREALIZADOS(
                idperfilconqueestaactivo=perfil,
                nombrecurso=request.POST.get('nombrecurso', ''),
                entidadpatrocinadora=request.POST.get('entidadpatrocinadora', ''),
                fechainicio=request.POST.get('fechainicio') or None,
                fechafin=request.POST.get('fechafin') or None,
                descripcion=request.POST.get('descripcion', ''),
                activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
            )
            if 'archivo_certificado' in request.FILES:
                curso.archivo_certificado = request.FILES['archivo_certificado']
            curso.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_curso.html')

@login_required
def agregar_producto_academico(request):
    if request.method == 'POST':
        perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
        if perfil:
            producto = PRODUCTOSACADEMICOS(
                idperfilconqueestaactivo=perfil,
                nombreproducto=request.POST.get('nombreproducto', ''),
                tiposproducto=request.POST.get('tiposproducto', ''),
                fechapublicacion=request.POST.get('fechapublicacion') or None,
                descripcion=request.POST.get('descripcion', ''),
                enlace=request.POST.get('enlace', ''),
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
        perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
        if perfil:
            reconocimiento = RECONOCIMIENTOS(
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
                reconocimiento.archivo_certificado = request.FILES['archivo_certificado']
            reconocimiento.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_reconocimiento.html')

# Vistas para Editar
@login_required
def editar_datos(request):
    datos = DATOSPERSONALES.objects.filter(perfilactivo=1).first()

    if request.method == 'POST' and datos:
        # 🔒 Guardar fecha original
        fecha_original = datos.fechanacimiento

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

        datos.mostrar_experiencia = 1 if request.POST.get('mostrar_experiencia') else 0
        datos.mostrar_cursos = 1 if request.POST.get('mostrar_cursos') else 0
        datos.mostrar_reconocimientos = 1 if request.POST.get('mostrar_reconocimientos') else 0
        datos.mostrar_productos_academicos = 1 if request.POST.get('mostrar_productos_academicos') else 0
        datos.mostrar_productos_laborales = 1 if request.POST.get('mostrar_productos_laborales') else 0
        datos.mostrar_ventas = 1 if request.POST.get('mostrar_ventas') else 0

        if 'foto' in request.FILES:
            datos.foto = request.FILES['foto']

        # 🔐 Restaurar fecha (no editable)
        datos.fechanacimiento = fecha_original

        datos.save()
        return redirect('panel_admin')

    return render(request, 'hojavida/editar_datos.html', {'datos': datos})

@login_required
def editar_experiencia(request, experiencia_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    experiencia = EXPERIENCIALABORAL.objects.filter(idexperiencia=experiencia_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
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
        
        experiencia.empresa = request.POST.get('empresa', experiencia.empresa)
        experiencia.cargo = request.POST.get('cargo', experiencia.cargo)
        experiencia.fechainicio = fechainicio_str or experiencia.fechainicio
        experiencia.fechafin = fechafin_str or experiencia.fechafin
        experiencia.descripcion = request.POST.get('descripcion', experiencia.descripcion)
        experiencia.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        experiencia.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_experiencia_laboral.html', {'experiencia': experiencia})

@login_required
def editar_curso(request, curso_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    curso = CURSOSREALIZADOS.objects.filter(idcurso=curso_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not curso:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        curso.nombrecurso = request.POST.get('nombrecurso', curso.nombrecurso)
        curso.entidadpatrocinadora = request.POST.get('entidadpatrocinadora', curso.entidadpatrocinadora)
        curso.fechainicio = request.POST.get('fechainicio') or curso.fechainicio
        curso.fechafin = request.POST.get('fechafin') or curso.fechafin
        curso.descripcion = request.POST.get('descripcion', curso.descripcion)
        if 'archivo_certificado' in request.FILES:
            curso.archivo_certificado = request.FILES['archivo_certificado']
        curso.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        curso.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_curso.html', {'curso': curso})

@login_required
def editar_producto_academico(request, producto_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    producto = PRODUCTOSACADEMICOS.objects.filter(idproducto=producto_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not producto:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
        producto.tiposproducto = request.POST.get('tiposproducto', producto.tiposproducto)
        producto.fechapublicacion = request.POST.get('fechapublicacion') or producto.fechapublicacion
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.enlace = request.POST.get('enlace', producto.enlace)
        if 'archivo' in request.FILES:
            producto.archivo = request.FILES['archivo']
        producto.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        producto.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_producto_academico.html', {'producto': producto})

@login_required
def editar_reconocimiento(request, reconocimiento_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    reconocimiento = RECONOCIMIENTOS.objects.filter(idreconocimiento=reconocimiento_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
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
            reconocimiento.archivo_certificado = request.FILES['archivo_certificado']
        reconocimiento.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        reconocimiento.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_reconocimiento.html', {'reconocimiento': reconocimiento})

@login_required
def agregar_producto_laboral(request):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        PRODUCTOSLABORALES.objects.create(
            idperfilconqueestaactivo=perfil,
            nombreproducto=request.POST.get('nombreproducto'),
            descripcion=request.POST.get('descripcion', ''),
            enlace=request.POST.get('enlace', ''),
            archivo=request.FILES.get('archivo'),
            activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
        )
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_producto_laboral.html')

@login_required
def agregar_venta(request):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        return redirect('agregar_datos')
    
    if request.method == 'POST':
        venta = VENTAS(
            idperfilconqueestaactivo=perfil,
            nombreproducto=request.POST.get('nombreproducto'),
            descripcion=request.POST.get('descripcion', ''),
            valordelbien=request.POST.get('valordelbien') or None,
            estadoproducto=request.POST.get('estadoproducto', ''),
            fechapublicacion=request.POST.get('fechapublicacion') or None,
            activarparaqueseveaenfront=1 if request.POST.get('activarparaqueseveaenfront') else 0
        )
        if 'archivo' in request.FILES:
            venta.archivo = request.FILES['archivo']
        if 'imagen' in request.FILES:
            venta.imagen = request.FILES['imagen']
        venta.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/agregar_venta.html')

@login_required
def editar_producto_laboral(request, producto_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    producto = PRODUCTOSLABORALES.objects.filter(idproducto=producto_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not producto:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
        producto.descripcion = request.POST.get('descripcion', producto.descripcion)
        producto.enlace = request.POST.get('enlace', producto.enlace)
        if 'archivo' in request.FILES:
            producto.archivo = request.FILES['archivo']
        producto.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        producto.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_producto_laboral.html', {'producto': producto})

@login_required
def editar_venta(request, venta_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    venta = VENTAS.objects.filter(idventa=venta_id, idperfilconqueestaactivo=perfil).first() if perfil else None
    
    if not venta:
        return redirect('panel_admin')
    
    if request.method == 'POST':
        venta.nombreproducto = request.POST.get('nombreproducto', venta.nombreproducto)
        venta.descripcion = request.POST.get('descripcion', venta.descripcion)
        venta.valordelbien = request.POST.get('valordelbien') or venta.valordelbien
        venta.estadoproducto = request.POST.get('estadoproducto', venta.estadoproducto)
        venta.fechapublicacion = request.POST.get('fechapublicacion') or venta.fechapublicacion
        if 'archivo' in request.FILES:
            venta.archivo = request.FILES['archivo']
        if 'imagen' in request.FILES:
            venta.imagen = request.FILES['imagen']
        venta.activarparaqueseveaenfront = 1 if request.POST.get('activarparaqueseveaenfront') else 0
        venta.save()
        return redirect('panel_admin')
    
    return render(request, 'hojavida/editar_venta.html', {'venta': venta})

# Vista para descargar el PDF de la hoja de vida 
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

# Vistas para descargar certificados
def descargar_certificado_curso(request, curso_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    curso = CURSOSREALIZADOS.objects.filter(idcurso=curso_id, idperfilconqueestaactivo=perfil).first()

    if not curso or not curso.archivo_certificado:
        return HttpResponse("Certificado no encontrado", status=404)

    url, _ = cloudinary_url(curso.archivo_certificado.public_id)
    return redirect(url)

def descargar_certificado_reconocimiento(request, reconocimiento_id):
    perfil = DATOSPERSONALES.objects.filter(perfilactivo=1).first()
    reconocimiento = RECONOCIMIENTOS.objects.filter(
        idreconocimiento=reconocimiento_id,
        idperfilconqueestaactivo=perfil
    ).first()

    if not reconocimiento or not reconocimiento.archivo_certificado:
        return HttpResponse("Certificado no encontrado", status=404)

    url, _ = cloudinary_url(reconocimiento.archivo_certificado.public_id)
    return redirect(url)
