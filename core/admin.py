from .models import Review, Thread, Post, Report
from django.contrib import admin
from .models import Brewery, Beer

# Personalización del sitio admin
admin.site.site_header = "🍺 Crisol del Cervecero - Administración"
admin.site.site_title = "Crisol del Cervecero"
admin.site.index_title = "Panel de Administración"

admin.site.register(Brewery)
admin.site.register(Beer)
admin.site.register(Review)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(Report)
