# Onda 2 -- Constraints Estruturais nos Satelites

> **Pre-requisito:** Onda 0 e Onda 1 concluidas.
> **Paralelismo:** Sequencial obrigatorio. T-2.1 habilita T-2.2. T-2.3 e T-2.4 dependem de T-2.2.
> **Complexidade:** Media (T-2.2) a Baixa (T-2.1, T-2.3, T-2.4).
> **Revisado:** 2026-04-27 — correcoes C2, A3, M1 aplicadas.

---

## T-2.1: P2.4 -- Substituir `related_name='+'` por nomes explicitos

### Referencia no plano
P2.4 do Plano Cirurgico v1.3

### Problema
Todos os 24 FKs com `related_name='+'` impedem navegacao reversa. Nao e possivel fazer `indicador.pessoas_set.all()`.

### Arquivo
- `src/ieb/models.py` -- todos os FKs `indicador` e `indicador_financiador` nos models satelites

### Models afetados (16 satelites)
Pessoas, Organizacoes, Area, AreasProtegidas, Evento, Rede, PequenoProjeto, Fundo, Outro, Leis, Parcerias, Planos, Produtos, Contratos, Mobilizados, AtividadeRegistroModelo

### Alteracao
Cada model satelite tem 2 FKs. Trocar `related_name='+'` por:

```python
# ANTES:
indicador = models.ForeignKey(Indicador, SET_NULL, null=True, blank=True, related_name='+')
indicador_financiador = models.ForeignKey(IndicadorFinanciador, SET_NULL, null=True, blank=True, related_name='+')

# DEPOIS:
indicador = models.ForeignKey(Indicador, SET_NULL, null=True, blank=True, related_name='%(class)s_set')
indicador_financiador = models.ForeignKey(IndicadorFinanciador, SET_NULL, null=True, blank=True, related_name='%(class)s_fin_set')
```

### Nota sobre `%(class)s`
Django resolve `%(class)s` para o nome do model em minusculo. Exemplo:
- Em `Pessoas`: `related_name='pessoas_set'` e `related_name='pessoas_fin_set'`
- Em `Area`: `related_name='area_set'` e `related_name='area_fin_set'`

### Migration
```python
# 24x AlterField (um para cada FK em cada model)
operations = [
    migrations.AlterField('pessoas', 'indicador', field=...),
    migrations.AlterField('pessoas', 'indicador_financiador', field=...),
    migrations.AlterField('organizacoes', 'indicador', field=...),
    # ... (repetir para todos os 16 models)
]
```

### Verificacao
```python
ind = Indicador.objects.first()
ind.pessoas_set.all()  # Deve funcionar (antes dava erro)

fin = IndicadorFinanciador.objects.first()
fin.pessoas_fin_set.all()  # Deve funcionar
```

### Por que antes de T-2.2?
Facilita queries reversas durante implementacao das UniqueConstraint.

### Dependencias
Onda 1 concluida.

---

## T-2.2: P0.2 + P0.3 -- `UniqueConstraint` condicionais + `CheckConstraint` em TODOS os satelites

### Referencia no plano
P0.2 + P0.3 do Plano Cirurgico v1.3

### Problema
1. `unique_together = ('atividade_registro', 'indicador')` nao cobre `indicador_financiador`
2. Tecnicamente possivel preencher ambos os FKs ou nenhum
3. Possivel criar registros duplicados para `indicador_financiador`

### Arquivo
- `src/ieb/models.py` -- 16 classes satelites

### Models afetados -- divididos em dois grupos

**Grupo A (12 models COM `unique_together` existente):**
Pessoas, Organizacoes, Area, AreasProtegidas, Evento, Leis, Parcerias, Produtos, Contratos, Mobilizados, Outro, Planos

Estes models possuem `unique_together = ('atividade_registro', 'indicador')` no `class Meta`. E preciso remover o `unique_together` ANTES de adicionar as novas constraints.

**Grupo B (4 models SEM `unique_together`):**
Rede, PequenoProjeto, Fundo, AtividadeRegistroModelo

Estes models NAO possuem `unique_together`. Basta adicionar as constraints diretamente.

### Alteracao -- padrao de constraints (aplicar a TODOS os 16 models)

```python
class Pessoas(models.Model):  # ou qualquer model satelite
    # ... campos existentes ...

    class Meta:
        # Grupo A ONLY: REMOVER a linha abaixo:
        # unique_together = ('atividade_registro', 'indicador')
        constraints = [
            # No maximo um FK preenchido (nunca ambos)
            models.CheckConstraint(
                check=~models.Q(
                    indicador__isnull=False,
                    indicador_financiador__isnull=False,
                ),
                name='%(class)s_single_fk',
            ),
            # Unicidade para indicador IEB
            models.UniqueConstraint(
                fields=['atividade_registro', 'indicador'],
                condition=models.Q(indicador__isnull=False),
                name='%(class)s_unique_indicador',
            ),
            # Unicidade para indicador financiador
            models.UniqueConstraint(
                fields=['atividade_registro', 'indicador_financiador'],
                condition=models.Q(indicador_financiador__isnull=False),
                name='%(class)s_unique_ind_fin',
            ),
        ]
```

### Migration

A migration deve tratar os dois grupos separadamente:

```python
operations = [
    # Grupo A (12 models): remover unique_together ANTES das novas constraints
    migrations.AlterUniqueTogether('pessoas', set()),
    migrations.AlterUniqueTogether('organizacoes', set()),
    migrations.AlterUniqueTogether('area', set()),
    migrations.AlterUniqueTogether('areasprotegidas', set()),
    migrations.AlterUniqueTogether('evento', set()),
    migrations.AlterUniqueTogether('leis', set()),
    migrations.AlterUniqueTogether('parcerias', set()),
    migrations.AlterUniqueTogether('produtos', set()),
    migrations.AlterUniqueTogether('contratos', set()),
    migrations.AlterUniqueTogether('mobilizados', set()),
    migrations.AlterUniqueTogether('outro', set()),
    migrations.AlterUniqueTogether('planos', set()),

    # Todos os 16 models: adicionar 3 constraints cada
    migrations.AddConstraint('pessoas', models.CheckConstraint(..., name='pessoas_single_fk')),
    migrations.AddConstraint('pessoas', models.UniqueConstraint(..., name='pessoas_unique_indicador')),
    migrations.AddConstraint('pessoas', models.UniqueConstraint(..., name='pessoas_unique_ind_fin')),
    # ... repetir para os 16 models
]
```

### Resumo das operacoes por grupo
| Grupo | Models | Operacoes |
|-------|--------|-----------|
| A | 12 models com `unique_together` | 1x `AlterUniqueTogether(model, set())` + 3x `AddConstraint` = 48 ops |
| B | 4 models sem `unique_together` | 3x `AddConstraint` = 12 ops |
| **Total** | **16 models** | **60 operacoes** |

### Atencao
- Verificar se existem registros que violam as constraints antes de aplicar
- Criar data migration de limpeza se necessario
- O `%(class)s` nos nomes das constraints e resolvido automaticamente pelo Django
- **Grupo A:** A remocao do `unique_together` DEVE vir ANTES das `AddConstraint` na migration
- **Grupo B:** NAO tentar remover `unique_together`, pois ele nao existe nestes models

### Verificacao
```python
# Mesmo indicador + mesma atividade -> IntegrityError
Pessoas.objects.create(atividade_registro=ar, indicador=ind)
Pessoas.objects.create(atividade_registro=ar, indicador=ind)  # ERRO

# Ambos FKs preenchidos -> IntegrityError
Pessoas(atividade_registro=ar, indicador=ind, indicador_financiador=fin).save()  # ERRO

# Ambos FKs nulos -> OK (permitido, registro generico)
Pessoas(atividade_registro=ar).save()  # OK

# Indicadores diferentes do mesmo tipo -> OK
Pessoas(atividade_registro=ar, indicador=ind1)
Pessoas(atividade_registro=ar, indicador_financiador=fin1)  # OK (FK diferente)
```

### Dependencias
T-2.1 (related_name explicito facilita queries de verificacao).

---

## T-2.3: P0.6 -- Constraints de validacao em `Pessoas`

### Referencia no plano
P0.6 do Plano Cirurgico v1.3

### Problema
Sem validacao de que `homens + mulheres == total_pessoas` quando ambos preenchidos.

### Arquivo
- `src/ieb/models.py` -- classe `Pessoas` (~linha 742-761)

### Alteracao

1. Adicionar `CheckConstraint` para cada subgrupo:
```python
constraints = [
    # ... constraints de T-2.2 ...
    models.CheckConstraint(
        check=models.Q(homens__lte=models.F('total_pessoas')) | models.Q(homens__isnull=True),
        name='pessoas_homens_lte_total',
    ),
    models.CheckConstraint(
        check=models.Q(mulheres__lte=models.F('total_pessoas')) | models.Q(mulheres__isnull=True),
        name='pessoas_mulheres_lte_total',
    ),
]
```

2. Adicionar metodo `clean()`:
```python
def clean(self):
    super().clean()
    if self.homens is not None and self.mulheres is not None:
        if self.homens + self.mulheres > (self.total_pessoas or 0):
            raise ValidationError('homens + mulheres nao pode exceder total_pessoas')
```

### Migration
```python
operations = [
    migrations.AddConstraint('pessoas', CheckConstraint(..., name='pessoas_homens_lte_total')),
    migrations.AddConstraint('pessoas', CheckConstraint(..., name='pessoas_mulheres_lte_total')),
]
```

### Verificacao
```python
Pessoas(total_pessoas=10, homens=15).save()  # IntegrityError
Pessoas(total_pessoas=10, homens=5, mulheres=8).clean()  # ValidationError (5+8=13 > 10)
Pessoas(total_pessoas=10, homens=4, mulheres=6).save()  # OK
Pessoas(total_pessoas=0, homens=None).save()  # OK (NULL permitido no Postgres)
Pessoas(total_pessoas=0, homens=1).save()  # IntegrityError
```

### Dependencias
T-2.2 (constraints base ja aplicadas).

---

## T-2.4: P0.7 -- Constraints em `Organizacoes` + campo `org_governo`

### Referencia no plano
P0.7 do Plano Cirurgico v1.3

### Problema
1. Falta campo `org_governo` (organizacoes governamentais)
2. Sem validacao de subgrupos vs total

### Arquivos
- `src/ieb/models.py` -- classe `Organizacoes` (~linha 820-835), classes `Indicador` e `IndicadorFinanciador`
- `src/ieb/views.py` -- `DESAG_FIELDS` (~linha 103-112), processamento POST organizacoes, e `indicadores_config['organizacoes']` (~linha 907-912)
- `src/ieb/admin.py` -- `IndicadorAdmin` fieldsets e `IndicadorFinanciadorAdmin` fieldsets

### Alteracao

1. **Model `Organizacoes`**: Adicionar campo:
```python
org_governo = models.PositiveIntegerField(null=True, blank=True, verbose_name='Governo')
```

2. **Model `Organizacoes`**: Adicionar constraints:
```python
constraints = [
    # ... constraints de T-2.2 ...
    models.CheckConstraint(
        check=models.Q(org_sociedade_civil__lte=models.F('total_organizacoes')) | models.Q(org_sociedade_civil__isnull=True),
        name='org_sc_lte_total',
    ),
    # ... repetir para org_indigenas, org_extrativistas, org_governo
]
```

3. **Models `Indicador` e `IndicadorFinanciador`**: Adicionar campo:
```python
desag_org_governo = models.BooleanField(default=False, verbose_name='Governo')
```

4. **Views `DESAG_FIELDS`**: `DESAG_FIELDS` e uma LISTA de strings, nao um dicionario. Adicionar a string `'desag_org_governo'`:
```python
DESAG_FIELDS = [
    'desag_homens', 'desag_mulheres', ...,
    'desag_org_sc', 'desag_org_indigenas', 'desag_org_extrativistas',
    'desag_org_governo',  # ADICIONAR
    ...
]
```

5. **Views processamento POST (organizacoes)**: Adicionar tratamento para `org_governo` no bloco de processamento de organizacoes:
```python
elif field_name == 'org_governo':
    d['org_governo'] = _int(value)
```

6. **Views `indicadores_config['organizacoes']`**: Adicionar campo na lista:
```python
{'name': 'org_governo', 'type': 'number', 'label': 'Governo', 'desag_key': 'desag_org_governo'}
```

7. **Admin `IndicadorAdmin` e `IndicadorFinanciadorAdmin`**: Adicionar `desag_org_governo` nos fieldsets de Organizacoes em ambos.

### Migration
```python
operations = [
    # Organizacoes
    migrations.AddField('organizacoes', 'org_governo', field=...),
    migrations.AddConstraint('organizacoes', ...),

    # Indicador
    migrations.AddField('indicador', 'desag_org_governo', field=...),

    # IndicadorFinanciador
    migrations.AddField('indicadorfinanciador', 'desag_org_governo', field=...),
]
```

### Verificacao
```python
Organizacoes(total_organizacoes=5, org_governo=10).save()  # IntegrityError
Organizacoes(total_organizacoes=10, org_governo=3).save()  # OK
```

### Dependencias
T-2.2 (constraints base ja aplicadas).

---

## Resultado da execução — 2026-04-27

### Status
Onda 2 concluída e validada no ambiente Docker local.

### Implementação realizada

- T-2.1: substituído `related_name='+'` por nomes reversos explícitos nos satélites cobertos pela onda.
- T-2.2: removidos `unique_together` legados dos satélites do Grupo A e adicionadas constraints condicionais nos satélites com os dois FKs (`indicador` e `indicador_financiador`).
- T-2.3: adicionadas constraints de `Pessoas` para `homens <= total_pessoas` e `mulheres <= total_pessoas`, além de `clean()` para impedir `homens + mulheres > total_pessoas`.
- T-2.4: adicionado suporte a `org_governo` em `Organizacoes`, `Indicador`, `IndicadorFinanciador`, `views.py` e `admin.py`.

### Observação sobre `AtividadeRegistroModelo`

Nesta onda foi alterado apenas o `related_name` de `AtividadeRegistroModelo.indicador`. As constraints satélites completas não foram aplicadas nele agora porque o model ainda não possui `indicador_financiador`; essa inclusão está prevista na Onda 4 (`T-4.7`).

### Migration

Migration gerada e aplicada:

```text
src/ieb/migrations/0034_alter_area_unique_together_and_more.py
```

A migration inclui:

- remoção dos `unique_together` legados dos satélites do Grupo A;
- campos `desag_org_governo` em `Indicador` e `IndicadorFinanciador`;
- campo `org_governo` em `Organizacoes`;
- alterações de `related_name`;
- constraints `*_single_fk`, `*_unique_indicador` e `*_unique_ind_fin`;
- constraints adicionais de `Pessoas` e `Organizacoes`.

### Validações executadas

- Verificação pré-migration de duplicidades e registros com ambos FKs preenchidos: zero bloqueios nos satélites verificados.
- `python manage.py migrate ieb`: migration aplicada com sucesso.
- `python manage.py check`: sem issues.
- `python manage.py makemigrations ieb --check --dry-run`: sem mudanças pendentes no app `ieb`.
- `curl -I http://localhost/ieb/atividade_registro/v2/`: HTTP 200.
- Testes com dados temporários em transação com rollback confirmaram:
  - `*_single_fk` bloqueia `indicador` e `indicador_financiador` preenchidos simultaneamente;
  - `pessoas_homens_lte_total` bloqueia `homens > total_pessoas`;
  - `org_governo_lte_total` bloqueia `org_governo > total_organizacoes`;
  - `Pessoas.clean()` bloqueia `homens + mulheres > total_pessoas`;
  - reverse relations `pessoas_set` e `pessoas_fin_set` existem.
- Rollback dos dados temporários confirmado: zero artefatos de teste persistidos.

