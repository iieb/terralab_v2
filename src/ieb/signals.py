from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Area, AreasProtegidas, Contratos, Leis, Parcerias, Produtos


def recalcular_leis(instance):
    leis = instance.leis.all()
    instance.total_leis = leis.count()
    instance.total_em_desenvolvimento = leis.filter(situacao='em desenvolvimento').count()
    instance.total_propostas = leis.filter(situacao='proposto').count()
    instance.total_aprovadas = leis.filter(situacao='aprovado').count()
    instance.total_implementadas = leis.filter(situacao='implementado').count()
    instance.save(update_fields=[
        'total_leis',
        'total_em_desenvolvimento',
        'total_propostas',
        'total_aprovadas',
        'total_implementadas',
    ])


@receiver(m2m_changed, sender=Leis.leis.through)
def leis_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_leis(instance)


def recalcular_parcerias(instance):
    parcerias = instance.parcerias.all()
    instance.total_parcerias = parcerias.count()
    instance.total_governo_federal = parcerias.filter(tipo='governo_federal').count()
    instance.total_governo_estadual_municipal = parcerias.filter(tipo='governo_estadual_municipal').count()
    instance.total_osc_ong = parcerias.filter(tipo='osc_ong').count()
    instance.total_organizacao_internacional = parcerias.filter(tipo='organizacao_internacional').count()
    instance.total_inst_ensino = parcerias.filter(tipo='inst_ensino').count()
    instance.total_inst_pesquisa = parcerias.filter(tipo='inst_pesquisa').count()
    instance.save(update_fields=[
        'total_parcerias',
        'total_governo_federal',
        'total_governo_estadual_municipal',
        'total_osc_ong',
        'total_organizacao_internacional',
        'total_inst_ensino',
        'total_inst_pesquisa',
    ])


@receiver(m2m_changed, sender=Parcerias.parcerias.through)
def parcerias_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_parcerias(instance)


def recalcular_produtos(instance):
    produtos = instance.produtos.all()
    instance.total_produtos = produtos.count()
    instance.total_revistas = produtos.filter(tipo='revista').count()
    instance.total_boletins = produtos.filter(tipo='boletim').count()
    instance.total_livros = produtos.filter(tipo='livro').count()
    instance.total_sistematizacoes = produtos.filter(tipo='sistematizacao').count()
    instance.total_notas_tecnicas = produtos.filter(tipo='nota_tecnica').count()
    instance.total_relatorios = produtos.filter(tipo='relatorio').count()
    instance.total_cartilhas = produtos.filter(tipo='cartilha').count()
    instance.save(update_fields=[
        'total_produtos',
        'total_revistas',
        'total_boletins',
        'total_livros',
        'total_sistematizacoes',
        'total_notas_tecnicas',
        'total_relatorios',
        'total_cartilhas',
    ])


@receiver(m2m_changed, sender=Produtos.produtos.through)
def produtos_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_produtos(instance)


def recalcular_contratos(instance):
    instance.valor_total = instance.contratos.aggregate(total=models.Sum('valor'))['total'] or 0
    instance.save(update_fields=['valor_total'])


@receiver(m2m_changed, sender=Contratos.contratos.through)
def contratos_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_contratos(instance)


def recalcular_area(instance):
    if instance.ha_restrito is not None:
        total_ha = instance.ha_restrito
    else:
        total_ha = 0
        for m2m in (instance.tis, instance.ucs, instance.pas, instance.tucs):
            total_ha += m2m.aggregate(s=models.Sum('area'))['s'] or 0
    instance.total_ha = total_ha
    Area.objects.filter(pk=instance.pk).update(total_ha=total_ha)


@receiver(m2m_changed, sender=Area.tis.through)
@receiver(m2m_changed, sender=Area.ucs.through)
@receiver(m2m_changed, sender=Area.pas.through)
@receiver(m2m_changed, sender=Area.tucs.through)
def area_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_area(instance)


def recalcular_areas_protegidas(instance):
    total_tis = instance.tis.count()
    total_ucs = instance.ucs.count()
    total_pas = instance.pas.count()
    total_tucs = instance.tucs.count()
    total = total_tis + total_ucs + total_pas + total_tucs
    total_ha = 0
    for m2m in (instance.tis, instance.ucs, instance.pas, instance.tucs):
        total_ha += m2m.aggregate(s=models.Sum('area'))['s'] or 0

    instance.total_tis = total_tis
    instance.total_ucs = total_ucs
    instance.total_pas = total_pas
    instance.total_tucs = total_tucs
    instance.total = total
    instance.total_ha = total_ha
    AreasProtegidas.objects.filter(pk=instance.pk).update(
        total_tis=total_tis,
        total_ucs=total_ucs,
        total_pas=total_pas,
        total_tucs=total_tucs,
        total=total,
        total_ha=total_ha,
    )


@receiver(m2m_changed, sender=AreasProtegidas.tis.through)
@receiver(m2m_changed, sender=AreasProtegidas.ucs.through)
@receiver(m2m_changed, sender=AreasProtegidas.pas.through)
@receiver(m2m_changed, sender=AreasProtegidas.tucs.through)
def areas_protegidas_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_areas_protegidas(instance)
