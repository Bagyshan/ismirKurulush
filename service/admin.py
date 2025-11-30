from django.contrib import admin
from .models import Service, Possibilities, Advantages, WorkProcess

# Register your models here.
class PossibilitiesInline(admin.TabularInline):
    model = Possibilities
    extra = 1
class AdvantagesInline(admin.TabularInline):
    model = Advantages
    extra = 1
class WorkProcessInline(admin.TabularInline):
    model = WorkProcess
    extra = 1
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at')
    date_hierarchy = 'created_at'
    inlines = [PossibilitiesInline, AdvantagesInline, WorkProcessInline]