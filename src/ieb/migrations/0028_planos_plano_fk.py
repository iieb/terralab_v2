from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ieb', '0027_indicadorfinanciadore'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicador',
            name='plano',
        ),
        migrations.AddField(
            model_name='planos',
            name='plano',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='registros',
                to='ieb.plano',
                verbose_name='Plano',
            ),
        ),
    ]
