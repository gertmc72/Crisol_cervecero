from django.db.models import Avg
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import models


class Brewery(models.Model):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name


class Beer(models.Model):
    brewery = models.ForeignKey(Brewery, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    style = models.CharField(max_length=80)
    abv = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.style})"


class Review(models.Model):
    beer = models.ForeignKey(
        Beer, on_delete=models.CASCADE, related_name="reviews")
    user_name = models.CharField(max_length=100)
    aroma = models.PositiveSmallIntegerField()
    sabor = models.PositiveSmallIntegerField()
    cuerpo = models.PositiveSmallIntegerField()
    apariencia = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.user_name} para {self.beer.name}"


@receiver([post_save, post_delete], sender=Review)
def update_beer_avg_rating(sender, instance, **kwargs):
    beer = instance.beer
    avg = beer.reviews.aggregate(promedio=Avg(
        (models.F('aroma') + models.F('sabor') +
         models.F('cuerpo') + models.F('apariencia')) / 4
    ))["promedio"]
    beer.avg_rating = round(avg or 0, 2)
    beer.save()


class Thread(models.Model):
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE, related_name="threads")
    title = models.CharField(max_length=140)
    user_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.beer.name}"


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="posts")
    user_name = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Post de {self.user_name} en {self.thread.title}"


class Report(models.Model):
    OBJECT_TYPES = (
        ("post", "post"),
        ("review", "review"),
    )
    STATUS_CHOICES = (
        ("open", "open"),
        ("closed", "closed"),
    )

    object_type = models.CharField(max_length=10, choices=OBJECT_TYPES)
    object_id = models.PositiveIntegerField()
    user_name = models.CharField(max_length=100)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.object_type}:{self.object_id} ({self.status})"

    # TODO: proteger vistas de moderación con staff
    # TODO: permitir editar/borrar posts del autor
    # TODO: rate-limit en creación de posts/reviews