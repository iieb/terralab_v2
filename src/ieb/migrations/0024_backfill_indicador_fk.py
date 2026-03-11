"""
Data migration: popula o campo `indicador` nos 13 models de registro
para registros históricos criados antes da Fase 2.

Estratégia:
  Para cada AtividadeRegistro, busca Indicadores com Meta para aquela
  Atividade. Se houver exatamente 1 candidato do tipo correto, associa
  automaticamente. Casos ambíguos ficam com indicador=NULL.
"""
from django.db import migrations

TIPO_PARA_MODEL = {
    'treinados':      'treinados',
    'area_restrito':  'arearestrito',
    'area_direto':    'areadireto',
    'area_geral':     'areageral',
    'leis_politicas': 'leis',
    'capacitados':    'capacitados',
    'aplicacao':      'aplicacao',
    'planos':         'planos',
    'parcerias':      'parcerias',
    'mobilizados':    'mobilizados',
    'produtos':       'produtos',
    'contratos':      'contratos',
    'outro':          'atividaderegistromodelo',
}


def backfill_indicador(apps, schema_editor):
    AtividadeRegistro = apps.get_model('ieb', 'AtividadeRegistro')
    Meta = apps.get_model('ieb', 'Meta')

    model_map = {tipo: apps.get_model('ieb', model_name)
                 for tipo, model_name in TIPO_PARA_MODEL.items()}

    for ar in AtividadeRegistro.objects.select_related('atividade').iterator():
        if not ar.atividade_id:
            continue

        metas = Meta.objects.filter(
            atividade_id=ar.atividade_id
        ).select_related('indicador')

        # Agrupa indicadores por tipo
        tipo_indicadores = {}
        for meta in metas:
            tipo = meta.indicador.tipo
            tipo_indicadores.setdefault(tipo, []).append(meta.indicador)

        for tipo, indicadores in tipo_indicadores.items():
            Model = model_map.get(tipo)
            if not Model:
                continue

            registros = Model.objects.filter(
                atividade_registro=ar, indicador__isnull=True
            )
            if not registros.exists():
                continue

            # Apenas 1 candidato → inferência segura
            if len(indicadores) == 1:
                registros.update(indicador=indicadores[0])
            # Múltiplos candidatos → deixa NULL (ambíguo)


def reverse_backfill(apps, schema_editor):
    for model_name in TIPO_PARA_MODEL.values():
        Model = apps.get_model('ieb', model_name)
        Model.objects.update(indicador=None)


class Migration(migrations.Migration):

    dependencies = [
        ('ieb', '0023_aplicacao_indicador_areadireto_indicador_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_indicador, reverse_code=reverse_backfill),
    ]
