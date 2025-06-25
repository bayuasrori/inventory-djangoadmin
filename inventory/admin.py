from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Warehouse, Stockard, Product, Stock, StockMovement, StockMovementItem

class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    fields = ('product', 'quantity')
    readonly_fields = ()
    ordering = ('product__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')

class StockMovementItemInline(admin.TabularInline):
    model = StockMovementItem
    extra = 1
    fields = (
        'product',
        'quantity'
    )
    readonly_fields = ()

    def save_formset(self, request, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Create stockards before validation
            if instance.movement.movement_type == 'IN':
                instance.to_stockard = Stockard.objects.get_or_create(
                    warehouse=instance.movement.to_warehouse,
                    name=f"{instance.product.name} Stock"
                )[0]
            elif instance.movement.movement_type == 'OUT':
                instance.from_stockard = Stock.objects.filter(
                    product=instance.product,
                    stockard__warehouse=instance.movement.from_warehouse
                ).order_by('stockard__name').first()
                if not instance.from_stockard:
                    raise ValidationError(_('No stock available for this product in the selected warehouse'))
                instance.from_stockard = instance.from_stockard.stockard
            elif instance.movement.movement_type == 'TRANSFER':
                instance.from_stockard = Stock.objects.filter(
                    product=instance.product,
                    stockard__warehouse=instance.movement.from_warehouse
                ).order_by('stockard__name').first()
                if not instance.from_stockard:
                    raise ValidationError(_('No stock available for this product in the selected warehouse'))
                instance.from_stockard = instance.from_stockard.stockard
                instance.to_stockard = Stockard.objects.get_or_create(
                    warehouse=instance.movement.to_warehouse,
                    name=f"{instance.product.name} Transfer Stock"
                )[0]
            instance.save()
        formset.save_m2m()

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

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()

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
