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

---

## Resultado executado em 2026-04-27

### T-0.1 concluida -- inventario de `src/ieb/models.py`

Arquivo lido integralmente: `src/ieb/models.py`.

#### Models por linha de inicio

| Model | Linha | Heranca | Campos | Meta / propriedades relevantes |
|---|---:|---|---:|---|
| OIsRegional | 12 | `models.Model` | 6 | - |
| OIsLocal | 24 | `models.Model` | 6 | - |
| OIRegLoc | 36 | `models.Model` | 2 | - |
| TIs | 44 | `models.Model` | 7 | - |
| Aldeia | 57 | `models.Model` | 4 | - |
| Indigena | 67 | `models.Model` | 7 | - |
| IGATI | 82 | `models.Model` | 2 | - |
| TIsIGATI | 90 | `models.Model` | 2 | - |
| Financiador | 101 | `models.Model` | 2 | `sigla` unique |
| Instituicao | 109 | `models.Model` | 2 | - |
| Equipe | 117 | `models.Model` | 4 | - |
| Programa | 128 | `models.Model` | 4 | `ordering=['sigla']` |
| Projeto | 145 | `models.Model` | 5 | M2M `programas`, `financiadores`; self-FK `projeto_pai` |
| Componente | 169 | `models.Model` | 4 | - |
| Atividade | 179 | `models.Model` | 4 | - |
| EquipeProjeto | 189 | `models.Model` | 2 | - |
| ProjetoOI | 197 | `models.Model` | 2 | - |
| ProjetoTI | 205 | `models.Model` | 2 | - |
| ProjetoIndicador | 213 | `models.Model` | 2 | `unique_together=('projeto', 'indicador')` |
| ProjetoIndicadorFin | 226 | `models.Model` | 2 | `unique_together=('projeto', 'indicador_financiador')` |
| AreaTematica | 241 | `models.Model` | 2 | verbose names |
| Subatividade | 253 | `models.Model` | 4 | FK `atividade` com `related_name='subatividades'` |
| AtividadeAreaTematica | 263 | `models.Model` | 2 | `unique_together=('atividade', 'area_tematica')` |
| AtividadeOILocal | 276 | `models.Model` | 2 | `unique_together=('atividade', 'oilocal')` |
| AtividadeOIRegional | 289 | `models.Model` | 2 | `unique_together=('atividade', 'oiregional')` |
| AtividadeTI | 302 | `models.Model` | 2 | `unique_together=('atividade', 'ti')` |
| Indicador | 344 | `models.Model` | 29 | usa `INDICADOR_TIPO_CHOICES` |
| IndicadorFinanciador | 391 | `models.Model` | 30 | verbose names; FK `financiador` |
| Meta | 445 | `models.Model` | 6 | propriedades `realizado`, `percentual` |
| MetaFinanciador | 507 | `models.Model` | 6 | propriedades `realizado`, `percentual` |
| AtividadeRegistro | 570 | `models.Model` | 16 | registro principal |
| AtividadeRegistroFoto | 593 | `models.Model` | 3 | `save()` customizado para thumbnail |
| AtividadeRegistroListaPresenca | 618 | `models.Model` | 2 | - |
| UC | 629 | `models.Model` | 2 | verbose names |
| PA | 641 | `models.Model` | 2 | verbose names |
| TUC | 653 | `models.Model` | 2 | verbose names |
| Area | 666 | `models.Model` | 9 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula `total_ha` |
| AreasProtegidas | 699 | `models.Model` | 13 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula totais |
| Pessoas | 743 | `models.Model` | 12 | `unique_together=('atividade_registro', 'indicador')` |
| Lei | 764 | `models.Model` | 3 | choices internos |
| Leis | 783 | `models.Model` | 9 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula totais |
| LeiHistorico | 810 | `models.Model` | 5 | historico de situacao |
| Organizacoes | 821 | `models.Model` | 8 | `unique_together=('atividade_registro', 'indicador')` |
| Evento | 838 | `models.Model` | 9 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula `total` |
| Rede | 868 | `models.Model` | 6 | sem `unique_together` |
| PequenoProjeto | 881 | `models.Model` | 7 | verbose names; sem `unique_together` |
| Fundo | 906 | `models.Model` | 6 | sem `unique_together` |
| Outro | 919 | `models.Model` | 5 | `unique_together=('atividade_registro', 'indicador')` |
| Plano | 934 | `models.Model` | 4 | choices internos; M2M `tis` |
| Planos | 961 | `models.Model` | 6 | `save()` cria `PlanoHistorico` e atualiza `Plano.situacao` |
| PlanoHistorico | 999 | `models.Model` | 5 | historico de plano |
| Parceria | 1019 | `models.Model` | 2 | usa `PARCERIA_TIPO_CHOICES` |
| Parcerias | 1027 | `models.Model` | 11 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula totais |
| Mobilizados | 1060 | `models.Model` | 6 | verbose names; `unique_together=('atividade_registro', 'indicador')` |
| Produto | 1101 | `models.Model` | 2 | usa `PRODUTO_TIPO_CHOICES` |
| Produtos | 1109 | `models.Model` | 12 | `unique_together=('atividade_registro', 'indicador')`; `save()` recalcula totais |
| Contrato | 1143 | `models.Model` | 4 | M2M `produtos` |
| Contratos | 1161 | `models.Model` | 5 | `unique_together=('atividade_registro', 'indicador')`; `save()` agrega `valor_total` |
| Modelo | 1180 | `models.Model` | 1 | verbose names |
| AtividadeRegistroModelo | 1190 | `models.Model` | 4 | verbose names; sem `unique_together` |
| FormacaoIndigena | 1212 | `models.Model` | 2 | - |
| CR | 1223 | `models.Model` | 2 | - |
| CTL | 1231 | `models.Model` | 3 | - |
| DSEI | 1242 | `models.Model` | 2 | - |
| Posto | 1250 | `models.Model` | 3 | - |
| Casai | 1259 | `models.Model` | 2 | - |
| Polo | 1267 | `models.Model` | 2 | - |
| AIS | 1275 | `models.Model` | 2 | - |
| Escola | 1285 | `models.Model` | 4 | - |
| Professores | 1295 | `models.Model` | 2 | - |

#### Choices e constantes globais

- `INDICADOR_TIPO_CHOICES`: linhas 317-333.
- `SCORE_PLANO`: linhas 335-341.
- `FOCO_CHOICES`: linhas 736-740.
- `REDE_TIPO_CHOICES`: linhas 861-866.
- `FUNDO_TIPO_CHOICES`: linhas 899-904.
- `PARCERIA_TIPO_CHOICES`: linhas 1010-1017.
- `PRODUTO_TIPO_CHOICES`: linhas 1091-1099.

#### `unique_together` existentes

- Vinculos de projeto/atividade: `ProjetoIndicador`, `ProjetoIndicadorFin`, `AtividadeAreaTematica`, `AtividadeOILocal`, `AtividadeOIRegional`, `AtividadeTI`.
- Satelites com `unique_together=('atividade_registro', 'indicador')`: `Area`, `AreasProtegidas`, `Pessoas`, `Leis`, `Organizacoes`, `Evento`, `Outro`, `Parcerias`, `Mobilizados`, `Produtos`, `Contratos`.
- Satelites sem `unique_together`: `Rede`, `PequenoProjeto`, `Fundo`, `AtividadeRegistroModelo`, `Planos`.

#### Campos com `related_name='+'`

- `Area.indicador`, `Area.indicador_financiador`.
- `AreasProtegidas.indicador`, `AreasProtegidas.indicador_financiador`.
- `Pessoas.indicador`, `Pessoas.indicador_financiador`.
- `Leis.indicador`, `Leis.indicador_financiador`.
- `Organizacoes.indicador`, `Organizacoes.indicador_financiador`.
- `Evento.indicador`, `Evento.indicador_financiador`.
- `Rede.indicador`, `Rede.indicador_financiador`.
- `PequenoProjeto.indicador`, `PequenoProjeto.indicador_financiador`.
- `Fundo.indicador`, `Fundo.indicador_financiador`.
- `Outro.indicador`, `Outro.indicador_financiador`.
- `Planos.indicador`, `Planos.indicador_financiador`.
- `Parcerias.indicador`, `Parcerias.indicador_financiador`.
- `Mobilizados.indicador`, `Mobilizados.indicador_financiador`.
- `Produtos.indicador`, `Produtos.indicador_financiador`.
- `Contratos.indicador`, `Contratos.indicador_financiador`.
- `AtividadeRegistroModelo.indicador`.

#### `save()` customizados

- `AtividadeRegistroFoto.save()`: cria thumbnail localmente.
- `Area.save()`: usa save inicial para obter `pk`; recalcula `total_ha` por `ha_restrito` ou M2M.
- `AreasProtegidas.save()`: usa save inicial para obter `pk`; recalcula contagens e `total_ha` por M2M.
- `Leis.save()`: recalcula contagens por situacao.
- `Evento.save()`: recalcula `total` por soma dos campos de evento.
- `Planos.save()`: registra historico e atualiza situacao do plano na criacao.
- `Parcerias.save()`: recalcula contagens por tipo.
- `Produtos.save()`: recalcula contagens por tipo.
- `Contratos.save()`: agrega soma de `Contrato.valor` em `valor_total`.

#### Propriedades calculadas

- `Meta.realizado`, `Meta.percentual`.
- `MetaFinanciador.realizado`, `MetaFinanciador.percentual`.

### T-0.2 concluida -- inventario de `src/ieb/views.py`

Arquivo lido integralmente: `src/ieb/views.py`.

#### Imports de models

O arquivo importa em bloco: `Programa`, `Projeto`, `Componente`, `Atividade`, `EquipeProjeto`, `Indicador`, `IndicadorFinanciador`, `Meta`, `MetaFinanciador`, `AtividadeRegistro`, `AtividadeRegistroFoto`, `AtividadeRegistroListaPresenca`, `Pessoas`, `Organizacoes`, `Area`, `AreasProtegidas`, `Evento`, `Rede`, `PequenoProjeto`, `Fundo`, `Outro`, `Leis`, `Planos`, `Parceria`, `Parcerias`, `Plano`, `PlanoHistorico`, `TIs`, `UC`, `PA`, `TUC`, `Produtos`, `Produto`, `Contrato`, `Contratos`, `Lei`, `LeiHistorico`, `Mobilizados`, `Modelo`, `AtividadeRegistroModelo`.

#### Funcoes e usos principais

| Funcao | Linhas | Uso principal de models |
|---|---:|---|
| `load_componentes` | 48-52 | `Componente` por projeto |
| `load_atividades` | 54-58 | `Atividade` por componente |
| `load_subatividades` | 60-65 | importa `Subatividade` localmente |
| `load_equipes`, `load_equipes_adicionais` | 67-77 | `EquipeProjeto` por projeto |
| `load_indicadores` | 80-131 | retorna indicadores base, indicadores de financiador, planos disponiveis e `DESAG_FIELDS` |
| `atividade_registro_detalhe_view` | 133-156 | consulta satelites por `AtividadeRegistro` |
| `adicionar_*` / `atualizar_*` | 162-344 | cria/atualiza `Parceria`, `Plano`, `Produto`, `Contrato`, `Lei`, `Modelo`; cria historicos de plano/lei |
| `enviar_email_notificacao` | 384-470 | consulta satelites para gerar PDF de notificacao |
| `_atividade_registro_process` | 477-1002 | processa POST por tipo de indicador e cria satelites base/financiador |
| `monitoramento_registros_view` | 1013-1046 | lista `AtividadeRegistro` filtrado |
| `monitoramento_metas_view` | 1049-1107 | lista `Meta` e `MetaFinanciador` com realizado/percentual |

#### `DESAG_FIELDS`

Definido dentro de `load_indicadores`, linhas 103-112, como lista de strings. Inclui desagregacoes de pessoas, organizacoes, area, areas protegidas e eventos. Nao inclui ainda `desag_org_governo`.

#### Processamento de indicadores em `_atividade_registro_process`

- Mapas base declarados para: pessoas, organizacoes, area, areas_protegidas, eventos, redes, pequenos_projetos, fundos, outro, planos, parcerias, produtos, contratos, leis, mobilizados, modelos.
- Mapas de financiador declarados para: pessoas, organizacoes, area, areas_protegidas, eventos, redes, pequenos_projetos, fundos, outro, parcerias, produtos, contratos, leis, mobilizados.
- Lacunas observadas:
  - `fin_planos_map` nao existe; `planos` so processa indicador base em `elif tipo == 'planos' and not is_fin`.
  - `modelos_map` e `modelos_existentes` existem no contexto, mas nao ha bloco de POST criando `AtividadeRegistroModelo` em `_atividade_registro_process`.
  - `indicadores_config` nao possui entrada `modelos`; possui `outro`.
  - Criacao de `Evento` e `Outro` usa filtros truthy (`any(v for v in data.values())`, `data.get('valor')`), o que pode ignorar valor `0` intencional.

#### `indicadores_config`

Definido nas linhas 895-994 com chaves: `pessoas`, `organizacoes`, `area`, `areas_protegidas`, `eventos`, `redes`, `pequenos_projetos`, `fundos`, `leis_politicas`, `planos`, `parcerias`, `produtos`, `contratos`, `mobilizados`, `outro`.

### T-0.3 concluida -- inventario de `src/ieb/admin.py`

Arquivo lido integralmente: `src/ieb/admin.py`.

#### Inlines

- `ProjetoIndicadorInline` -> `ProjetoIndicador`.
- `ProjetoOIInline` -> `ProjetoOI`.
- `ProjetoTIInline` -> `ProjetoTI`.
- `ComponenteInline` -> `Componente`.
- `SubatividadeInline` -> `Subatividade`.
- `MetaInline` -> `Meta`.
- `MetaFinanciadorInline` -> `MetaFinanciador`.
- `ProjetoIndicadorFinInline` -> `ProjetoIndicadorFin`.
- `IndicadorFinanciadorInline` -> `IndicadorFinanciador`.
- `AtividadeAreaTematicaInline` -> `AtividadeAreaTematica`.
- `AtividadeOILocalInline` -> `AtividadeOILocal`.
- `AtividadeOIRegionalInline` -> `AtividadeOIRegional`.
- `AtividadeTIInline` -> `AtividadeTI`.
- `SubprojetoInline` -> `Projeto` via `fk_name='projeto_pai'`.
- `PlanoHistoricoInline` -> `PlanoHistorico`.

#### Admins customizados registrados por decorator

| Model | AdminClass | Linhas | Notas |
|---|---|---:|---|
| Programa | `ProgramaAdmin` | 109-113 | `list_display`, filtro `ativo`, busca nome/sigla |
| Projeto | `ProjetoAdmin` | 116-122 | filtros por programas/financiadores; varios inlines |
| Atividade | `AtividadeAdmin` | 125-127 | inlines de subatividade, metas e vinculos territoriais |
| Subatividade | `SubatividadeAdmin` | 130-134 | lista codigo/nome/atividade |
| AreaTematica | `AreaTematicaAdmin` | 137-140 | busca por nome |
| Indicador | `IndicadorAdmin` | 143-179 | fieldsets de desagregacoes |
| Financiador | `FinanciadorAdmin` | 183-187 | inline de indicadores proprios |
| IndicadorFinanciador | `IndicadorFinanciadorAdmin` | 190-226 | fieldsets equivalentes aos de `Indicador` |
| Meta | `MetaAdmin` | 230-242 | exibe `realizado` e `%` via propriedades |
| Plano | `PlanoAdmin` | 283-289 | historico inline e `filter_horizontal=('tis',)` |
| Planos | `PlanosAdmin` | 292-296 | `raw_id_fields=('atividade_registro', 'indicador', 'plano')` |

#### Registros simples com `admin.site.register`

`Componente`, `Instituicao`, `Equipe`, `EquipeProjeto`, `ProjetoOI`, `ProjetoTI`, `ProjetoIndicador`, `ProjetoIndicadorFin`, `MetaFinanciador`, `AtividadeAreaTematica`, `AtividadeOILocal`, `AtividadeOIRegional`, `AtividadeTI`, `OIsRegional`, `OIsLocal`, `OIRegLoc`, `TIs`, `Aldeia`, `Indigena`, `FormacaoIndigena`, `IGATI`, `TIsIGATI`, `AtividadeRegistro`, `Pessoas`, `Leis`, `Lei`, `LeiHistorico`, `PlanoHistorico`, `Parcerias`, `Parceria`, `Mobilizados`, `Produtos`, `Produto`, `Contratos`, `Contrato`, `Modelo`, `AtividadeRegistroModelo`, `CR`, `CTL`, `DSEI`, `Posto`, `Casai`, `Polo`, `AIS`, `Escola`, `Professores`.

#### Verificacao sobre `Outro`

`Outro` nao esta registrado no admin e tambem nao aparece como inline. Essa confirmacao impacta a tarefa T-4.6: nao ha remocao de registro admin a fazer para `Outro` no estado atual.

