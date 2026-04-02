# Plano: Redesign do Sistema de Indicadores — Tipos + Desagregações

_Última atualização: 2026-03-17_

---

## Contexto

O `INDICADOR_TIPO_CHOICES` atual mistura tipos históricos (`treinados`, `capacitados`) com
nomes de sub-categorias específicas que deveriam ser instâncias de `Indicador`. O redesign:

- Revisa a lista de tipos para refletir a realidade do IEB, tornando-os genéricos
- Move a especificidade para o cadastro do `Indicador` via desagregações configuráveis
- Renomeia result models para refletir o tipo (não um uso específico)
- Cria novos result models para tipos que ainda não existem
- Remove models legados cujas responsabilidades são absorvidas pelos novos

**Princípio central:** o tipo define a *estrutura* do registro; o nome do `Indicador`
define o *conteúdo*. Exemplo: `tipo='pessoas'` é usado tanto para "Pessoas Treinadas"
quanto para "Pessoas Beneficiárias" — ambos usam o mesmo result model `Pessoas`, com
campos habilitados pelos `desag_*` configurados no `Indicador`.

---

## Fluxo redesenhado

```
Cadastro (admin)
  Indicador(nome='Pessoas Treinadas', tipo='pessoas',
            desag_mulheres=True, desag_homens=True, desag_jovens=True,
            desag_pct=True, desag_pct_indigenas=True)
  ↓
  ProjetoIndicador → vincula ao Projeto
  ↓
  Meta(atividade, indicador, base, meta, data)

Registro (formulário v2)
  → load_indicadores retorna {tipo, desagregacoes, tem_foco, available_plans, ...}
  → JS renderiza campos dinâmicos baseados em item.desagregacoes + item.tipo
  → POST → _atividade_registro_process → cria result record com campos preenchidos
```

---

## `INDICADOR_TIPO_CHOICES`

```python
INDICADOR_TIPO_CHOICES = [
    ('pessoas',           'Pessoas'),
    ('organizacoes',      'Organizações'),
    ('area',              'Área'),
    ('areas_protegidas',  'Áreas Protegidas'),
    ('eventos',           'Eventos'),
    ('planos',            'Planos'),
    ('parcerias',         'Parcerias'),
    ('mobilizados',       'Recursos Mobilizados'),
    ('produtos',          'Produtos'),
    ('contratos',         'Contratos'),
    ('redes',             'Redes'),
    ('pequenos_projetos', 'Pequenos Projetos'),
    ('fundos',            'Fundos'),
    ('leis_politicas',    'Leis e Políticas'),
    ('outro',             'Outro'),
]
```

---

## Referência por tipo: campos, desagregações e result model

### 1. `pessoas` — Pessoas

**Result model:** `Pessoas` (renomeado de `Treinados`)

**Campos fixos:**
```python
total_pessoas = PositiveIntegerField(default=0)  # manual — não calculado
foco          = CharField(max_length=30, choices=FOCO_CHOICES, blank=True)
               # preenchido só se Indicador.tem_foco=True
```

**Campos por desagregação (null/blank se não habilitado):**
```python
# Gênero e faixa etária
homens    = PositiveIntegerField(null=True, blank=True)  # desag_homens
mulheres  = PositiveIntegerField(null=True, blank=True)  # desag_mulheres
jovens    = PositiveIntegerField(null=True, blank=True)  # desag_jovens

# PCT — Povos e Comunidades Tradicionais (grupo habilitado por desag_pct)
pct_indigenas    = PositiveIntegerField(null=True, blank=True)  # desag_pct_indigenas
pct_extrativistas = PositiveIntegerField(null=True, blank=True) # desag_pct_extrativistas
pct_quilombolas  = PositiveIntegerField(null=True, blank=True)  # desag_pct_quilombolas
# Nota: sub-categorias de PCT são extensíveis (novos campos em migrations futuras)

# Outros
servidor_publico = PositiveIntegerField(null=True, blank=True)  # desag_servidor_publico
```

**Campos no `Indicador` / `IndicadorFinanciador`:**
```python
desag_homens           = BooleanField(default=False)
desag_mulheres         = BooleanField(default=False)
desag_jovens           = BooleanField(default=False)
desag_pct              = BooleanField(default=False, verbose_name='PCT (grupo)')
desag_pct_indigenas    = BooleanField(default=False, verbose_name='PCT — Indígenas')
desag_pct_extrativistas= BooleanField(default=False, verbose_name='PCT — Extrativistas')
desag_pct_quilombolas  = BooleanField(default=False, verbose_name='PCT — Quilombolas')
desag_servidor_publico = BooleanField(default=False, verbose_name='Servidor Público')
tem_foco               = BooleanField(default=False, verbose_name='Coletar foco da ação')
```

**SUM_MAP:** `(Pessoas, 'total_pessoas')`

---

### 2. `organizacoes` — Organizações

**Result model:** `Organizacoes` (renomeado de `Capacitados`, sem M2M de catálogo)

**Campos fixos:**
```python
total_organizacoes = PositiveIntegerField(default=0)  # manual
foco               = CharField(max_length=30, choices=FOCO_CHOICES, blank=True)
                   # preenchido só se Indicador.tem_foco=True
```

**Campos por desagregação (null/blank se não habilitado):**
```python
org_sociedade_civil = PositiveIntegerField(null=True, blank=True)  # desag_org_sc
org_indigenas       = PositiveIntegerField(null=True, blank=True)  # desag_org_indigenas
org_extrativistas   = PositiveIntegerField(null=True, blank=True)  # desag_org_extrativistas
# Nota: tipos de organização são extensíveis em migrations futuras
```

**Evolução futura (não implementar agora):** quando necessário, adicionar M2M para
`OIsLocal`, `OIsRegional` e um novo catálogo `Organizacao` genérico (para OSCs, ONGs,
órgãos governamentais) — seguindo o mesmo padrão de `AreasProtegidas` com contagem
automática.

**Campos no `Indicador`:**
```python
desag_org_sc          = BooleanField(default=False, verbose_name='Sociedade Civil')
desag_org_indigenas   = BooleanField(default=False, verbose_name='Org. Indígenas')
desag_org_extrativistas = BooleanField(default=False, verbose_name='Org. Extrativistas')
tem_foco              = BooleanField(default=False)  # compartilhado com tipo='pessoas'
```

**SUM_MAP:** `(Organizacoes, 'total_organizacoes')`

---

### 3. `area` — Área

**Result model:** `Area` (substitui `AreaRestrito` + `AreaDireto` + `AreaGeral`)

Três modos configuráveis por indicador. Cada indicador normalmente usa um único modo;
a especificidade fica no nome do `Indicador` (ex: "ha SAF plantado", "ha TIs diretas").

**Campos:**
```python
# Modo restrito — HA informado manualmente
ha_restrito = FloatField(null=True, blank=True)

# Modos direto / indireto — seleção de áreas + soma HA automática
tis  = ManyToManyField('TIs', blank=True)
ucs  = ManyToManyField('UC',  blank=True)
pas  = ManyToManyField('PA',  blank=True)
tucs = ManyToManyField('TUC', blank=True)

# Total calculado no save()
total_ha = FloatField(default=0.0, editable=False)
# save(): se ha_restrito → total_ha = ha_restrito
#         senão → sum de .area de todos os M2M selecionados
```

**Campos no `Indicador`:**
```python
desag_restrito  = BooleanField(default=False, verbose_name='Área Restrita (HA manual)')
desag_direto    = BooleanField(default=False, verbose_name='Área Direta (M2M → soma HA)')
desag_indireto  = BooleanField(default=False, verbose_name='Área Indireta (M2M → soma HA)')
# desag_ti/uc/pa/tuc compartilhados com tipo='areas_protegidas' — ver seção 4
```

**SUM_MAP:** `(Area, 'total_ha')`

---

### 4. `areas_protegidas` — Áreas Protegidas

**Result model:** `AreasProtegidas` (NOVO)

Conta **unidades** de cada tipo de área (quantas TIs, UCs, etc.) e também registra
a **área total em HA** das áreas selecionadas.

**Campos:**
```python
tis  = ManyToManyField('TIs', blank=True)
ucs  = ManyToManyField('UC',  blank=True)
pas  = ManyToManyField('PA',  blank=True)
tucs = ManyToManyField('TUC', blank=True)

# Calculados no save() via .count() e .aggregate(Sum('area'))
total_tis  = PositiveIntegerField(default=0, editable=False)
total_ucs  = PositiveIntegerField(default=0, editable=False)
total_pas  = PositiveIntegerField(default=0, editable=False)
total_tucs = PositiveIntegerField(default=0, editable=False)
total      = PositiveIntegerField(default=0, editable=False)  # soma de todos
total_ha   = FloatField(default=0.0, editable=False)          # soma das áreas em HA
```

**Campos no `Indicador` (compartilhados com `tipo='area'` modos direto/indireto):**
```python
desag_ti  = BooleanField(default=False, verbose_name='Terra Indígena (TI)')
desag_uc  = BooleanField(default=False, verbose_name='Unidade de Conservação (UC)')
desag_pa  = BooleanField(default=False, verbose_name='Projeto de Assentamento (PA)')
desag_tuc = BooleanField(default=False, verbose_name='Território de Uso Comum (TUC)')
```

**SUM_MAP:** `(AreasProtegidas, 'total')` para contagem de unidades.
Para consultas de HA, usar `total_ha` diretamente.

**Distinção com `tipo='area'`:** `areas_protegidas` conta *unidades*; `area` mede *hectares*.
São independentes e podem coexistir na mesma atividade.

---

### 5. `eventos` — Eventos

**Result model:** `Evento` (NOVO)

**Campos:**
```python
# Modalidades — null/blank se não habilitado pelo desag_*
formacoes  = PositiveIntegerField(null=True, blank=True)
seminarios = PositiveIntegerField(null=True, blank=True)
encontros  = PositiveIntegerField(null=True, blank=True)
reunioes   = PositiveIntegerField(null=True, blank=True)

# Participantes — campo opcional global (não por modalidade)
participantes = PositiveIntegerField(null=True, blank=True)

# Total calculado no save() como soma das modalidades habilitadas
total = PositiveIntegerField(default=0, editable=False)
```

**Campos no `Indicador`:**
```python
desag_formacoes   = BooleanField(default=False)
desag_seminarios  = BooleanField(default=False)
desag_encontros   = BooleanField(default=False)
desag_reunioes    = BooleanField(default=False)
desag_participantes = BooleanField(default=False, verbose_name='Registrar participantes')
```

**SUM_MAP:** `(Evento, 'total')`

---

### 6. `planos` — Planos

**Result model:** `Planos` (existente — recebe `indicador_financiador`)

Progressão medida por score de situação. **Atualização:** escala de 5 níveis.

```python
SITUACAO_CHOICES = [
    ('em desenvolvimento', 'Em Desenvolvimento'),
    ('proposto',           'Proposto'),
    ('adotado',            'Adotado'),
    ('em implementacao',   'Em Implementação'),   # NOVO
    ('implementado',       'Implementado'),
]

SCORE_PLANO = {
    'em desenvolvimento': 1,
    'proposto':           2,
    'adotado':            3,
    'em implementacao':   4,
    'implementado':       5,
}
```

`Meta.base=1`, `Meta.meta=5`. `Meta.realizado` → score do `Planos` mais recente.

O formulário exibe sempre: dropdown do catálogo `Plano` + seletor `situacao_nova`.
Sem desag_* — a especificidade fica no `Plano` selecionado.

`Planos` ganha `indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)`.

**SUM_MAP:** lógica própria de score (não entra no SUM_MAP padrão).

---

### 7. `parcerias` — Parcerias

**Result model:** `Parcerias` (existente — adicionar contagem por tipo)

**`PARCERIA_TIPO_CHOICES`:**
```python
PARCERIA_TIPO_CHOICES = [
    ('governo_federal',           'Governo Federal'),
    ('governo_estadual_municipal', 'Governo Estadual / Municipal'),
    ('osc_ong',                   'OSC / ONG'),
    ('organizacao_internacional',  'Organização Internacional'),
    ('inst_ensino',               'Instituição de Ensino'),
    ('inst_pesquisa',             'Instituição de Pesquisa'),
]
```

**Catálogo `Parceria`** — `tipo` (CharField livre existente) converte para choices:
```python
tipo = CharField(max_length=50, choices=PARCERIA_TIPO_CHOICES, blank=True)
```

**Result model `Parcerias`:**
```python
parcerias       = ManyToManyField('Parceria', related_name='parcerias')
total_parcerias = PositiveIntegerField(default=0, editable=False)

# Contagem por tipo — calculadas no save() via parcerias.filter(tipo=X).count()
total_governo_federal            = PositiveIntegerField(default=0, editable=False)
total_governo_estadual_municipal = PositiveIntegerField(default=0, editable=False)
total_osc_ong                    = PositiveIntegerField(default=0, editable=False)
total_organizacao_internacional  = PositiveIntegerField(default=0, editable=False)
total_inst_ensino                = PositiveIntegerField(default=0, editable=False)
total_inst_pesquisa              = PositiveIntegerField(default=0, editable=False)
# Nota: ao adicionar um novo tipo em PARCERIA_TIPO_CHOICES, adicionar campo correspondente aqui
```

**SUM_MAP:** `(Parcerias, 'total_parcerias')`

---

### 8. `mobilizados` — Recursos Mobilizados

**Result model:** `Mobilizados` (existente — sem mudanças)

```python
valor_mobilizado = DecimalField(max_digits=12, decimal_places=2)
tipo_apoio = CharField(choices=[...])   # adequado como está
fonte_apoio = CharField(choices=[...])  # adequado como está
```

**SUM_MAP:** `(Mobilizados, 'valor_mobilizado')`

---

### 9. `produtos` — Produtos

**Result model:** `Produtos` (existente — adicionar contagem por tipo)

**`PRODUTO_TIPO_CHOICES`:**
```python
PRODUTO_TIPO_CHOICES = [
    ('revista',          'Revista'),
    ('boletim',          'Boletim'),
    ('livro',            'Livro'),
    ('sistematizacao',   'Sistematização de Experiências'),
    ('nota_tecnica',     'Nota Técnica'),
    ('relatorio',        'Relatório'),
    ('cartilha',         'Cartilha'),
]
```

**Catálogo `Produto`** ganha campo `tipo`:
```python
class Produto(models.Model):
    nome = CharField(max_length=100)
    tipo = CharField(max_length=30, choices=PRODUTO_TIPO_CHOICES, blank=True)
```

**Result model `Produtos`:**
```python
produtos       = ManyToManyField('Produto', related_name='produtos')
total_produtos = PositiveIntegerField(default=0, editable=False)

# Contagem por tipo — calculadas no save() via produtos.filter(tipo=X).count()
total_revistas        = PositiveIntegerField(default=0, editable=False)
total_boletins        = PositiveIntegerField(default=0, editable=False)
total_livros          = PositiveIntegerField(default=0, editable=False)
total_sistematizacoes = PositiveIntegerField(default=0, editable=False)
total_notas_tecnicas  = PositiveIntegerField(default=0, editable=False)
total_relatorios      = PositiveIntegerField(default=0, editable=False)
total_cartilhas       = PositiveIntegerField(default=0, editable=False)
# Nota: ao adicionar um novo tipo em PRODUTO_TIPO_CHOICES, adicionar campo correspondente aqui
```

**SUM_MAP:** `(Produtos, 'total_produtos')`

---

### 10. `contratos` — Contratos

**Result model:** `Contratos` (existente — adicionar valor_total)

**Catálogo `Contrato`** ganha campo `valor`:
```python
class Contrato(models.Model):
    # campos existentes (numero, objeto, data_inicio, data_fim, etc.)
    valor = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                         verbose_name='Valor do contrato (R$)')
```

**Result model `Contratos`:**
```python
contratos   = ManyToManyField('Contrato', related_name='contratos_registro')
valor_total = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                           editable=False)
# valor_total calculado no save() via contratos.aggregate(Sum('valor'))['valor__sum']
# Retorna None se nenhum contrato tiver valor preenchido
```

**SUM_MAP:** `COUNT_MAP → Contratos` (contagem de registros).
`valor_total` disponível para consultas e relatórios, mas não entra no `Meta.realizado` padrão.

---

### 11. `redes` — Redes

**Result model:** `Rede` (NOVO — mais rico que contagem simples)

```python
class Rede(models.Model):
    atividade_registro    = FK(AtividadeRegistro, CASCADE)
    indicador             = FK(Indicador, SET_NULL, null=True)
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)
    nome       = CharField(max_length=255, blank=True)   # nome/referência da rede
    tipo       = CharField(max_length=50, choices=REDE_TIPO_CHOICES, blank=True)
    quantidade = PositiveIntegerField(default=1)

REDE_TIPO_CHOICES = [
    ('local',         'Local'),
    ('regional',      'Regional'),
    ('nacional',      'Nacional'),
    ('internacional', 'Internacional'),
]
```

**Nota:** cada registro de `Rede` representa uma rede específica (ou um conjunto do mesmo
tipo). Para múltiplas redes de tipos diferentes no mesmo registro de atividade, criar um
registro `Rede` por tipo/nome. O `Meta.realizado` soma `quantidade` de todos os registros.

**SUM_MAP:** `(Rede, 'quantidade')`

---

### 12. `pequenos_projetos` — Pequenos Projetos

**Result model:** `PequenoProjeto` (NOVO — mais rico que contagem simples)

```python
class PequenoProjeto(models.Model):
    atividade_registro    = FK(AtividadeRegistro, CASCADE)
    indicador             = FK(Indicador, SET_NULL, null=True)
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)
    quantidade  = PositiveIntegerField(default=0)
    tipo        = CharField(max_length=100, blank=True)
    tema        = CharField(max_length=100, blank=True)
    valor_total = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
```

**SUM_MAP:** `(PequenoProjeto, 'quantidade')`

---

### 13. `fundos` — Fundos

**Result model:** `Fundo` (NOVO)

```python
class Fundo(models.Model):
    atividade_registro    = FK(AtividadeRegistro, CASCADE)
    indicador             = FK(Indicador, SET_NULL, null=True)
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)
    quantidade  = PositiveIntegerField(default=0)
    valor_total = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    tipo        = CharField(max_length=50, choices=FUNDO_TIPO_CHOICES, blank=True)

FUNDO_TIPO_CHOICES = [
    ('publico',        'Público'),
    ('privado',        'Privado'),
    ('internacional',  'Internacional'),
    ('misto',          'Misto'),
]
```

**SUM_MAP:** `(Fundo, 'quantidade')`

---

### 14. `leis_politicas` — Leis e Políticas

**Result model:** `Leis` (existente — adicionar desagregação por situação)

Mantém M2M com catálogo `Lei`. Adiciona rastreamento de situação similar ao `Planos`.

```python
class Leis(models.Model):
    atividade_registro    = FK(AtividadeRegistro, CASCADE)
    indicador             = FK(Indicador, SET_NULL, null=True)
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)
    leis        = ManyToManyField('Lei', related_name='leis')
    total_leis  = PositiveIntegerField(default=0, editable=False)

    # Desagregação por situação — calculada no save() a partir do M2M
    total_em_desenvolvimento = PositiveIntegerField(default=0, editable=False)
    total_propostas          = PositiveIntegerField(default=0, editable=False)
    total_aprovadas          = PositiveIntegerField(default=0, editable=False)
    total_implementadas      = PositiveIntegerField(default=0, editable=False)
```

**Catálogo `Lei`** — `SITUACAO_CHOICES` já existe. `LeiHistorico` rastreia mudanças.

**SUM_MAP:** `(Leis, 'total_leis')`

---

### 15. `outro` — Outro

**Result model:** `Outro` (NOVO — sem correspondente atual)

Para indicadores sem estrutura de dados definida.

```python
class Outro(models.Model):
    atividade_registro    = FK(AtividadeRegistro, CASCADE)
    indicador             = FK(Indicador, SET_NULL, null=True)
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True)
    descricao = TextField(blank=True)
    valor     = FloatField(null=True, blank=True)
```

**SUM_MAP:** `(Outro, 'valor')` — retorna 0 se valor=None.

---

## Mapeamento de result models: antes → depois

| Tipo antigo | Tipo novo | Model antigo | Model novo | Ação |
|---|---|---|---|---|
| `treinados` | `pessoas` | `Treinados` | `Pessoas` | **RenameModel** |
| `capacitados` | `organizacoes` | `Capacitados` | `Organizacoes` | **RenameModel** + simplificar |
| `area_restrito` | `area` | `AreaRestrito` | `Area` | **Substituir** (3→1) |
| `area_direto` | `area` | `AreaDireto` | `Area` | **Substituir** (3→1) |
| `area_geral` | `area` | `AreaGeral` | `Area` | **Substituir** (3→1) |
| `aplicacao` | `pessoas` | `Aplicacao` | `Pessoas` | Migrar (Fase 5) |
| `leis_politicas` | `leis_politicas` | `Leis` | `Leis` | Manter + expandir |
| `planos` | `planos` | `Planos` | `Planos` | + `indicador_financiador` |
| `parcerias` | `parcerias` | `Parcerias` | `Parcerias` | + contagem por tipo |
| `mobilizados` | `mobilizados` | `Mobilizados` | `Mobilizados` | Sem mudanças |
| `produtos` | `produtos` | `Produtos` | `Produtos` | + tipo no catálogo |
| `contratos` | `contratos` | `Contratos` | `Contratos` | + `valor_total` |
| — | `areas_protegidas` | — | `AreasProtegidas` | **NOVO** |
| — | `eventos` | — | `Evento` | **NOVO** |
| — | `redes` | — | `Rede` | **NOVO** (enriquecido) |
| — | `pequenos_projetos` | — | `PequenoProjeto` | **NOVO** (enriquecido) |
| — | `fundos` | — | `Fundo` | **NOVO** |
| — | `outro` | — | `Outro` | **NOVO** |

**Models a remover:** `Organizacao` (catálogo M2M de `Capacitados`).

---

## `Meta.realizado` — SUM_MAP completo

```python
SUM_MAP = {
    'pessoas':           (Pessoas,        'total_pessoas'),
    'organizacoes':      (Organizacoes,   'total_organizacoes'),
    'area':              (Area,           'total_ha'),
    'areas_protegidas':  (AreasProtegidas,'total'),
    'eventos':           (Evento,         'total'),
    'redes':             (Rede,           'quantidade'),
    'pequenos_projetos': (PequenoProjeto, 'quantidade'),
    'fundos':            (Fundo,          'quantidade'),
    'leis_politicas':    (Leis,           'total_leis'),
    'parcerias':         (Parcerias,      'total_parcerias'),
    'mobilizados':       (Mobilizados,    'valor_mobilizado'),
    'produtos':          (Produtos,       'total_produtos'),
    'outro':             (Outro,          'valor'),
    # compat. histórica
    'treinados':         (Pessoas,        'total_pessoas'),
    'capacitados':       (Organizacoes,   'total_organizacoes'),
    'aplicacao':         (Pessoas,        'total_pessoas'),
}
COUNT_MAP = {
    'contratos': Contratos,
}
# tipo='planos' usa lógica própria de score (SCORE_PLANO, 5 níveis)
```

**`MetaFinanciador.realizado`** deve ser idêntico — incluindo o bloco de score de planos.

---

## Campos de desagregação em `Indicador` e `IndicadorFinanciador` — lista completa

```python
# ── Pessoas ──────────────────────────────────────────────────────────────
desag_homens            = BooleanField(default=False)
desag_mulheres          = BooleanField(default=False)
desag_jovens            = BooleanField(default=False)
desag_pct               = BooleanField(default=False, verbose_name='PCT (grupo)')
desag_pct_indigenas     = BooleanField(default=False, verbose_name='PCT — Indígenas')
desag_pct_extrativistas = BooleanField(default=False, verbose_name='PCT — Extrativistas')
desag_pct_quilombolas   = BooleanField(default=False, verbose_name='PCT — Quilombolas')
desag_servidor_publico  = BooleanField(default=False, verbose_name='Servidor Público')
tem_foco                = BooleanField(default=False, verbose_name='Coletar foco da ação')

# ── Organizações ─────────────────────────────────────────────────────────
desag_org_sc            = BooleanField(default=False, verbose_name='Sociedade Civil')
desag_org_indigenas     = BooleanField(default=False, verbose_name='Org. Indígenas')
desag_org_extrativistas = BooleanField(default=False, verbose_name='Org. Extrativistas')
# tem_foco compartilhado com Pessoas

# ── Área (modos) ──────────────────────────────────────────────────────────
desag_restrito  = BooleanField(default=False, verbose_name='Área Restrita (HA manual)')
desag_direto    = BooleanField(default=False, verbose_name='Área Direta (M2M → soma HA)')
desag_indireto  = BooleanField(default=False, verbose_name='Área Indireta (M2M → soma HA)')

# ── Área protegida (compartilhado entre tipo='area' e tipo='areas_protegidas') ──
desag_ti  = BooleanField(default=False, verbose_name='Terra Indígena (TI)')
desag_uc  = BooleanField(default=False, verbose_name='Unidade de Conservação (UC)')
desag_pa  = BooleanField(default=False, verbose_name='Projeto de Assentamento (PA)')
desag_tuc = BooleanField(default=False, verbose_name='Território de Uso Comum (TUC)')

# ── Eventos ───────────────────────────────────────────────────────────────
desag_formacoes     = BooleanField(default=False, verbose_name='Formações')
desag_seminarios    = BooleanField(default=False, verbose_name='Seminários')
desag_encontros     = BooleanField(default=False, verbose_name='Encontros')
desag_reunioes      = BooleanField(default=False, verbose_name='Reuniões')
desag_participantes = BooleanField(default=False, verbose_name='Registrar participantes')
```

---

## Admin — `IndicadorAdmin` fieldsets

```python
fieldsets = (
    (None, {'fields': ('nome', 'codigo', 'tipo', 'descricao', 'reporte')}),
    ('Desagregações — Pessoas', {
        'fields': (
            'desag_homens', 'desag_mulheres', 'desag_jovens',
            'desag_pct', 'desag_pct_indigenas', 'desag_pct_extrativistas',
            'desag_pct_quilombolas', 'desag_servidor_publico', 'tem_foco',
        ),
        'classes': ('collapse',),
    }),
    ('Desagregações — Organizações', {
        'fields': ('desag_org_sc', 'desag_org_indigenas', 'desag_org_extrativistas'),
        'classes': ('collapse',),
        'description': 'tem_foco acima também se aplica a organizações.',
    }),
    ('Desagregações — Área', {
        'fields': ('desag_restrito', 'desag_direto', 'desag_indireto'),
        'classes': ('collapse',),
    }),
    ('Seletores de Área Protegida (Área direto/indireto + Áreas Protegidas)', {
        'fields': ('desag_ti', 'desag_uc', 'desag_pa', 'desag_tuc'),
        'classes': ('collapse',),
        'description': 'Usados por tipo=area (modos direto/indireto) e tipo=areas_protegidas.',
    }),
    ('Desagregações — Eventos', {
        'fields': (
            'desag_formacoes', 'desag_seminarios',
            'desag_encontros', 'desag_reunioes', 'desag_participantes',
        ),
        'classes': ('collapse',),
    }),
)
```

---

## Fase 0 — Limpeza de registros (pré-requisito obrigatório)

```python
# Via shell Django — rodar ANTES das migrations 0029+
from ieb.models import AtividadeRegistro, Plano

AtividadeRegistro.objects.all().delete()
# Deletados em cascata: Treinados, Capacitados, Aplicacao, AreaRestrito,
# AreaDireto, AreaGeral, Planos, Parcerias, Mobilizados, Produtos,
# Contratos, Leis, AtividadeRegistroModelo

# Resetar situação dos Planos do catálogo
Plano.objects.update(situacao='em desenvolvimento')
```

**Mantidos:** `Projeto`, `Componente`, `Atividade`, `Indicador`, `IndicadorFinanciador`,
`ProjetoIndicador`, `ProjetoIndicadorFin`, `Meta`, `MetaFinanciador`, `Plano`,
`PlanoHistorico`, `Parceria`, `Produto`, `Contrato`, `Lei`.

---

## Fase 1 — `INDICADOR_TIPO_CHOICES` + `Plano` (migration 0029)

### A. Data migration de renomes

```python
Indicador.objects.filter(tipo='treinados').update(tipo='pessoas')
Indicador.objects.filter(tipo='capacitados').update(tipo='organizacoes')
Indicador.objects.filter(tipo__in=['area_restrito', 'area_direto', 'area_geral']).update(tipo='area')
IndicadorFinanciador.objects.filter(tipo='treinados').update(tipo='pessoas')
IndicadorFinanciador.objects.filter(tipo='capacitados').update(tipo='organizacoes')
IndicadorFinanciador.objects.filter(tipo__in=['area_restrito', 'area_direto', 'area_geral']).update(tipo='area')
```

### B. `Plano.TIPO_CHOICES` expandido

```python
TIPO_CHOICES = [
    ('PGTA',                   'PGTA'),
    ('Plano de Adaptação',     'Plano de Adaptação'),
    ('Plano de Manejo',        'Plano de Manejo'),
    ('Plano de Enfrentamento', 'Plano de Enfrentamento'),
    ('Plano de Diagnóstico',   'Plano de Diagnóstico'),
    ('Outro',                  'Outro'),
]
```

### C. `Plano.SITUACAO_CHOICES` — 5 níveis (atualização crítica)

```python
SITUACAO_CHOICES = [
    ('em desenvolvimento', 'Em Desenvolvimento'),
    ('proposto',           'Proposto'),
    ('adotado',            'Adotado'),
    ('em implementacao',   'Em Implementação'),  # NOVO
    ('implementado',       'Implementado'),
]
SCORE_PLANO = {
    'em desenvolvimento': 1,
    'proposto':           2,
    'adotado':            3,
    'em implementacao':   4,
    'implementado':       5,
}
# Meta.base=1, Meta.meta=5
```

---

## Fase 2 — Desagregações no `Indicador` (migration 0030)

Adicionar todos os campos `desag_*` e `tem_foco` listados na seção
"Campos de desagregação" acima em `Indicador` **e** em `IndicadorFinanciador`.

`load_indicadores` retorna o dict completo de desagregações para o JS.

---

## Fase 3 — Result models: renomes + novos + remoções (migration 0031)

### Operações na migration

```
RenameModel: Treinados       → Pessoas
RenameModel: Capacitados     → Organizacoes
DeleteModel: AreaRestrito
DeleteModel: AreaDireto
DeleteModel: AreaGeral
DeleteModel: Organizacao     (catálogo M2M legado)

CreateModel: UC, PA, TUC     (catálogos geográficos)
CreateModel: Area
CreateModel: AreasProtegidas
CreateModel: Evento
CreateModel: Rede
CreateModel: PequenoProjeto
CreateModel: Fundo
CreateModel: Outro

AddField:    Pessoas.indigenas, .quilombolas → substituídos por campos PCT
AddField:    Pessoas.pct_indigenas, .pct_extrativistas, .pct_quilombolas
AddField:    Pessoas.servidor_publico
RenameField: Pessoas.foco_treinamento → foco  (+ atualizar FOCO_CHOICES)
RemoveField: Organizacoes.organizacoes (M2M)
RemoveField: Organizacoes.total_organizacoes (recalculado)
RenameField: Organizacoes.foco_capacitacao → foco
AddField:    Organizacoes.org_sociedade_civil, .org_indigenas, .org_extrativistas
AddField:    Leis.total_em_desenvolvimento, .total_propostas, .total_aprovadas, .total_implementadas
AddField:    Planos.indicador_financiador
AddField:    Plano.ucs, .pas, .tucs (M2M)
AddField:    Contratos.valor_total
AddField:    Evento.participantes
AddField:    Produto.tipo (PRODUTO_TIPO_CHOICES)
AddField:    Produtos.total_revistas, .total_boletins, .total_livros,
             .total_sistematizacoes, .total_notas_tecnicas, .total_relatorios, .total_cartilhas
AlterField:  Parceria.tipo → CharField com PARCERIA_TIPO_CHOICES
AddField:    Parcerias.total_governo_federal, .total_governo_estadual_municipal,
             .total_osc_ong, .total_organizacao_internacional,
             .total_inst_ensino, .total_inst_pesquisa
AddField:    Contrato.valor (DecimalField null/blank)
```

---

## Fase 4 — Formulário v2 (JS + views)

### `renderIndicador` — lógica por tipo

```javascript
// tipo='pessoas'
//   → total_pessoas (sempre, manual)
//   → homens/mulheres/jovens se desag_* habilitado
//   → grupo PCT (se desag_pct): indigenas/extrativistas/quilombolas habilitados por desag_pct_*
//   → servidor_publico se desag_servidor_publico
//   → foco se tem_foco

// tipo='organizacoes'
//   → total_organizacoes (sempre, manual)
//   → org_sociedade_civil/indigenas/extrativistas se desag_org_* habilitado
//   → foco se tem_foco

// tipo='area'
//   → se desag_restrito: campo ha_restrito (manual)
//   → se desag_direto ou desag_indireto:
//       seletores M2M TI/UC/PA/TUC habilitados por desag_ti/uc/pa/tuc
//       total_ha calculado no back-end (readonly)

// tipo='areas_protegidas'
//   → seletores M2M TI/UC/PA/TUC habilitados por desag_ti/uc/pa/tuc
//   → total e total_ha calculados no back-end

// tipo='eventos'
//   → formacoes/seminarios/encontros/reunioes se desag_* habilitado
//   → participantes se desag_participantes
//   → total calculado no back-end

// tipo='planos'
//   → dropdown catálogo Plano (available_plans)
//   → seletor situacao_nova (5 opções)

// tipo='parcerias'
//   → seletor M2M catálogo Parceria (multiselect)
//   → total_parcerias calculado no back-end (readonly)

// tipo='leis_politicas'
//   → seletor M2M catálogo Lei (multiselect)
//   → total_leis + desagregação por situação calculados no back-end (readonly)

// tipo='mobilizados'
//   → valor_mobilizado (decimal, manual)
//   → tipo_apoio (choices existentes)
//   → fonte_apoio (choices existentes)

// tipo='contratos'
//   → seletor M2M catálogo Contrato (multiselect)
//   → valor_total calculado no back-end (readonly, se Contrato.valor preenchido)

// tipo='produtos'
//   → seletor M2M catálogo Produto (multiselect, filtrado por tipo se desejado)
//   → total_produtos + contagem por tipo calculados no back-end (readonly)

// tipo='redes'
//   → nome (texto), tipo (REDE_TIPO_CHOICES), quantidade

// tipo='pequenos_projetos'
//   → quantidade, tipo, tema, valor_total

// tipo='fundos'
//   → quantidade, valor_total, tipo (FUNDO_TIPO_CHOICES)

// tipo='outro'
//   → descricao (texto), valor (número)
```

---

## Fase 5 — Migrar `aplicacao` → `pessoas` (posterior)

```python
for ap in Aplicacao.objects.select_related('atividade_registro', 'indicador'):
    Pessoas.objects.create(
        atividade_registro=ap.atividade_registro,
        indicador=ap.indicador,
        total_pessoas=ap.total_pessoas,
        homens=ap.homens,
        mulheres=ap.mulheres,
        jovens=ap.jovens,
    )
Indicador.objects.filter(tipo='aplicacao').update(tipo='pessoas')
IndicadorFinanciador.objects.filter(tipo='aplicacao').update(tipo='pessoas')
# migrations.DeleteModel('Aplicacao')
```

---

## Itens pendentes (a resolver antes ou durante as migrations)

| Item | Quando |
|---|---|
| ~~Definir `PRODUTO_TIPO_CHOICES`~~ — **✓** revista, boletim, livro, sistematizacao, nota_tecnica, relatorio, cartilha | ✓ |
| ~~Padronizar `Parceria.tipo`~~ — **✓** `PARCERIA_TIPO_CHOICES` definido (6 tipos) | ✓ |
| ~~Contagem por tipo em `Parcerias` e `Produtos`~~ — **✓** campos definidos em ambos os result models | ✓ |
| ~~Campo `valor` em `Contrato` (catálogo)~~ — **✓** `DecimalField null/blank` documentado | ✓ |
| Evolução futura: M2M `Organizacoes` → `OIsLocal`/`OIsRegional`/catálogo genérico | Fase posterior |

---

## Sequência de migrations

| # | Migration | Conteúdo |
|---|---|---|
| 0029 | `_tipo_choices_rename` | `INDICADOR_TIPO_CHOICES`; data migration renomes; `Plano.TIPO_CHOICES` + `SITUACAO_CHOICES` (5 níveis) |
| 0030 | `_indicador_desagregacoes` | Todos os `desag_*` e `tem_foco` em `Indicador` e `IndicadorFinanciador` |
| 0031 | `_result_models_redesign` | Todas as operações da Fase 3 listadas acima |
| 0032 | `_aplicacao_to_pessoas` | Fase 5: migrar `Aplicacao` → `Pessoas` |

---

## Arquivos críticos

| Arquivo | Mudanças |
|---|---|
| `src/ieb/models.py` | `INDICADOR_TIPO_CHOICES`; `FOCO_CHOICES`; `SCORE_PLANO` (5 níveis); todos os `desag_*`; result models renomeados/novos; catálogos `UC/PA/TUC`; `SUM_MAP` em `Meta` e `MetaFinanciador` |
| `src/ieb/migrations/0029_*` | TIPO_CHOICES + renomes + Plano.SITUACAO_CHOICES |
| `src/ieb/migrations/0030_*` | Desag fields em Indicador |
| `src/ieb/migrations/0031_*` | Redesign completo de result models |
| `src/ieb/migrations/0032_*` | Migração Aplicacao → Pessoas |
| `src/ieb/views.py` | `load_indicadores`; `_atividade_registro_process`; `indicadores_config` |
| `src/terralab_v2/static/ieb/js/script_v2.js` | `renderIndicador` por tipo + desagregações |
| `src/ieb/admin.py` | `IndicadorAdmin` fieldsets; inlines novos models |

---

## Verificação

```bash
# Pré-requisito: Fase 0 no shell Django

docker compose exec django python manage.py makemigrations ieb --dry-run
docker compose exec django python manage.py migrate

# Pessoas com PCT
# Admin: Indicador(tipo='pessoas', desag_pct=True, desag_pct_indigenas=True)
# Formulário → grupo PCT aparece com campo pct_indigenas
# Submeter → Pessoas(total_pessoas=30, pct_indigenas=18)

# Área modo direto
# Admin: Indicador(tipo='area', desag_direto=True, desag_ti=True)
# Formulário → seletor de TIs → submeter
# Pessoas: Area(tis=[TI-A], total_ha=185000.0)

# Eventos com participantes
# Admin: Indicador(tipo='eventos', desag_formacoes=True, desag_participantes=True)
# Formulário → formacoes + participantes
# Evento(formacoes=2, participantes=45, total=2)

# Planos com 5 níveis
# Admin: Indicador(tipo='planos'), Meta(base=1, meta=5)
# Formulário → situacao_nova='em implementacao'
# Meta.realizado → 4

# Verificar MetaFinanciador.realizado para todos os tipos (incluindo planos)
```
