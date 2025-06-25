from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone

def generate_unique_reference_numbers(apps, schema_editor):
    StockMovement = apps.get_model('inventory', 'StockMovement')
    
    # Generate unique reference numbers for existing records
    current_year = timezone.now().year
    sequence = 1
    
    for movement in StockMovement.objects.all():
        if not movement.reference_number:
            ref_number = f"MOV-{current_year}-{sequence:04d}"
            movement.reference_number = ref_number
            movement.save()
            sequence += 1

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(generate_unique_reference_numbers, reverse_func),
    ]
