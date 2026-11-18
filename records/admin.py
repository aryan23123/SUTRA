from django.contrib import admin

from .models import Category, InformationRecord, Tag

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(InformationRecord)
