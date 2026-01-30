from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date
from cloudinary.models import CloudinaryField

# --- FUNCIONES DE VALIDACIÓN PROFESIONALES ---

def validar_fecha_no_futura(value):
    if value and value > date.today():
        raise ValidationError('La fecha ingresada no puede ser posterior a la fecha actual.')

def validar_rango_edad_realista(value):
    if value and value < date(date.today().year - 100, 1, 1):
        raise ValidationError('La fecha ingresada es demasiado antigua (límite de 100 años).')

# --- 1. DATOS PERSONALES ---
class DatosPersonales(models.Model):
    SEXO_CHOICES = [('H', 'Hombre'), ('M', 'Mujer')]
    
    idperfil = models.AutoField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50, blank=True, null=True)
    perfilactivo = models.IntegerField(default=1)
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    foto_perfil = CloudinaryField('image', folder='fotos_perfil/', blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True, null=True)
    
    # Aplicación de validadores profesionales
    fechanacimiento = models.DateField(
        blank=True, 
        null=True, 
        validators=[validar_fecha_no_futura, validar_rango_edad_realista]
    )
    
    numerocedula = models.CharField(
        max_length=10, 
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'La cédula debe contener exactamente 10 dígitos numéricos')]
    )
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    estadocivil = models.CharField(max_length=50, blank=True, null=True)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    
    # Flags de control para visibilidad en PDF y Front-end
    mostrar_experiencia = models.BooleanField(default=True)
    mostrar_reconocimientos = models.BooleanField(default=True)
    mostrar_cursos = models.BooleanField(default=True)
    mostrar_productos_academicos = models.BooleanField(default=True)
    mostrar_productos_laborales = models.BooleanField(default=True)
    mostrar_venta_garage = models.BooleanField(default=False)

    # --- MENÚ DE SELECCIÓN PARA EL PDF ---
    imprimir_experiencia = models.BooleanField(default=True, verbose_name="¿Imprimir Experiencia?")
    imprimir_reconocimientos = models.BooleanField(default=True, verbose_name="¿Imprimir Reconocimientos?")
    imprimir_cursos = models.BooleanField(default=True, verbose_name="¿Imprimir Cursos?")
    imprimir_productos_academicos = models.BooleanField(default=True, verbose_name="¿Imprimir Productos Académicos?")
    imprimir_productos_laborales = models.BooleanField(default=True, verbose_name="¿Imprimir Productos Laborales?")
    imprimir_venta_garage = models.BooleanField(default=True, verbose_name="¿Imprimir Venta Garage?")
    
    class Meta:
        db_table = 'hojavida_datospersonales'
        verbose_name = 'Datos Personales'
        verbose_name_plural = 'Datos Personales'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

# --- 2. EXPERIENCIA LABORAL ---
class ExperienciaLaboral(models.Model):
    idexperiencialaboral = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='experiencias')
    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50, blank=True, null=True)
    emailempresa = models.EmailField(max_length=100, blank=True, null=True)
    sitiowebempresa = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoempresarial = models.CharField(max_length=60, blank=True, null=True)
    
    fechainiciogestion = models.DateField(validators=[validar_fecha_no_futura])
    fechafingestion = models.DateField(blank=True, null=True, validators=[validar_fecha_no_futura])
    
    descripcionfunciones = models.TextField(blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('raw', folder='certificados/experiencia/', blank=True, null=True)
    
    class Meta:
        db_table = 'hojavida_experiencialaboral'
        ordering = ['-fechainiciogestion']
        verbose_name = 'Experiencia Laboral'
        verbose_name_plural = 'Experiencias Laborales'
    
    def clean(self):
        # Validar que no sean fechas futuras
        if self.fechainiciogestion and self.fechainiciogestion > date.today():
            raise ValidationError({'fechainiciogestion': 'La fecha de inicio no puede ser en el futuro.'})
        
        if self.fechafingestion and self.fechafingestion > date.today():
            raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser en el futuro.'})
        
        # Validar que fin sea posterior a inicio
        if self.fechafingestion and self.fechainiciogestion:
            if self.fechafingestion < self.fechainiciogestion:
                raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser anterior a la fecha de inicio.'})
    
    def __str__(self):
        return f"{self.cargodesempenado} - {self.nombrempresa}"

# --- 3. RECONOCIMIENTOS ---
class Reconocimientos(models.Model):
    TIPO_CHOICES = [('Académico', 'Académico'), ('Público', 'Público'), ('Privado', 'Privado')]
    
    idreconocimiento = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='reconocimientos')
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES)
    fechareconocimiento = models.DateField(validators=[validar_fecha_no_futura])
    descripcionreconocimiento = models.TextField(blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('raw', folder='certificados/reconocimientos/', blank=True, null=True)
    
    class Meta:
        db_table = 'hojavida_reconocimientos'
        ordering = ['-fechareconocimiento']
        verbose_name = 'Reconocimiento'
        verbose_name_plural = 'Reconocimientos'
    
    def clean(self):
        if self.fechareconocimiento and self.fechareconocimiento > date.today():
            raise ValidationError({'fechareconocimiento': 'La fecha no puede ser en el futuro.'})
    
    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.entidadpatrocinadora}"

# --- 4. CURSOS REALIZADOS ---
class CursosRealizados(models.Model):
    idcursorealizado = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='cursos')
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField(validators=[validar_fecha_no_futura])
    fechafin = models.DateField(blank=True, null=True, validators=[validar_fecha_no_futura])
    totalhoras = models.IntegerField(blank=True, null=True)
    descripcioncurso = models.TextField(blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.EmailField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('raw', folder='certificados/cursos/', blank=True, null=True)
    
    class Meta:
        db_table = 'hojavida_cursosrealizados'
        ordering = ['-fechainicio']
        verbose_name = 'Curso Realizado'
        verbose_name_plural = 'Cursos Realizados'

    def clean(self):
        if self.fechafin and self.fechainicio:
            if self.fechafin < self.fechainicio:
                raise ValidationError('La fecha de culminación del curso debe ser posterior a la de inicio.')
    
    def __str__(self):
        return self.nombrecurso

# --- 5. PRODUCTOS ACADÉMICOS ---
class ProductosAcademicos(models.Model):
    CATEGORIA_CHOICES = [
        ('Artículo', 'Artículo Académico'),
        ('Tesis', 'Tesis o Proyecto de Grado'),
        ('Investigación', 'Investigación'),
        ('Publicación', 'Publicación'),
        ('Ponencia', 'Ponencia'),
        ('Tutorial', 'Tutorial'),
        ('Otro', 'Otro')
    ]

    idproductoacademico = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='productos_academicos')
    nombrerecurso = models.CharField(max_length=100)
    clasificador = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='Artículo')
    descripcion = models.TextField(blank=True, null=True)
    archivo = CloudinaryField('raw', folder='productos_academicos/', blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    fecha_registro = models.DateField(default=date.today, validators=[validar_fecha_no_futura])

    class Meta:
        db_table = 'hojavida_productosacademicos'
        ordering = ['-fecha_registro']
        verbose_name = 'Producto Académico'
        verbose_name_plural = 'Productos Académicos'
    
    def __str__(self):
        return self.nombrerecurso

# --- 6. PRODUCTOS LABORALES ---
class ProductosLaborales(models.Model):
    idproductoslaborales = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='productos_laborales')
    nombreproducto = models.CharField(max_length=100)
    fechaproducto = models.DateField(validators=[validar_fecha_no_futura])
    descripcion = models.TextField(blank=True, null=True)
    archivo = CloudinaryField('raw', folder='productos_laborales/', blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'hojavida_productoslaborales'
        ordering = ['-fechaproducto']
        verbose_name = 'Producto Laboral'
        verbose_name_plural = 'Productos Laborales'
    
    def __str__(self):
        return self.nombreproducto

# --- 7. VENTA GARAGE ---
class VentaGarage(models.Model):
    ESTADO_PRODUCTO_CHOICES = [('Bueno', 'Bueno'), ('Regular', 'Regular')]
    
    idventagarage = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, related_name='ventas_garage')
    nombreproducto = models.CharField(max_length=100)
    estadoproducto = models.CharField(max_length=40, choices=ESTADO_PRODUCTO_CHOICES, default='Bueno')
    descripcion = models.TextField(blank=True, null=True)
    valordelbien = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Imagen obligatoria para ventas
    imagen_producto = CloudinaryField('image', folder='ventas_garage/')
    
    # Fecha automática de publicación
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    activarparaqueseveaenfront = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'hojavida_ventas'
        ordering = ['-fecha_publicacion']
        verbose_name = 'Venta Garage'
        verbose_name_plural = 'Ventas Garage'
    
    def __str__(self):
        return f"{self.nombreproducto} - ${self.valordelbien}"