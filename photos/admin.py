from django.contrib import admin
from .models import Photo

# Register your models here.


class PhotoAdmin(admin.ModelAdmin):
    # prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'width')
    search_fields = ('title', )

admin.site.register(Photo, PhotoAdmin)
