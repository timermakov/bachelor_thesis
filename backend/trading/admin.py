from django.contrib import admin
from .models import Position, Target


class TargetInline(admin.TabularInline):
    model = Target
    extra = 1


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    inlines = [TargetInline, ]
    list_display = ('__str__', 'author', 'created_date', 'modified_date')
    search_fields = ('base_asset', 'quote_asset', 'author__username')



