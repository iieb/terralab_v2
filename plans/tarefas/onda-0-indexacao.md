# Onda 0 -- Indexacao e Levantamento

> **Pre-requisito:** Nenhum. Executar ANTES de todas as outras ondas.
> **Paralelismo:** As 3 tarefas sao 100% paralelas.
> **Objetivo:** Produzir mapa completo do codigo para orientar todas as tarefas seguintes.

---

## T-0.1: Indexar `models.py` -- mapear estrutura completa

### Escopo
Ler `src/ieb/models.py` inteiro e catalogar toda a estrutura.

### Arquivo alvo
- `src/ieb/models.py`

### O que catalogar
1. Todas as classes de model (nome, heranca, linha de inicio)
2. Todos os campos de cada model (nome, tipo, null/blank, default, FK/M2M targets, related_name)
3. Todos os `unique_together` existentes
4. Todos os `choices` definidos (INDICADOR_TIPO_CHOICES, FOCO_CHOICES, SCORE_PLANO, etc.)
5. Todos os metodos `save()` customizados
6. Todos os metodos de propriedade (`@property`) como `realizado`, `percentual`
7. Classes Meta internas com `ordering`, `verbose_name`, etc.
8. Todos os `related_name='+'` (FKs sem navegacao reversa)

### Resultado esperado
Lista estruturada (pode ser em texto ou tabela markdown) com:
```
Model: Pessoas (linha 742)
  Fields:
    atividade_registro = FK(AtividadeRegistro, CASCADE)
    indicador = FK(Indicador, SET_NULL, null=True, related_name='+')
    indicador_financiador = FK(IndicadorFinanciador, SET_NULL, null=True, related_name='+')
    total_pessoas = PositiveIntegerField(default=0)
    ...
  Meta:
    unique_together = ('atividade_registro', 'indicador')
  Methods:
    save() - recalcula totais
```

### Verificacao
- Nenhum model foi esquecido
- Todos os FKs com `related_name='+'` foram identificados
- Todos os `save()` com logica de recalculo foram mapeados

### Dependencias
Nenhuma.

---

## T-0.2: Indexar `views.py` -- mapear referencias a models

### Escopo
Ler `src/ieb/views.py` e catalogar como os models sao usados.

### Arquivo alvo
- `src/ieb/views.py`

### O que catalogar
1. Todos os imports de models
2. Bloco `DESAG_FIELDS` (mapeamento de campos de desagregacao)
3. Funcao `load_indicadores` -- o que retorna e como monta o JSON
4. Funcao `_atividade_registro_process` -- blocos de processamento por tipo de indicador
5. Dicionario `indicadores_config` -- configuracao de cada tipo
6. Funcao `atividade_registro_detail` -- queries de satelites por tipo
7. Funcoes `atualizar_situacao_lei` e `atualizar_situacao_plano` -- como criam historico
8. Qualquer referencia a `Outro`, `Planos` com `indicador_financiador`, `Rede`

### Resultado esperado
Mapa de:
- Quais views usam quais models
- Quais tipos de indicador sao processados e em quais linhas
- Quais tipos tem lacunas (ex: planos sem suporte a financiador)

### Verificacao
- Todos os tipos de INDICADOR_TIPO_CHOICES aparecem no processamento
- Gaps identificados (ex: tipo 'outro' sem uso real, planos sem financiador)

### Dependencias
Nenhuma (paralelo com T-0.1 e T-0.3).

---

## T-0.3: Indexar `admin.py` -- mapear registros e inlines

### Escopo
Ler `src/ieb/admin.py` e catalogar todos os registros no admin.

### Arquivo alvo
- `src/ieb/admin.py`

### O que catalogar
1. Todos os `admin.site.register` (model, admin_class)
2. Todos os `TabularInline` / `StackedInline` (model pai, model inline)
3. Fieldsets customizados (especialmente `IndicadorAdmin`)
4. `list_display`, `list_filter`, `search_fields` relevantes
5. Qualquer `raw_id_fields` ou `autocomplete_fields`
6. Verificar se `Outro` esta registrado

### Resultado esperado
Tabela:
```
Model          | AdminClass          | Inlines | Notas
Indicador      | IndicadorAdmin      | -       | fieldsets com desag_*
Pessoas        | (inline?)           | -       | verificar
...
```

### Verificacao
- Todos os models satelites estao registrados (ou sao inline)
- `Outro` esta (ou nao) registrado -- impacta T-4.6

### Dependencias
Nenhuma (paralelo com T-0.1 e T-0.2).
