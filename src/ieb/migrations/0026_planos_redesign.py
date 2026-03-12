from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ieb', '0025_remove_campos_legados'),
    ]

    operations = [
        # --- Plano: adicionar M2M com TIs ---
        migrations.AddField(
            model_name='plano',
            name='tis',
            field=models.ManyToManyField(
                blank=True,
                related_name='planos',
                to='ieb.tis',
                verbose_name='Terras Indígenas',
            ),
        ),

        # --- Indicador: adicionar FK para Plano ---
        migrations.AddField(
            model_name='indicador',
            name='plano',
            field=models.ForeignKey(
                blank=True,
                help_text='Preencher apenas quando tipo=planos',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='indicadores',
                to='ieb.plano',
                verbose_name='Plano monitorado',
            ),
        ),

        # --- Planos: remover campos legados ---
        migrations.RemoveField(
            model_name='planos',
            name='planos',
        ),
        migrations.RemoveField(
            model_name='planos',
            name='total_planos',
        ),

        # --- Planos: adicionar novos campos de situação ---
        migrations.AddField(
            model_name='planos',
            name='situacao_anterior',
            field=models.CharField(
                blank=True,
                choices=[
                    ('em desenvolvimento', 'Em Desenvolvimento'),
                    ('proposto', 'Proposto'),
                    ('adotado', 'Adotado'),
                    ('implementado', 'Implementado'),
                ],
                editable=False,
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='planos',
            name='situacao_nova',
            field=models.CharField(
                choices=[
                    ('em desenvolvimento', 'Em Desenvolvimento'),
                    ('proposto', 'Proposto'),
                    ('adotado', 'Adotado'),
                    ('implementado', 'Implementado'),
                ],
                default='em desenvolvimento',
                max_length=255,
            ),
        ),

    ]
