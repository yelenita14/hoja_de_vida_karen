from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class DATOSPERSONALES(models.Model):
    idperfil = models.AutoField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50, blank=True)
    perfilactivo = models.IntegerField(default=1)
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20, blank=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True)
    fechanacimiento = models.DateField(null=True, blank=True)
    numerocedula = models.CharField(max_length=10, unique=True)
    sexo = models.CharField(max_length=1, choices=[('H','Hombre'),('M','Mujer')])
    estadocivil = models.CharField(max_length=50, blank=True)
    licenciaconducir = models.CharField(max_length=6, blank=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True)
    telefonofijo = models.CharField(max_length=15, blank=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True)
    sitioweb = models.CharField(max_length=60, blank=True)
    foto = models.ImageField(upload_to='fotos/', null=True, blank=True)
    # Visibilidad de secciones
    mostrar_experiencia = models.IntegerField(default=1)
    mostrar_cursos = models.IntegerField(default=1)
    mostrar_reconocimientos = models.IntegerField(default=1)
    mostrar_productos_academicos = models.IntegerField(default=1)
    mostrar_productos_laborales = models.IntegerField(default=1)
    mostrar_ventas = models.IntegerField(default=1)

    def clean(self):
        if self.fechanacimiento and self.fechanacimiento > timezone.now().date():
            raise ValidationError({'fechanacimiento': 'La fecha de nacimiento no puede ser en el futuro.'})

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

class EXPERIENCIALABORAL(models.Model):
    idexperiencia = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.fechainicio > timezone.now().date():
            raise ValidationError({'fechainicio': 'La fecha de inicio no puede ser en el futuro.'})
        
        if self.fechafin and self.fechafin > timezone.now().date():
            raise ValidationError({'fechafin': 'La fecha de fin no puede ser en el futuro.'})
        
        if self.fechafin and self.fechainicio > self.fechafin:
            raise ValidationError({'fechafin': 'La fecha de fin debe ser posterior o igual a la fecha de inicio.'})

    def __str__(self):
        return f"{self.cargo} - {self.empresa}"


class CURSOSREALIZADOS(models.Model):
    idcurso = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    nombrecurso = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    fechainicio = models.DateField(null=True, blank=True)
    fechafin = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    archivo_certificado = models.FileField(upload_to='certificados/', null=True, blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def __str__(self):
        return self.nombrecurso


class RECONOCIMIENTOS(models.Model):
    idreconocimiento = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    tiporeconocimiento = models.CharField(max_length=50)
    entidadpatrocinadora = models.CharField(max_length=100)
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.TextField(blank=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True)
    telefonocontactoauspicia = models.CharField(max_length=20, blank=True)
    archivo_certificado = models.FileField(upload_to='certificados/', null=True, blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.entidadpatrocinadora}"


class PRODUCTOSACADEMICOS(models.Model):
    idproducto = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=150)
    tiposproducto = models.CharField(max_length=100)
    fechapublicacion = models.DateField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    enlace = models.URLField(max_length=200, blank=True)
    archivo = models.FileField(upload_to='productos/', null=True, blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.nombreproducto} - {self.tiposproducto}"


class PRODUCTOSLABORALES(models.Model):
    idproducto = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    enlace = models.URLField(max_length=200, blank=True)
    archivo = models.FileField(upload_to='productos/', null=True, blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.nombreproducto}"


class VENTAS(models.Model):
    ESTADO_CHOICES = [
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
    ]
    
    idventa = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DATOSPERSONALES, on_delete=models.CASCADE)
    nombreproducto = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    valordelbien = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estadoproducto = models.CharField(max_length=50, choices=ESTADO_CHOICES, blank=True)
    archivo = models.FileField(upload_to='ventas/', null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fechapublicacion = models.DateField(null=True, blank=True)
    activarparaqueseveaenfront = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.nombreproducto} - ${self.valordelbien}"