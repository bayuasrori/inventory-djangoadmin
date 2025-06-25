from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_ensure_unique_reference_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockmovement',
            name='reference_number',
            field=models.CharField(
                max_length=50,
                unique=True,
                verbose_name='Reference Number',
                help_text='A unique reference number for this movement'
            ),
        ),
    ]
