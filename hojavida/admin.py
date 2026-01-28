from django.contrib import admin
from .models import DATOSPERSONALES, EXPERIENCIALABORAL, CURSOSREALIZADOS, RECONOCIMIENTOS, PRODUCTOSACADEMICOS, PRODUCTOSLABORALES, VENTAS

@admin.register(DATOSPERSONALES)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'perfilactivo')
    fieldsets = (
        ('Perfil', {
            'fields': ('nombres', 'apellidos', 'descripcionperfil', 'perfilactivo')
        }),
        ('Datos Personales', {
            'fields': ('numerocedula', 'nacionalidad', 'lugarnacimiento', 'fechanacimiento', 'sexo', 'estadocivil', 'licenciaconducir')
        }),
        ('Contacto', {
            'fields': ('telefonoconvencional', 'telefonofijo', 'sitioweb')
        }),
        ('Dirección', {
            'fields': ('direcciondomiciliaria', 'direcciontrabajo')
        }),
        ('Foto', {
            'fields': ('foto',)
        }),
        ('Visibilidad de Secciones', {
            'fields': ('mostrar_experiencia', 'mostrar_cursos', 'mostrar_reconocimientos', 'mostrar_productos_academicos', 'mostrar_productos_laborales', 'mostrar_ventas')
        }),
    )

@admin.register(CURSOSREALIZADOS)
class CursosRealizadosAdmin(admin.ModelAdmin):
    list_display = ('curso', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Curso', {
            'fields': ('idperfilconqueestaactivo', 'curso', 'institucion', 'fechainicio', 'fechafin', 'descripcion')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )

@admin.register(EXPERIENCIALABORAL)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'empresa', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Experiencia', {
            'fields': ('idperfilconqueestaactivo', 'empresa', 'cargo', 'fechainicio', 'fechafin', 'descripcion')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )

@admin.register(RECONOCIMIENTOS)
class ReconocimientosAdmin(admin.ModelAdmin):
    list_display = ('nombrepremio', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Reconocimiento', {
            'fields': ('idperfilconqueestaactivo', 'nombrepremio', 'descripcion', 'fecha')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )

@admin.register(PRODUCTOSACADEMICOS)
class ProductosAcademicosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Producto', {
            'fields': ('idperfilconqueestaactivo', 'nombre', 'descripcion', 'url')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )

@admin.register(PRODUCTOSLABORALES)
class ProductosLaboralesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Producto', {
            'fields': ('idperfilconqueestaactivo', 'nombre', 'descripcion', 'url', 'ventas')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )

@admin.register(VENTAS)
class VentasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'idperfilconqueestaactivo', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    fieldsets = (
        ('Venta', {
            'fields': ('idperfilconqueestaactivo', 'nombre', 'descripcion', 'url', 'precio')
        }),
        ('Visibilidad', {
            'fields': ('activarparaqueseveaenfront',)
        }),
    )
