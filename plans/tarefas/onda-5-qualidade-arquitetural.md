# Onda 5 -- Qualidade Arquitetural

> **Pre-requisito:** TODAS as ondas anteriores concluidas e estaveis.
> **Paralelismo:** Sequencial obrigatorio. T-5.3 e a ULTIMA tarefa de todo o plano.
> **Complexidade:** Media (T-5.1, T-5.2) a ALTA (T-5.3).
> **Revisado:** 2026-04-27 — correcoes C5, M2, M3 aplicadas.

---

## T-5.1: P2.3 -- `FloatField` -> `DecimalField` para areas geograficas

### Referencia no plano
P2.3 do Plano Cirurgico v1.3

### Problema
`FloatField` em areas geograficas causa erros de precisao em somatorios acumulados.

### Arquivo
- `src/ieb/models.py`

### Campos a alterar

| Model | Campo | Linha aproximada |
|-------|-------|-----------------|
| `TIs` | `area` | ~46 |
| `UC` | `area` | ~631 |
| `PA` | `area` | ~643 |
| `TUC` | `area` | ~655 |
| `Area` | `ha_restrito` | ~671 |
| `Area` | `total_ha` | ~677 |
| `AreasProtegidas` | `total_ha` | ~712 |
| `Meta` | `base` | ~448 |
| `Meta` | `meta` | ~449 |
| `MetaFinanciador` | `base` | ~510 |
| `MetaFinanciador` | `meta` | ~511 |

> Nota: Se `Outro` foi removido em T-4.6, pular `Outro.valor`. Se nao, incluir.

### Alteracao
```python
# ANTES:
area = models.FloatField()

# DEPOIS:
area = models.DecimalField(max_digits=14, decimal_places=4)
```

### Migration
```python
operations = [
    migrations.AlterField('tis', 'area', field=models.DecimalField(max_digits=14, decimal_places=4, ...)),
    migrations.AlterField('uc', 'area', ...),
    migrations.AlterField('pa', 'area', ...),
    migrations.AlterField('tuc', 'area', ...),
    migrations.AlterField('area', 'ha_restrito', ...),
    migrations.AlterField('area', 'total_ha', ...),
    migrations.AlterField('areasprotegidas', 'total_ha', ...),
    migrations.AlterField('meta', 'base', ...),
    migrations.AlterField('meta', 'meta', ...),
    migrations.AlterField('metafinanciador', 'base', ...),
    migrations.AlterField('metafinanciador', 'meta', ...),
]
```

### Atencao
- `DecimalField` retorna `Decimal` do Python, nao `float`. Verificar se algum codigo faz comparacao com `float` literal.
- Atualizar `save()` de `Area`/`AreasProtegidas` para substituir qualquer fallback `or 0.0` por `or Decimal('0')`.
- Em agregacoes com `Sum()`, usar fallback Decimal para manter tipo consistente:
```python
from decimal import Decimal

result = queryset.aggregate(total=Sum('area'))
self.total_ha = result['total'] or Decimal('0')
```
- Nao misturar `float` e `Decimal` em soma, comparacao ou formatacao. Se houver entrada via POST, converter usando `Decimal(str(valor))` quando necessario.

### Verificacao
```python
# Somar areas no shell Python
from decimal import Decimal
total = sum(ti.area for ti in TIs.objects.all())
# Deve ser Decimal, sem erro de ponto flutuante
assert isinstance(total, Decimal)
```

### Dependencias
Todas as ondas anteriores (para evitar conflitos de migration).

---

## T-5.2: P2.5 -- Mover geracao de thumbnail para Celery

### Referencia no plano
P2.5 do Plano Cirurgico v1.3

### Problema
Geracao de thumbnail no `save()` de `AtividadeRegistroFoto` bloqueia a requisicao HTTP.

### Arquivos
- `src/ieb/models.py` -- classe `AtividadeRegistroFoto` (~linha 593-615)
- `src/ieb/tasks.py` -- **NOVO** (ou usar `src/tasks.py` se existir)
- `src/ieb/apps.py` -- registrar tasks (auto-discover do Celery)

### Alteracao

1. **Criar `tasks.py`**:
```python
from celery import shared_task
from .models import AtividadeRegistroFoto


@shared_task
def gerar_thumbnail(foto_pk):
    try:
        foto = AtividadeRegistroFoto.objects.get(pk=foto_pk)
    except AtividadeRegistroFoto.DoesNotExist:
        return

    # Logica extraida do save() atual
    if foto.foto:
        from io import BytesIO
        from PIL import Image
        import os

        img = Image.open(foto.foto)
        img.thumbnail((300, 300))
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)

        thumb_name = f"thumb_{os.path.basename(foto.foto.name)}"
        foto.foto_thumbnail.save(thumb_name, thumb_io, save=True)
```

2. **Alterar `save()` em `AtividadeRegistroFoto`** usando `transaction.on_commit()` para evitar race condition em que a task roda antes do commit da transacao:
```python
from django.db import transaction
from .tasks import gerar_thumbnail


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)  # primeiro save preserva PK/caminho do arquivo
    if self.foto and not self.foto_thumbnail:
        transaction.on_commit(lambda: gerar_thumbnail.delay(self.pk))
```

**Nao chamar a task antes do `super().save()`**: o arquivo pode ainda nao existir no storage e `self.pk` pode estar vazio.

3. **Registrar Celery auto-discover** (se necessario):
```python
# Em src/terralab_v2/celery.py (ou equivalente)
app.autodiscover_tasks(['ieb'])
```

### Migration
Nenhuma (somente logica Python).

### Atencao
- Verificar se o projeto ja usa Celery. Se nao, esta tarefa exige configuracao adicional (broker, worker e `app.autodiscover_tasks()`).
- O thumbnail pode nao estar disponivel imediatamente apos o upload. Garantir que o template lida com `foto_thumbnail` vazio.
- Usar `transaction.on_commit()` obrigatoriamente para evitar task lendo registro/arquivo antes do commit.
- Se nao houver Celery configurado, nao implementar uma solucao improvisada dentro do `save()`; manter sincrono por enquanto ou abrir uma tarefa separada de infraestrutura Celery.

### Verificacao
```python
# Upload de foto
foto = AtividadeRegistroFoto(foto=arquivo)
foto.save()

# Inicialmente sem thumbnail
assert not foto.foto_thumbnail

# Apos alguns segundos (task Celery)
foto.refresh_from_db()
assert foto.foto_thumbnail  # Thumbnail gerado
```

### Dependencias
Nenhuma tecnica, mas recomendado apos todas as ondas anteriores.

---

## T-5.3: P2.6 + P2.7 -- Modularizar `models.py` por subdominio

### Referencia no plano
P2.6 + P2.7 do Plano Cirurgico v1.3

### Complexidade
**ALTA** -- usar planejamento com agente `muse` antes de executar com `forge`.

### Problema
`models.py` e um arquivo monolitico com ~1200+ linhas e 40+ models. Dificil de navegar e manter.

### Pre-condicao
TODAS as tarefas anteriores concluidas e estaveis. Esta e a ULTIMA tarefa.

### Arquivos
- `src/ieb/models.py` -> `src/ieb/models/` (diretorio com multiplos modulos)

### Estrutura alvo

```
src/ieb/models/
    __init__.py          <- re-exporta tudo (from .movimento import *, etc.)
    movimento.py         <- OIsRegional, OIsLocal, TIs, Aldeia, Indigena, IGATI, OIRegLoc, TIsIGATI
    projetos.py          <- Programa, Projeto, Componente, Atividade, Subatividade, EquipeProjeto, ProjetoOI, ProjetoTI
    indicadores.py       <- Indicador, IndicadorFinanciador, Meta, MetaFinanciador, ProjetoIndicador, ProjetoIndicadorFin, choices, SCORE_PLANO, SUM_MAP
    monitoramento.py     <- AtividadeRegistro, AtividadeRegistroFoto, AtividadeRegistroListaPresenca, AtividadeRegistroModelo, Pessoas, Organizacoes, Area, AreasProtegidas, Evento, Rede/AtividadeRegistroRede, PequenoProjeto, Fundo, Leis, Parcerias, Planos, Produtos, Contratos, Mobilizados
    catalogos.py         <- UC, PA, TUC, Lei, LeiHistorico, Plano, PlanoHistorico, Parceria, Produto, Contrato, Modelo
    organizacional.py    <- Financiador, Instituicao, Equipe
    formacao.py          <- CR, CTL, DSEI, Posto, Casai, Polo, AIS, Escola, Professores, FormacaoIndigena
```

### Regras criticas

1. **`db_table` explicito em CADA model**: Para garantir que as tabelas no banco NAO mudem de nome:
```python
class Pessoas(models.Model):
    ...
    class Meta:
        db_table = 'ieb_pessoas'  # Nome exato da tabela atual
```

2. **`__init__.py` re-exporta tudo**: Para nao quebrar imports existentes:
```python
from .movimento import *
from .projetos import *
from .indicadores import *
from .monitoramento import *
from .catalogos import *
from .organizacional import *
from .formacao import *
```

3. **Verificar todos os imports externos**: `views.py`, `admin.py`, `signals.py`, `tests.py`, etc. devem continuar funcionando com `from ieb.models import X`.

4. **Constantes transversais**: mover para um modulo estavel e sem dependencia circular: `src/ieb/constants.py`. Este arquivo fica fora do pacote `models/` para poder ser importado por models, views, admin, signals e scripts auxiliares sem criar ciclos. Constantes conhecidas no codigo atual:
   - `INDICADOR_TIPO_CHOICES`
   - `SCORE_PLANO`
   - `FOCO_CHOICES`
   - `REDE_TIPO_CHOICES`
   - `FUNDO_TIPO_CHOICES`
   - `PARCERIA_TIPO_CHOICES`
   - `PRODUTO_TIPO_CHOICES`

```python
# src/ieb/constants.py
INDICADOR_TIPO_CHOICES = (...)
SCORE_PLANO = {...}
FOCO_CHOICES = (...)
REDE_TIPO_CHOICES = (...)
FUNDO_TIPO_CHOICES = (...)
PARCERIA_TIPO_CHOICES = (...)
PRODUTO_TIPO_CHOICES = (...)
```

Importar explicitamente nos modulos que precisarem:

```python
from ieb.constants import INDICADOR_TIPO_CHOICES, SCORE_PLANO
```

5. **FKs entre modulos**: preferir referencias por string (`'Indicador'`, `'AtividadeRegistro'`) quando isso reduzir import circular. Quando importar classes, importar do modulo especifico, nao de `__init__`:
```python
# Em monitoramento.py:
from .indicadores import Indicador, IndicadorFinanciador
from .catalogos import Lei, Plano, Parceria, Produto, Contrato
```

### Estrategia de execucao
1. Agente `muse` analisa `models.py` inteiro e cria plano de modularizacao exato (qual model vai para qual arquivo, imports cruzados)
2. Agente `forge` executa uma etapa por vez:
   - Etapa 1: Criar diretorio `models/` com `__init__.py` que importa tudo do `models.py` original
   - Etapa 2: Mover primeiro modulo (ex: `movimento.py`) e testar
   - Etapa 3-8: Mover demais modulos um por vez
   - Etapa 9: Remover `models.py` original
   - Etapa 10: Verificar todos os imports e rodar testes

### Migration
Nenhuma migration de banco. Pode haver necessidade de atualizar referencias em migrations existentes (Django usa string de model). Verificar se `models.py` e referenciado em migrations anteriores.

### Verificacao
```python
# Todos os imports continuam funcionando
from ieb.models import Pessoas, Indicador, AtividadeRegistro, Projeto

# db_table nao mudou
assert Pessoas._meta.db_table == 'ieb_pessoas'

# Migrations continuam funcionando
python manage.py makemigrations --dry-run  # "No changes detected"
python manage.py migrate  # OK
```

### Dependencias
TODAS as tarefas anteriores concluidas. Esta e a ULTIMA tarefa de todo o plano.
