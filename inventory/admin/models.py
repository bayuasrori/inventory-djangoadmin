from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .inlines import StockInline, StockMovementItemInline
from ..models import Warehouse, Stockard, Product, Stock, StockMovement

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': (
                'movement_type',
                'from_warehouse',
                'to_warehouse',
                'reference_number',
                'notes'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'created_by'
            ),
            'classes': ('collapse',),
        }),
    )
    list_display = (
        'reference_number',
        'movement_type',
        'from_warehouse',
        'to_warehouse',
        'created_at',
        'created_by'
    )
    list_filter = (
        'movement_type',
        'created_at',
        'from_warehouse',
        'to_warehouse'
    )
    search_fields = (
        'reference_number',
        'notes',
        'items__product__name'
    )
    readonly_fields = ('created_at', 'created_by')
    inlines = [StockMovementItemInline]

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)

@admin.register(Stockard)
class StockardAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'created_at')
    list_filter = ('warehouse',)
    search_fields = ('name', 'description', 'warehouse__name')
    ordering = ('warehouse__name', 'name')
    fieldsets = (
        (None, {
            'fields': ('warehouse', 'name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)
    inlines = [StockInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [StockInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'stockard', 'quantity', 'is_in_stock', 'created_at')
    list_filter = ('stockard__warehouse', 'stockard')
    search_fields = (
        'product__name',
        'product__description',
        'stockard__name',
        'stockard__description',
        'stockard__warehouse__name'
    )
    ordering = ('stockard__warehouse__name', 'stockard__name', 'product__name')
    fieldsets = (
        (None, {
            'fields': ('product', 'stockard', 'quantity')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def is_in_stock(self, obj):
        return obj.quantity > 0
    is_in_stock.boolean = True
    is_in_stock.short_description = _('In Stock')
