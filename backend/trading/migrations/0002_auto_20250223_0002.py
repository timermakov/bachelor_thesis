from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
