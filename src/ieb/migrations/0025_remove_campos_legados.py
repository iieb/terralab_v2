from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ieb', '0024_backfill_indicador_fk'),
    ]

    operations = [
        # Remover campos legados de AtividadeRegistro
        # (substituídos por AtividadeRegistroFoto e AtividadeRegistroListaPresenca)
        migrations.RemoveField(
            model_name='atividaderegistro',
            name='fotos',
        ),
        migrations.RemoveField(
            model_name='atividaderegistro',
            name='fotos_thumbnail',
        ),
        migrations.RemoveField(
            model_name='atividaderegistro',
            name='lista_presenca',
        ),
        # Remover model AtividadeRegistroEquipe
        # (duplicata de AtividadeRegistro.equipe_adicional M2M)
        migrations.DeleteModel(
            name='AtividadeRegistroEquipe',
        ),
    ]
