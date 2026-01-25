from django.urls import path
from django.views.generic import RedirectView
from .views import (
    mi_hoja_vida, panel_admin, login_view, logout_view, descargar_cv_pdf,
    agregar_datos, agregar_experiencia, agregar_curso,
    agregar_producto_academico, agregar_producto_laboral,
    agregar_reconocimiento, agregar_venta,
    editar_datos, editar_experiencia, editar_curso,
    editar_producto_academico, editar_producto_laboral,
    editar_reconocimiento, editar_venta, descargar_certificado_curso, descargar_certificado_reconocimiento
)

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False), name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('mi-hoja-vida/', mi_hoja_vida, name='mi_hoja_vida'),
    path('panel-admin/', panel_admin, name='panel_admin'),
    path("descargar-cv-pdf/", descargar_cv_pdf, name="descargar_cv_pdf"),
    path("descargar-certificado-curso/<int:curso_id>/", descargar_certificado_curso, name="descargar_certificado_curso"),
    path("descargar-certificado-reconocimiento/<int:reconocimiento_id>/", descargar_certificado_reconocimiento, name="descargar_certificado_reconocimiento"),

    # Rutas para agregar
    path('agregar-datos/', agregar_datos, name='agregar_datos'),
    path('agregar-experiencia/', agregar_experiencia, name='agregar_experiencia'),
    path('agregar-curso/', agregar_curso, name='agregar_curso'),
    path('agregar-producto-academico/', agregar_producto_academico, name='agregar_producto_academico'),
    path('agregar-producto-laboral/', agregar_producto_laboral, name='agregar_producto_laboral'),
    path('agregar-reconocimiento/', agregar_reconocimiento, name='agregar_reconocimiento'),
    path('agregar-venta/', agregar_venta, name='agregar_venta'),
    
    # Rutas para editar
    path('editar-datos/', editar_datos, name='editar_datos'),
    path('editar-experiencia-laboral/<int:experiencia_id>/', editar_experiencia, name='editar_experiencia_laboral'),
    path('editar-curso/<int:curso_id>/', editar_curso, name='editar_curso'),
    path('editar-producto-academico/<int:producto_id>/', editar_producto_academico, name='editar_producto_academico'),
    path('editar-producto-laboral/<int:producto_id>/', editar_producto_laboral, name='editar_producto_laboral'),
    path('editar-reconocimiento/<int:reconocimiento_id>/', editar_reconocimiento, name='editar_reconocimiento'),
    path('editar-venta/<int:venta_id>/', editar_venta, name='editar_venta'),
]