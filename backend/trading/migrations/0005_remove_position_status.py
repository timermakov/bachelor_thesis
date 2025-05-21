
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0004_auto_20250410_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='position',
            name='status',
        ),
    ]
