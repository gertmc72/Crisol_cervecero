from .models import Review, Thread, Post, Report, ReviewPhoto
from django.contrib import admin
from .models import Brewery, Beer


class ReviewPhotoInline(admin.TabularInline):
    model = ReviewPhoto
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'beer', 'brand', 'brewery_name', 'created_at')
    list_filter = ('created_at', 'beer')
    search_fields = ('user_name', 'brand', 'brewery_name', 'comment')
    inlines = [ReviewPhotoInline]
    readonly_fields = ('created_at',)


# Personalización del sitio admin
admin.site.site_header = "🍺 Crisol del Cervecero - Administración"
admin.site.site_title = "Crisol del Cervecero"
admin.site.index_title = "Panel de Administración"

admin.site.register(Brewery)
admin.site.register(Beer)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(Report)
admin.site.register(ReviewPhoto)
