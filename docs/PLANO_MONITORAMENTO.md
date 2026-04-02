# Plano: Estrutura de Coleta, Metas e Indicadores por Projetos

## Contexto

Evolução do sistema de monitoramento para refletir a estrutura real da instituição:
- **Programas** = áreas temáticas internas que agrupam projetos por tema (NÃO confundir com `AreaTematica`, que classifica Atividades — Programa agrupa Projetos estrategicamente)
- **Projetos** = unidade central de monitoramento — têm Financiadores, Indicadores, Metas e Registros de execução
- **Sub-projetos** = Projetos menores dentro de um Projeto maior, executados por outras organizações
- **Indicadores** = catalogados com `ProjetoIndicador` (existente), classificáveis por origem/tipo

---

## Diagnóstico dos problemas atuais

### Bugs ativos em produção (sem migração)

**Bug A: `form.save()` chamado duas vezes** (views.py linhas ~815 e ~1005)
```python
atividade_registro = form.save()   # ← linha 815 — save correto
# ... 190 linhas de processamento ...
atividade_registro = form.save()   # ← linha 1005 — segundo save desnecessário → 2 INSERTs
```

**Bug B: `Plano.objects.create(atividade_registro=...)` inexistente** (views.py ~linha 947)
```python
Plano.objects.create(atividade_registro=atividade_registro, **planos_data)
# ← Model Plano (models.py:567) NÃO tem campo atividade_registro
# O vínculo correto é via Planos (plural) → M2M para Plano
```

**Bug C: múltiplos indicadores do mesmo tipo se sobrescrevem**
```python
# Se a atividade tiver dois indicadores tipo 'treinados':
treinados_data = {}  # ← dict único para todos
# iteração 1: treinados_data = {'total_pessoas': 30, ...}
# iteração 2: treinados_data = {'total_pessoas': 15, ...}  # ← sobrescreve!
Treinados.objects.create(**treinados_data)  # ← cria apenas 1 registro, com dados da iteração 2
```

**Bug D: `indicador_id` descartado — sem vínculo execução-planejamento**
```python
indicador = Indicador.objects.get(id=indicador_id)   # ← lido
Treinados.objects.create(atividade_registro=ar, **data)  # ← indicador perdido
```
Consequência: impossível saber qual Indicador originou cada registro. Impossível calcular `realizado vs. meta`.

### Problemas estruturais

1. **Sem camada Programa** — não existe entidade para agrupar projetos por área de atuação da instituição
2. **Projeto sem Financiadores nem auto-referência** — isolado, sem suporte a co-financiamento ou sub-projetos
3. **ProjetoIndicador subutilizado** — existe (models.py:180) mas não é usado no `load_indicadores`
4. **Meta nunca criada via interface** — `Meta` (models.py:298) existe mas nenhum formulário a cria
5. **Sem transação atômica** — `_atividade_registro_process` cria 1+13 objects sem `transaction.atomic()`

---

## Nova estrutura de dados

### Hierarquia
```
Instituição
  ├── Programa (área temática) [NOVO]
  │     └── agrupa → Projetos [ManyToMany]
  │
  └── Financiador (existente)
        └── apoia → Projetos [ManyToMany — co-financiamento]
                ↓
             Projeto  [EXPANDE: projeto_pai para sub-projetos]
                ↓
          ProjetoIndicador [existente — vínculo canônico Projeto↔Indicador]
                ↓
          Componente > Atividade > Subatividade
               ↓ planejamento         ↓ execução
            Meta                 AtividadeRegistro
      (Atividade + Indicador       Treinados / AreaDireto / etc.
       + base + meta + data)       + FK para Indicador ← FIX
```

### Indicadores disponíveis para uma Atividade
```
= Indicadores vinculados ao Projeto via ProjetoIndicador (já existe)
  FILTRADO pelos que têm Meta definida para a Atividade selecionada
```
> **Nota:** Usar `ProjetoIndicador` como mecanismo canônico — não criar `Indicador.financiador`.
> Para classificar a origem de um indicador (institucional vs. exigido por financiador), usar campo `Indicador.reporte` (já existe) ou adicionar `Indicador.escopo` como metadado separado — não misturar com Financiador.

---

## Mudanças nos models

### A. Novo model `Programa` (área temática — NÃO é `AreaTematica`)
```python
# AreaTematica (existente, lines 195-204): classifica Atividades individualmente
# Programa (NOVO): agrupa Projetos estrategicamente na instituição

class Programa(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return self.sigla
```

### B. Expansões em `Projeto`
```python
class Projeto(models.Model):
    nome = models.CharField(max_length=255)
    nome_fant = models.CharField(max_length=255)

    # NOVO: área temática institucional
    programas = models.ManyToManyField(
        'Programa', related_name='projetos', blank=True
    )
    # NOVO: financiadores (co-financiamento)
    financiadores = models.ManyToManyField(
        Financiador, related_name='projetos', blank=True
    )
    # NOVO: sub-projeto (auto-referência — profundidade máxima: 2 níveis)
    projeto_pai = models.ForeignKey(
        'self', on_delete=models.SET_NULL,   # ← SET_NULL: não excluir filhos com pai
        null=True, blank=True,
        related_name='subprojetos'
    )
```

### C. FK `indicador` nos 13 models de indicador (bug fix D)
Todos os 13 models já têm `atividade_registro = FK(AtividadeRegistro)` — esse campo permanece.
Adicionar **apenas**:

```python
# Em Treinados, AreaRestrito, AreaDireto, AreaGeral, Leis, Capacitados,
# Aplicacao, Planos, Parcerias, Mobilizados, Produtos, Contratos, AtividadeRegistroModelo:
indicador = models.ForeignKey(
    Indicador, on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='registros_%(class)s'
)
```

E adicionar restrição de unicidade nos models simples (onde faz sentido ter 1 por indicador por registro):
```python
class Meta:
    unique_together = ('atividade_registro', 'indicador')
```

### D. Propriedades em `Meta` para calcular progresso
```python
class Meta(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    base = models.FloatField()
    meta = models.FloatField()
    data = models.DateField()

    @property
    def realizado(self):
        """Uso pontual (detalhe de uma Meta). Para listagens, usar anotação na queryset."""
        from django.db.models import Sum, Count
        registros = AtividadeRegistro.objects.filter(atividade=self.atividade)
        tipo = self.indicador.tipo
        # Sum para tipos numéricos:
        SUM_MAP = {
            'treinados':     (Treinados,    'total_pessoas'),
            'area_restrito': (AreaRestrito, 'area_em_ha'),
            'area_direto':   (AreaDireto,   'total_area'),
            'area_geral':    (AreaGeral,    'total_area'),
            'leis_politicas':(Leis,         'total_leis'),
            'capacitados':   (Capacitados,  'total_organizacoes'),
            'aplicacao':     (Aplicacao,    'total_pessoas'),
            'planos':        (Planos,       'total_planos'),
            'parcerias':     (Parcerias,    'total_parcerias'),
            'mobilizados':   (Mobilizados,  'valor_mobilizado'),
            'produtos':      (Produtos,     'total_produtos'),
        }
        # Count para tipos que medem número de registros:
        COUNT_MAP = {
            'contratos': Contratos,
        }
        if tipo in SUM_MAP:
            Model, field = SUM_MAP[tipo]
            result = Model.objects.filter(
                atividade_registro__in=registros, indicador=self.indicador
            ).aggregate(total=Sum(field))
            return result['total'] or 0
        elif tipo in COUNT_MAP:
            return COUNT_MAP[tipo].objects.filter(
                atividade_registro__in=registros, indicador=self.indicador
            ).count()
        return 0  # tipo 'outro': sem métrica padrão

    @property
    def percentual(self):
        return round((self.realizado / self.meta) * 100, 1) if self.meta else 0
```

---

## Mudanças em views.py

### Correções de bugs (Bugs A, B, C, D)

**Bug A — remover segundo `form.save()`:**
```python
# Substituído por: email_org = form.cleaned_data.get('email_organizacao')
```

**Bug B — criar Planos via model correto:**
```python
# Substituir Plano.objects.create(atividade_registro=...) por:
inst = Planos(atividade_registro=atividade_registro)
inst.save()
inst.planos.set(data['planos'])
inst.save()  # Planos.save() auto-atualiza total_planos
```

**Bug C — reestruturar loop para dict por indicador:**
```python
treinados_map = {}  # {indicador_id: {...}}  em vez de treinados_data = {} (compartilhado)
# Cada map.values() vira um create separado
```

**Adicionar `transaction.atomic()`:**
```python
from django.db import transaction

with transaction.atomic():
    atividade_registro = form.save()
    # ... criação de fotos, listas, indicadores ...
# email notification fora do bloco (efeito colateral)
```

### `load_indicadores` — usar ProjetoIndicador como filtro canônico
```python
def load_indicadores(request):
    atividade_id = request.GET.get('atividade')
    projeto_id = request.GET.get('projeto')

    # Indicadores vinculados ao projeto (ProjetoIndicador é o mecanismo canônico)
    qs = Indicador.objects.all()
    if projeto_id:
        qs = qs.filter(projeto_indicadores__projeto_id=projeto_id)
    # Apenas os que têm Meta definida para esta atividade
    if atividade_id:
        qs = qs.filter(meta__atividade_id=atividade_id)

    data = [{'id': i.id, 'nome': i.nome, 'tipo': i.tipo} for i in qs.distinct()]
    return JsonResponse(data, safe=False)
```

---

## Mudanças estruturais no formulário v2

### Análise do estado atual

O formulário v2 tem 3 etapas:
- **Etapa 1 (Identificação):** Projeto → Componente → Atividade → Subatividade → Equipe → Datas → Local
- **Etapa 2 (Detalhamento):** Descrição, fotos, listas de presença, campos narrativos, equipe adicional
- **Etapa 3 (Indicadores):** Cards dinâmicos por indicador + email de notificação

**Fluxo de dados atual:**
```
1. Usuário seleciona Atividade
2. JS faz: fetch(`${urlIndicadores}?atividade=${atividadeId}&projeto=${projetoId}`)
3. Backend retorna indicadores filtrados por ProjetoIndicador + Meta da atividade
4. JS combina com indicadoresConfig (JSON embutido no template) e renderiza cards
5. Campos gerados: indicadores_{id}_{field_name}
```

### O que NÃO muda estruturalmente no formulário
- Etapas e navegação entre etapas — intactas
- Renderização de indicadores via `renderIndicador()` — intacta (já suporta múltiplos cards por tipo)
- Nomes de campos (`indicadores_{id}_{field_name}`) — intactos após correção do loop na view
- Upload de fotos e listas de presença — intactos

---

## Plano de Implementação

### Fase 0 — Bug fixes (sem migração de schema) ✅ CONCLUÍDA
**Arquivo:** `views.py`, `script_v2.js`
- [x] Remover segundo `form.save()` (Bug A)
- [x] Corrigir `Plano.objects.create()` para usar `Planos` (Bug B)
- [x] Reestruturar loop para dict-por-indicador (Bug C)
- [x] Adicionar `transaction.atomic()` em `_atividade_registro_process`
- [x] Passar `projeto_id` no fetch de `load_indicadores` (script_v2.js)

### Fase 1 — Programa + expansões em Projeto ✅ CONCLUÍDA
**Arquivos:** `models.py`, `admin.py`, migration `0022_...`
- [x] Criar model `Programa`
- [x] Adicionar `programas`, `financiadores`, `projeto_pai` em `Projeto`
- [x] Atualizar `__str__` de `Projeto` para exibir contexto de sub-projetos
- [x] Admin: `ProgramaAdmin`; `ProjetoAdmin` com filter_horizontal e SubprojetoInline
- [x] `makemigrations ieb && migrate`

### Fase 2 — FK indicador nos 13 models + data migration ✅ CONCLUÍDA
**Arquivos:** `models.py`, `views.py`, migrations `0023_...` e `0024_backfill_indicador_fk`
- [x] Adicionar `indicador = FK(Indicador, null=True)` nos 13 models (`related_name='+'`)
- [x] `unique_together = ('atividade_registro', 'indicador')` em `AreaRestrito`
- [x] Corrigir `_atividade_registro_process` para passar `indicador=ind` em cada create (Bug D)
- [x] Adicionar `indicadores_por_id` no loop de POST para rastrear objetos Indicador
- [x] Corrigir `load_indicadores` para usar `ProjetoIndicador` como filtro canônico
- [x] Data migration `0024`: inferência automática de `indicador` para registros históricos (1 candidato → associa; ambíguo → NULL)
- [x] `makemigrations ieb && migrate`

### Fase 3 — Meta funcional ✅ CONCLUÍDA
**Arquivos:** `models.py`, `admin.py`
- [x] Adicionar `realizado` e `percentual` em `Meta`
- [x] Verificar que `MetaInline` no `AtividadeAdmin` cria Metas corretamente (já estava OK)
- [x] `MetaAdmin` com colunas `realizado` e `%` na listagem do admin

### Fase 4 — Dashboard de monitoramento ✅ CONCLUÍDA
**Arquivos:** `views.py`, `urls.py`, `templates/`, `static/ieb/css/monitoramento.css`
- [x] `monitoramento_registros_view` — listagem com filtros (programa, projeto, data) → `/monitoramento/registros/`
- [x] `monitoramento_metas_view` — metas por projeto com realizado/meta/% → `/monitoramento/metas/`
- [x] Templates `monitoramento_registros.html` e `monitoramento_metas.html`
- [x] CSS `monitoramento.css` com barra de progresso colorida (verde ≥100% / laranja ≥60% / vermelho <60%)

### Fase 5 — Limpeza técnica ✅ CONCLUÍDA
**Arquivos:** `models.py`, `admin.py`, `views.py`, `settings.py`, `.env`, migration `0025_...`
- [x] Remover `AtividadeRegistro.fotos`, `.fotos_thumbnail`, `.lista_presenca` + override `save()` de thumbnail
- [x] Remover `AtividadeRegistroEquipe` (duplicata de `equipe_adicional` M2M — nunca usado em views/templates)
- [x] `MONITORING_EMAIL` em `settings.py` via `os.getenv()` + entrada em `.env`
- [x] Migration `0025_remove_campos_legados.py`

---

## Arquivos críticos

| Arquivo | Mudanças |
|---|---|
| `src/ieb/models.py` | `Programa` (novo), expansões em `Projeto` (programas, financiadores, projeto_pai + `__str__`), FK `indicador` nos 13 models, propriedades em `Meta` |
| `src/ieb/admin.py` | `ProgramaAdmin`, atualizar `ProjetoAdmin` e `IndicadorAdmin` |
| `src/ieb/views.py` | Bugs A/B/C/D + transaction.atomic + `load_indicadores` com `ProjetoIndicador` + aceitar `projeto` como parâmetro |
| `src/terralab_v2/static/ieb/js/script_v2.js` | Passar `projeto_id` no fetch de `load_indicadores` |
| `src/ieb/urls.py` | Endpoints de dashboard/listagem |
| `src/ieb/migrations/` | Migrations + data migration para registros históricos |

---

## Verificação

```bash
# Fase 0: testar formulário v2 após correção dos bugs
# → submeter com 2 indicadores do mesmo tipo; verificar que 2 records são criados

# Migrations sem erros
docker compose exec django python manage.py makemigrations ieb --dry-run

# Admin: criar Programa → associar a Projetos
# Admin: associar Financiadores a Projetos
# Admin: configurar ProjetoIndicador (quais indicadores cada projeto usa)
# Admin: criar Meta em Atividade (Indicador + base + meta)

# Preencher formulário v2 → selecionar indicador → submeter
# Shell: Treinados.objects.last().indicador  → deve retornar o Indicador correto (não None)
# Shell: Meta.objects.first().realizado      → soma dos valores coletados
# Shell: Meta.objects.first().percentual     → % de cumprimento
```
