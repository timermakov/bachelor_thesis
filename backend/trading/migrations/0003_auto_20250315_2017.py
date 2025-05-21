
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0002_auto_20250223_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targets', to='trading.position'),
        ),
    ]
