from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline
from ..models import Stock, StockMovementItem, Stockard

class StockInline(TabularInline):
    model = Stock
    extra = 1
    fields = ('product', 'quantity')
    readonly_fields = ()
    ordering = ('product__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')

class StockMovementItemInline(TabularInline):
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
