# Onda 1 -- Correcoes Pontuais Independentes

> **Pre-requisito:** Onda 0 (indexacao) concluida.
> **Paralelismo:** Todas as 9 tarefas sao 100% paralelas entre si.
> **Complexidade:** Baixa. Cada tarefa altera 1 arquivo + 1 migration.
> **Revisado:** 2026-04-27 — correcoes C1, A1, A2 aplicadas.

---

## T-1.1: P0.8 -- Corrigir `Evento.total` (substituir `if v` por `or 0`)

### Referencia no plano
P0.8 do Plano Cirurgico v1.3

### Problema
O `save()` de `Evento` usa `sum(v for v in [...] if v)` que filtra valores falsy (`None` E `0`). Isso significa que um campo intencionalmente enviado como `0` e excluido da soma. A correcao com `(v or 0)` e mais defensiva e explicita, tratando `None` como `0` e preservando `0` literais.

### Arquivo
- `src/ieb/models.py` -- metodo `save()` da classe `Evento` (~linha 852-854)

### Alteracao
```python
# ANTES:
total = sum(v for v in [self.formacoes, self.seminarios, self.encontros, self.reunioes] if v)

# DEPOIS:
total = sum((v or 0) for v in [self.formacoes, self.seminarios, self.encontros, self.reunioes])
```

### Migration
Nenhuma (somente logica Python, sem mudanca de schema).

### Verificacao
```python
Evento(formacoes=0, seminarios=0, encontros=0, reunioes=0).save()
# Esperado: total=0
Evento(formacoes=None, seminarios=2).save()
# Esperado: total=2
```

### Dependencias
Nenhuma.

---

## T-1.2: P0.10 -- `Contratos.valor_total` com `default=0`

### Referencia no plano
P0.10 do Plano Cirurgico v1.3

### Problema
`valor_total` em `Contratos` nao tem default, causando `None` em novos registros. Alem disso, o `save()` de `Contratos` (linha 1174) faz `self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']` que retorna `None` quando nao ha contratos com valor. Mesmo com `default=0`, o `save()` sobrescreve com `None`.

### Arquivo
- `src/ieb/models.py` -- campo `valor_total` em `Contratos` (~linha 1166) e metodo `save()` (~linha 1171-1175)

### Alteracao

1. Corrigir campo `valor_total`:
```python
# ANTES:
valor_total = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, editable=False)

# DEPOIS:
valor_total = DecimalField(max_digits=15, decimal_places=2, default=0, editable=False)
```

2. Corrigir `save()` de `Contratos` para usar `or 0` no aggregate result:
```python
# ANTES (linha 1174):
self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']

# DEPOIS:
self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total'] or 0
```
Sem isso, o `save()` sobrescreve o `default=0` com `None`.

### Migration
```python
operations = [
    migrations.AlterField(
        model_name='contratos',
        name='valor_total',
        field=models.DecimalField(default=0, editable=False, max_digits=15, decimal_places=2),
    ),
]
```

### Verificacao
```python
c = Contratos.objects.create(atividade_registro=ar, indicador=ind)
c.valor_total  # Esperado: 0 (nao None)
c.save()
c.valor_total  # Esperado: 0 (nao None -- save() nao deve sobrescrever com None)
```

### Dependencias
Nenhuma.

---

## T-1.3: P0.11 -- `CheckConstraint: data_final >= data_inicio` em `AtividadeRegistro`

### Referencia no plano
P0.11 do Plano Cirurgico v1.3

### Problema
Nao ha validacao no banco para garantir que `data_final >= data_inicio`.

### Arquivo
- `src/ieb/models.py` -- classe `AtividadeRegistro` (~linha 570-591)

### Alteracao
CRIAR classe Meta em `AtividadeRegistro` (o model atual NAO tem classe Meta). Adicionar apos o campo `email_organizacao` e antes do `def __str__`:
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(data_final__gte=models.F('data_inicio')),
            name='data_final_gte_data_inicio',
        ),
    ]
```

### Migration
```python
operations = [
    migrations.AddConstraint(
        model_name='atividaderegistro',
        constraint=models.CheckConstraint(
            check=models.Q(data_final__gte=models.F('data_inicio')),
            name='data_final_gte_data_inicio',
        ),
    ),
]
```

### Atencao
Verificar se existem registros no banco que violam esta constraint antes de aplicar a migration. Se houver, criar data migration para corrigir.

### Verificacao
```python
ar = AtividadeRegistro(data_inicio='2026-06-01', data_final='2026-01-01')
ar.save()  # Esperado: IntegrityError
```

### Dependencias
Nenhuma.

---

## T-1.4: P0.12 -- `CheckConstraint: data >= data_inicio` em `Meta` e `MetaFinanciador`

### Referencia no plano
P0.12 do Plano Cirurgico v1.3

### Problema
`Meta` tem `data_inicio` e `data` (prazo/fim), mas sem validacao de que `data >= data_inicio`.

### Arquivos
- `src/ieb/models.py` -- classe `Meta` (~linha 445-455) e `MetaFinanciador` (~linha 507-516)

### Alteracao
CRIAR classe Meta em `Meta` (apos `def percentual`) e em `MetaFinanciador` (apos `def percentual`). Ambos NAO tem classe Meta atualmente. Adicionar em ambas:
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(data_inicio__isnull=True) | models.Q(data__gte=models.F('data_inicio')),
            name='%(class)s_data_gte_data_inicio',
        ),
    ]
```

### Migration
```python
operations = [
    migrations.AddConstraint(
        model_name='meta',
        constraint=models.CheckConstraint(..., name='meta_data_gte_data_inicio'),
    ),
    migrations.AddConstraint(
        model_name='metafinanciador',
        constraint=models.CheckConstraint(..., name='metafinanciador_data_gte_data_inicio'),
    ),
]
```

### Verificacao
```python
Meta(data_inicio='2026-06-01', data='2026-01-01', ...).save()  # IntegrityError
Meta(data_inicio=None, data='2026-01-01', ...).save()  # OK (data_inicio null e permitido)
```

### Dependencias
Nenhuma.

---

## T-1.5: P1.5 -- `unique_together` em `OIRegLoc`

### Referencia no plano
P1.5 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- classe `OIRegLoc` (~linha 36-41)

### Alteracao
CRIAR classe Meta em `OIRegLoc` (apos o campo `oilocal` e antes de `def __str__`). O model NAO tem classe Meta atualmente.
```python
class Meta:
    unique_together = ('oiregional', 'oilocal')
```

### Migration
```python
operations = [
    migrations.AlterUniqueTogether(
        model_name='oiregloc',
        unique_together={('oiregional', 'oilocal')},
    ),
]
```
Nota: `AlterUniqueTogether` funciona corretamente aqui -- Django criara a constraint unique_together mesmo sem uma pre-existente.

### Verificacao
Duplicar par `oiregional + oilocal` -> `IntegrityError`

### Dependencias
Nenhuma.

---

## T-1.6: P1.6 -- `unique_together` em `TIsIGATI`

### Referencia no plano
P1.6 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- classe `TIsIGATI` (~linha 90-95)

### Alteracao
CRIAR classe Meta em `TIsIGATI` (apos o campo `tis` e antes de `def __str__`). O model NAO tem classe Meta atualmente.
```python
class Meta:
    unique_together = ('igati', 'tis')
```

### Migration
```python
operations = [
    migrations.AlterUniqueTogether(
        model_name='tisigati',
        unique_together={('igati', 'tis')},
    ),
]
```

### Verificacao
Duplicar par `igati + tis` -> `IntegrityError`

### Dependencias
Nenhuma.

---

## T-1.7: P1.7 -- `unique_together` em `EquipeProjeto`, `ProjetoOI`, `ProjetoTI`

### Referencia no plano
P1.7 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- 3 classes (~linha 189-210)

### Alteracao
CRIAR classe Meta em cada um dos tres models (nenhum tem classe Meta atualmente):
```python
# EquipeProjeto -- apos o campo projeto
class Meta:
    unique_together = ('equipe', 'projeto')

# ProjetoOI -- apos o campo projeto
class Meta:
    unique_together = ('oilocal', 'projeto')

# ProjetoTI -- apos o campo projeto
class Meta:
    unique_together = ('tis', 'projeto')
```

### Migration
```python
operations = [
    migrations.AlterUniqueTogether('equiprojeto', {('equipe', 'projeto')}),
    migrations.AlterUniqueTogether('projetooi', {('oilocal', 'projeto')}),
    migrations.AlterUniqueTogether('projetoti', {('tis', 'projeto')}),
]
```

### Verificacao
Duplicar qualquer par -> `IntegrityError`

### Dependencias
Nenhuma.

---

## T-1.8: P1.8 -- `unique_together` contextual de `Componente.codigo` e `Atividade.codigo`

### Referencia no plano
P1.8 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- `Componente` (~linha 169-176) e `Atividade` (~linha 179-186)

### Alteracao
CRIAR classe Meta em `Componente` e em `Atividade` (nenhum dos dois tem classe Meta atualmente):
```python
# Componente -- apos o campo instituicao
class Meta:
    unique_together = ('projeto', 'codigo')

# Atividade -- apos o campo componente
class Meta:
    unique_together = ('componente', 'codigo')
```

### Migration
```python
operations = [
    migrations.AlterUniqueTogether('componente', {('projeto', 'codigo')}),
    migrations.AlterUniqueTogether('atividade', {('componente', 'codigo')}),
]
```

### Verificacao
Mesmo codigo no mesmo pai -> `IntegrityError`. Codigos iguais em pais diferentes -> OK.

### Dependencias
Nenhuma.

---

## T-1.9: P1.9 -- `unique_together` em `Subatividade.codigo`

### Referencia no plano
P1.9 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- classe `Subatividade` (~linha 253-260)

### Alteracao
CRIAR classe Meta em `Subatividade` (o model NAO tem classe Meta atualmente). Adicionar apos o campo `atividade`:
```python
class Meta:
    unique_together = ('atividade', 'codigo')
```

### Migration
```python
operations = [
    migrations.AlterUniqueTogether('subatividade', {('atividade', 'codigo')}),
]
```

### Verificacao
Mesmo codigo na mesma atividade -> `IntegrityError`

### Dependencias
Nenhuma.

---

## T-1.11: P1.11 -- `CheckConstraint: valor_mobilizado > 0` em `Mobilizados`

### Referencia no plano
P1.11 do Plano Cirurgico v1.3

### Arquivo
- `src/ieb/models.py` -- classe `Mobilizados` (~linha 1060-1088)

### Alteracao
`Mobilizados` JA POSSUI classe Meta com `verbose_name` e `unique_together = ('atividade_registro', 'indicador')`. ADICIONAR `constraints` a classe Meta existente (preservando o `unique_together` ja existente):
```python
class Meta:
    verbose_name = 'Mobilizado'
    verbose_name_plural = 'Mobilizados'
    unique_together = ('atividade_registro', 'indicador')  # ja existente -- preservar
    constraints = [  # ADICIONAR isto
        models.CheckConstraint(
            check=models.Q(valor_mobilizado__gt=0),
            name='valor_mobilizado_positive',
        ),
    ]
```

### Migration
```python
operations = [
    migrations.AddConstraint(
        model_name='mobilizados',
        constraint=models.CheckConstraint(
            check=models.Q(valor_mobilizado__gt=0),
            name='valor_mobilizado_positive',
        ),
    ),
]
```

### Verificacao
```python
Mobilizados(valor_mobilizado=0, ...).save()  # IntegrityError
Mobilizados(valor_mobilizado=100, ...).save()  # OK
```

### Dependencias
Nenhuma.

---

## Resultado da execucao — 2026-04-27

### Status
Concluida.

### Arquivos alterados
- `src/ieb/models.py`
- `src/ieb/migrations/0033_alter_contratos_valor_total_and_more.py`

### Tarefas executadas
- T-1.1: `Evento.save()` passou a somar campos com `(v or 0)`.
- T-1.2: `Contratos.valor_total` recebeu `default=0` e o aggregate do `save()` passou a usar fallback `or 0`.
- T-1.3: adicionada constraint `data_final_gte_data_inicio` em `AtividadeRegistro`.
- T-1.4: adicionadas constraints `meta_data_gte_data_inicio` e `metafinanciador_data_gte_data_inicio`.
- T-1.5: adicionado `unique_together` em `OIRegLoc`.
- T-1.6: adicionado `unique_together` em `TIsIGATI`.
- T-1.7: adicionados `unique_together` em `EquipeProjeto`, `ProjetoOI` e `ProjetoTI`.
- T-1.8: adicionados `unique_together` contextuais em `Componente` e `Atividade`.
- T-1.9: adicionado `unique_together` em `Subatividade`.
- T-1.11: adicionada constraint `valor_mobilizado_positive` em `Mobilizados`, preservando `unique_together` existente.

### Validacoes executadas
- Verificacao previa de duplicidades e violacoes de constraints no banco local: zero ocorrencias bloqueantes.
- `python manage.py makemigrations ieb`: gerou a migration `0033_alter_contratos_valor_total_and_more.py`.
- `python manage.py migrate ieb`: aplicou a migration com sucesso.
- `python manage.py check`: sem issues.
- `python manage.py makemigrations ieb --check --dry-run`: sem mudancas pendentes no app `ieb`.
- `curl -I http://localhost/ieb/atividade_registro/v2/`: HTTP 200.

### Observacoes
- A checagem global `makemigrations --check --dry-run` apontou mudanca pendente no app externo `upload` do GeoNode instalado em `/usr/local/lib/python3.10/dist-packages/geonode/upload`; isso nao pertence ao app `ieb` nem foi alterado nesta onda.
- Os avisos sobre suporte futuro ao Python 3.10 vieram de `google.api_core` e nao bloquearam as validacoes.

