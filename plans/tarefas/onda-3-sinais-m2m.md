# Onda 3 -- Sinais M2M

> **Pre-requisito:** Onda 2 concluida.
> **Paralelismo:** Tarefa unica.
> **Complexidade:** Media.
> **Revisado:** 2026-04-27 — correcao C3 aplicada.

---

## T-3.1: P0.9 -- Substituir `save()` por sinais `m2m_changed`

### Referencia no plano
P0.9 do Plano Cirurgico v1.3

### Problema
Models com M2M calculam totais no `save()`, mas `save()` nao e disparado quando itens M2M sao adicionados/removidos via admin ou shell. Isso causa totais dessincronizados.

### Arquivos
- `src/ieb/models.py` -- remover logica de recalculo dos `save()` afetados
- `src/ieb/signals.py` -- **NOVO** arquivo com receivers
- `src/ieb/apps.py` -- registrar signals no `ready()`

### Models afetados (6)
| Model | M2M | Total calculado |
|-------|-----|-----------------|
| `Leis` | `leis` | `total_leis`, `total_em_desenvolvimento`, `total_propostas`, `total_aprovadas`, `total_implementadas` |
| `Parcerias` | `parcerias` | `total_parcerias`, `total_governo_federal`, `total_governo_estadual_municipal`, `total_osc_ong`, `total_organizacao_internacional`, `total_inst_ensino`, `total_inst_pesquisa` |
| `Produtos` | `produtos` | `total_produtos`, `total_revistas`, `total_boletins`, `total_livros`, `total_sistematizacoes`, `total_notas_tecnicas`, `total_relatorios`, `total_cartilhas` |
| `Contratos` | `contratos` | `valor_total` (aggregate Sum) |
| `Area` | `tis`, `ucs`, `pas`, `tucs` | `total_ha` (aggregate Sum de area) |
| `AreasProtegidas` | `tis`, `ucs`, `pas`, `tucs` | `total_tis`, `total_ucs`, `total_pas`, `total_tucs`, `total`, `total_ha` |

### Estrutura do arquivo `signals.py`

```python
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Leis, Parcerias, Produtos, Contratos, Area, AreasProtegidas


def recalcular_leis(instance):
    """Recalcula totais de Leis baseado no M2M."""
    leis = instance.leis.all()
    instance.total_leis = leis.count()
    instance.total_em_desenvolvimento = leis.filter(situacao='em desenvolvimento').count()
    instance.total_propostas = leis.filter(situacao='proposta').count()
    instance.total_aprovadas = leis.filter(situacao='aprovada').count()
    instance.total_implementadas = leis.filter(situacao='implementada').count()
    instance.save(update_fields=[
        'total_leis', 'total_em_desenvolvimento', 'total_propostas',
        'total_aprovadas', 'total_implementadas',
    ])


@receiver(m2m_changed, sender=Leis.leis.through)
def leis_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_leis(instance)


# Repetir padrao para Parcerias, Produtos e Contratos.
# Para Contratos: aggregate Sum retorna None quando vazio; usar or 0:
# instance.valor_total = instance.contratos.aggregate(total=models.Sum('valor'))['total'] or 0


# Area e AreasProtegidas possuem 4 M2Ms cada: tis, ucs, pas, tucs.
# Registrar 4 receivers por model, ou 1 receiver por model com 4 decorators:
@receiver(m2m_changed, sender=Area.tis.through)
@receiver(m2m_changed, sender=Area.ucs.through)
@receiver(m2m_changed, sender=Area.pas.through)
@receiver(m2m_changed, sender=Area.tucs.through)
def area_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_area(instance)

@receiver(m2m_changed, sender=AreasProtegidas.tis.through)
@receiver(m2m_changed, sender=AreasProtegidas.ucs.through)
@receiver(m2m_changed, sender=AreasProtegidas.pas.through)
@receiver(m2m_changed, sender=AreasProtegidas.tucs.through)
def areas_protegidas_m2m_changed(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        recalcular_areas_protegidas(instance)
```

### Alteracao em `apps.py`

```python
class IebConfig(AppConfig):
    name = 'ieb'

    def ready(self):
        import ieb.signals  # noqa: F401
```

### Alteracao em `models.py`

#### Models simples: `Leis`, `Parcerias`, `Produtos`, `Contratos`

Esses models usam `save()` com logica de recalculo, mas sem o padrao double-save. Remover toda a logica de recalculo do `save()` e deixar apenas `super().save(*args, **kwargs)`. Se o `save()` so tinha logica de recalculo, pode ser removido inteiramente.

#### Models com double-save: `Area` e `AreasProtegidas`

Esses models usam `if not self.pk: super().save()` para obter um PK antes de setar M2Ms. O signal `m2m_changed` NAO e disparado durante esse primeiro save, porque os M2Ms ainda nao existem. Por isso:

1. **Manter** o `if not self.pk: super().save(*args, **kwargs)` (primeiro save para obter PK)
2. **Mover SOMENTE a logica de calculo** para o signal
3. **Remover** o `super().save(*args, **kwargs)` final do metodo
4. O `save()` resultante deve ser apenas:

```python
def save(self, *args, **kwargs):
    if not self.pk:
        super().save(*args, **kwargs)
```

Exemplo para `Area`:
```python
def recalcular_area(instance):
    if instance.ha_restrito is not None:
        instance.total_ha = instance.ha_restrito
    else:
        total = 0
        for m2m in (instance.tis, instance.ucs, instance.pas, instance.tucs):
            total += m2m.aggregate(s=models.Sum('area'))['s'] or 0
        instance.total_ha = total
    instance.save(update_fields=['total_ha'])
```

Exemplo para `AreasProtegidas`:
```python
def recalcular_areas_protegidas(instance):
    instance.total_tis  = instance.tis.count()
    instance.total_ucs  = instance.ucs.count()
    instance.total_pas  = instance.pas.count()
    instance.total_tucs = instance.tucs.count()
    instance.total = instance.total_tis + instance.total_ucs + instance.total_pas + instance.total_tucs
    ha = 0
    for m2m in (instance.tis, instance.ucs, instance.pas, instance.tucs):
        ha += m2m.aggregate(s=models.Sum('area'))['s'] or 0
    instance.total_ha = ha
    instance.save(update_fields=['total_tis', 'total_ucs', 'total_pas', 'total_tucs', 'total', 'total_ha'])
```

#### Contratos: tratamento de `None`

O `aggregate(Sum('valor'))` retorna `None` quando nao ha contratos. O signal deve usar `or 0`:

```python
def recalcular_contratos(instance):
    instance.valor_total = instance.contratos.aggregate(total=models.Sum('valor'))['total'] or 0
    instance.save(update_fields=['valor_total'])
```

### Migration
Nenhuma (somente logica Python).

### Atencao
- O signal `m2m_changed` nao e disparado quando o objeto e criado com M2M via bulk. Garantir que o `save()` inicial ainda sete defaults corretos.
- Para `Area` e `AreasProtegidas`, existem **4 M2Ms cada** (`tis`, `ucs`, `pas`, `tucs`). Sao necessarios **4 receivers separados por model** ou **1 receiver por model** registrado com os 4 senders.
- O signal recebe `instance` do model pai (nao do through). Usar `update_fields` no `save()` para evitar recursao.
- **Padrao double-save:** para `Area` e `AreasProtegidas`, manter o primeiro save para obter PK; remover apenas a logica de calculo e o save final.
- **Contratos aggregate None:** sempre usar `or 0` para evitar `None` em `valor_total`.
- **Areas e DecimalField:** usar fallback `or 0` nos somatorios para funcionar tanto antes quanto depois de T-5.1 (`FloatField -> DecimalField`). Nao usar `0.0` depois que os campos virarem `DecimalField`.

### Verificacao
```python
# Via admin: adicionar Parceria a Parcerias
p = Parcerias.objects.create(atividade_registro=ar, indicador=ind)
parc = Parceria.objects.create(nome='Teste', tipo='osc_ong')
p.parcerias.add(parc)
p.refresh_from_db()
p.total_parcerias  # Esperado: 1
p.total_osc_ong    # Esperado: 1

# Remover
p.parcerias.remove(parc)
p.refresh_from_db()
p.total_parcerias  # Esperado: 0

# Contratos com lista vazia
c = Contratos.objects.create(atividade_registro=ar, indicador=ind)
c.refresh_from_db()
c.valor_total  # Esperado: 0 (nao None)

# Area -- adicionar TI via M2M
a = Area.objects.create(atividade_registro=ar, indicador=ind)
ti = TIs.objects.create(nome='TI Teste', area=1000.0)
a.tis.add(ti)
a.refresh_from_db()
a.total_ha  # Esperado: 1000.0
```

### Dependencias
Onda 2 concluida (constraints ja aplicadas, related_names ja explicitos).
