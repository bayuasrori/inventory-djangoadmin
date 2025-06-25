from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .utils import generate_reference_number

User = settings.AUTH_USER_MODEL

class Warehouse(models.Model):
    name = models.CharField(_('Warehouse Name'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
        ordering = ['name']

    def __str__(self):
        return self.name

class Stockard(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stockards')
    name = models.CharField(_('Stockard Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Stockard')
        verbose_name_plural = _('Stockards')
        ordering = ['warehouse__name', 'name']
        unique_together = ['warehouse', 'name']

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"

class Product(models.Model):
    name = models.CharField(_('Product Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']

    def __str__(self):
        return self.name

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    stockard = models.ForeignKey(Stockard, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(_('Quantity'), default=0)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        ordering = ['stockard__warehouse__name', 'stockard__name', 'product__name']
        unique_together = ['product', 'stockard']

    def __str__(self):
        return f"{self.product.name} in {self.stockard}"

    @property
    def is_in_stock(self):
        return self.quantity > 0

class StockMovement(models.Model):
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name=_('From Warehouse'),
        related_name='outbound_movements',
        null=True,
        blank=True
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name=_('To Warehouse'),
        related_name='inbound_movements',
        null=True,
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.warehouse_id:
            raise ValidationError(_('Warehouse is required'))
        if self.movement_type == 'TRANSFER' and not (self.from_warehouse and self.to_warehouse):
            raise ValidationError(_('Both From Warehouse and To Warehouse are required for transfer movements'))
        elif self.movement_type == 'IN' and not self.to_warehouse:
            raise ValidationError(_('To Warehouse is required for inbound movements'))
        elif self.movement_type == 'OUT' and not self.from_warehouse:
            raise ValidationError(_('From Warehouse is required for outbound movements'))
        if self.from_warehouse and self.to_warehouse and self.from_warehouse == self.to_warehouse:
            raise ValidationError(_('From Warehouse and To Warehouse must be different'))
        
        super().save(*args, **kwargs)

    MOVEMENT_TYPES = [
        ('IN', _('Inbound')),
        ('OUT', _('Outbound')),
        ('TRANSFER', _('Transfer')),
    ]
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES,
        verbose_name=_('Movement Type')
    )
    reference_number = models.CharField(
        max_length=50,
        verbose_name=_('Reference Number'),
        unique=True,
        help_text=_('A unique reference number for this movement'),
        default=generate_reference_number
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Created By')
    )

    class Meta:
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ('-created_at',)

    def __str__(self):
        return f"#{self.reference_number} - {self.get_movement_type_display()}"

class StockMovementItem(models.Model):
    movement = models.ForeignKey(
        StockMovement,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )
    from_stockard = models.ForeignKey(
        Stockard,
        on_delete=models.CASCADE,
        related_name='outbound_movement_items',
        verbose_name=_('From Stockard'),
        null=True,
        blank=True
    )
    to_stockard = models.ForeignKey(
        Stockard,
        on_delete=models.CASCADE,
        related_name='inbound_movement_items',
        verbose_name=_('To Stockard'),
        null=True,
        blank=True
    )

    quantity = models.IntegerField(
        verbose_name=_('Quantity')
    )

    class Meta:
        verbose_name = _('Stock Movement Item')
        verbose_name_plural = _('Stock Movement Items')
        ordering = ('movement', 'product')

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(_('Quantity must be greater than zero'))
        
        if self.movement.movement_type == 'OUT' or self.movement.movement_type == 'TRANSFER':
            if not self.product:
                raise ValidationError(_('Product is required'))
            
            try:
                stock = Stock.objects.get(
                    product=self.product,
                    stockard=self.from_stockard
                )
                if stock.quantity < self.quantity:
                    raise ValidationError(_(
                        'Not enough stock available. Only {} units available in stockard {}'
                    ).format(stock.quantity, self.from_stockard))
            except Stock.DoesNotExist:
                raise ValidationError(_(
                    'No stock available for this product in the selected stockard'
                ))
            
        # Skip stockard validation since they will be created in save()
        pass

    def save(self, *args, **kwargs):
        # Find or create stockards based on product and warehouse
        if self.movement.movement_type == 'IN':
            # For inbound, find or create a stockard in to_warehouse
            self.to_stockard = Stockard.objects.get_or_create(
                warehouse=self.movement.to_warehouse,
                name=f"{self.product.name} Stock"
            )[0]
        elif self.movement.movement_type == 'OUT':
            # For outbound, find the stockard with available stock in from_warehouse
            self.from_stockard = Stock.objects.filter(
                product=self.product,
                stockard__warehouse=self.movement.from_warehouse
            ).order_by('stockard__name').first()
            if not self.from_stockard:
                raise ValidationError(_('No stock available for this product in the selected warehouse'))
            self.from_stockard = self.from_stockard.stockard
        elif self.movement.movement_type == 'TRANSFER':
            # For transfer, find the stockard with available stock in from_warehouse
            self.from_stockard = Stock.objects.filter(
                product=self.product,
                stockard__warehouse=self.movement.from_warehouse
            ).order_by('stockard__name').first()
            if not self.from_stockard:
                raise ValidationError(_('No stock available for this product in the selected warehouse'))
            self.from_stockard = self.from_stockard.stockard
            
            # Create or get a stockard for to_stockard in to_warehouse
            self.to_stockard = Stockard.objects.get_or_create(
                warehouse=self.movement.to_warehouse,
                name=f"{self.product.name} Transfer Stock"
            )[0]

        # Update stock quantities
        if self.movement.movement_type == 'IN':
            stock, created = Stock.objects.get_or_create(
                product=self.product,
                stockard=self.to_stockard
            )
            stock.quantity += self.quantity
            stock.save()
        elif self.movement.movement_type == 'OUT':
            stock = Stock.objects.get(
                product=self.product,
                stockard=self.from_stockard
            )
            stock.quantity -= self.quantity
            stock.save()
        elif self.movement.movement_type == 'TRANSFER':
            from_stock = Stock.objects.get(
                product=self.product,
                stockard=self.from_stockard
            )
            to_stock, created = Stock.objects.get_or_create(
                product=self.product,
                stockard=self.to_stockard
            )
            from_stock.quantity -= self.quantity
            to_stock.quantity += self.quantity
            from_stock.save()
            to_stock.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.quantity}"
