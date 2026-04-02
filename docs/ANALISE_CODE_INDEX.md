# Análise do CODE_INDEX — Resolução de Pontos Cegos e Perguntas

> **Data:** 2026-04-02  
> **Autores:** Claude Code + Eduardo Passaro Jr.  
> **Branch:** retomada  
> **Objetivo:** Completar a análise iniciada em CODE_INDEX.md com exploração profunda e esclarecimentos

---

## Contexto

O CODE_INDEX.md (gerado em 2026-04-02, branch `retomada`) listou 10 pontos cegos (seção 9) e 10 perguntas de esclarecimento (seção 10) que não podiam ser respondidas por varredura estática. Este documento registra as respostas obtidas via exploração de código e confirmação com o usuário, e lista os itens de ação resultantes.

---

## Respostas — Pontos Cegos (Seção 9)

### 1. GeoNode internals
**Status: não resolvível estaticamente** — por design, o GeoNode é instalado como pacote pip. Models, signals e middlewares do GeoNode só são visíveis com `python manage.py shell` ou leitura do pacote instalado no container.

### 2. `src/tasks.py` e `src/pavement.py`
**Resolvido.** `tasks.py` usa `invoke` para o ciclo Docker:
- `update` → gera `~/.override_env` com todas as variáveis de runtime
- `migrations` → `migrate` nas DBs `default` + `datastore`, depois `rebuild_index`
- `statics` → `collectstatic` + criação de diretórios em `/mnt/volumes/statics/`
- `fixtures` → carrega `sample_admin`, OAuth2, Sites, `initial_data.json`
- `monitoringfixture` → carrega métricas/notificações de monitoring (condicional)

`pavement.py` usa `paver` para ambiente de desenvolvimento:
- `setup_geoserver` → baixa WAR + Jetty + data dir
- `start`/`stop` → gerencia Django, GeoServer e broker
- `test`/`test_bdd`/`test_javascript`/`test_integration` → runners de teste (estrutura já existe para quando testes forem implementados)

### 3. `src/ieb/tests.py`
**Confirmado vazio.** O usuário confirmou que **testes são prioridade** — ver itens de ação.

### 4. Templates HTML
**Parcialmente resolvido.** `atividade_registro_form_v2.html`:
- Estrutura wizard de 3 etapas: Identificação → Detalhamento → Indicadores
- CSS próprio (`form_v2.css`), sem Bootstrap
- Single `<form>` encapsula todos os steps
- Bloco `<script>` inline injeta `indicadoresConfig` do contexto Django
- `script_v2.js` incluído no final

### 5. JavaScript (`script.js`, `script_v2.js`)
**Resolvido.** `script_v2.js` é o driver principal do formulário v2:
- Gerencia navegação entre steps (goToStep)
- Validação por step incluindo `data_final >= data_inicio`
- AJAX cascata: Projeto → Componentes/Equipes → Atividades → Subatividades → Indicadores
- `renderIndicador()` constrói cards dinâmicos com suporte a `number`, `text`, `select` (radios), `checkbox`, `planos` (seletor + situação)
- Validação completa antes do submit, navega ao primeiro step com erro

### 6. `django.contrib.gis`
**Revisado: import intencional — integração com camadas oficiais planejada e prioritária.** Grep por `gis_models.` retornou zero resultados atualmente, mas o import **não é legado**. Os models `UC`, `PA`, `TUC` e `TIs` serão parametrizados a partir de **camadas geográficas já existentes de fontes oficiais** (ex: FUNAI, IBAMA, INCRA, IEB) — ou seja, não haverá digitalização manual: os dados espaciais virão de shapefiles/WFS dessas fontes e serão importados/vinculados aos models. A infraestrutura já está preparada (PostgreSQL + PostGIS, GeoServer 2.24.4, django.contrib.gis via GeoNode). Campos `FloatField` de área são derivados — os polígonos virão das camadas oficiais.

### 7. Email/SMTP
**Parcialmente resolvido.** A view `enviar_email_notificacao` usa `EmailBackend` diretamente. Configuração depende de variáveis `EMAIL_*` no `.env`. Não verificável estaticamente — requer teste em ambiente com SMTP configurado.

### 8. CSRF exempt — **Vulnerabilidade confirmada**
**Resolvido.** Três views usam `@csrf_exempt`:
- `adicionar_lei` (views.py ~line 279)
- `atualizar_situacao_lei` (views.py ~line 303)
- `adicionar_modelo` (views.py ~line 331)

**Nenhuma das três tem `@login_required`.** Combinação `@csrf_exempt` + sem autenticação = qualquer requisição externa pode criar/modificar Leis e Modelos. **Usuário confirmou: corrigir.**

### 9. Autenticação nas views AJAX
**Resolvido — bug confirmado.** Apenas `load_indicadores` tem `@login_required`. As demais views (`load_componentes`, `load_atividades`, `load_subatividades`, `load_equipes`, `load_equipes_adicionais`) são publicamente acessíveis. Os formulários principais (`atividade_registro_view`, `atividade_registro_view_v2`) também não têm `@login_required`. **Usuário confirmou: foi esquecido, é um bug.**

### 10. Vagrant/Ansible
**Não analisado** — fora do escopo prioritário. Vagrant provavelmente é para desenvolvimento local, Ansible para provisionamento de servidor.

---

## Respostas — Perguntas de Esclarecimento (Seção 10)

| # | Pergunta | Resposta |
|---|---|---|
| 1 | Versão Python? | Indireta: base image `geonode/geonode-base:latest-ubuntu-22.04` → **Python 3.10** (Ubuntu 22.04 default) |
| 2 | DRF? | Não usado em `ieb` hoje — todo CRUD é via views function-based + `JsonResponse` manual, sem serializers nem ViewSets. Porém DRF já está instalado no ambiente como dependência transitiva do GeoNode 4.4.1. **Implementar DRF no `ieb` é uma prioridade**, pois viabiliza: integrações com ferramentas de análise (pandas, R, QGIS), atualizações em massa de dados (ex: importação das camadas oficiais FUNAI/IBAMA/INCRA), gestão programática via scripts e futuras integrações com dashboards ou outros sistemas. |
| 3 | Django signals? | **Nenhum signal registrado.** Toda lógica de cálculo está em 9 overrides de `save()` distribuídos pelos models de resultado. Isso funciona para operações unitárias via formulário, mas **`bulk_create`/`bulk_update` silenciosamente ignoram todos esses `save()`** — o que é crítico para a API REST (item F) e importação em massa das camadas oficiais (item D). Os 9 overrides e seus riscos: `AtividadeRegistroFoto` (geração de thumbnail), `Area` (soma `total_ha` via M2M), `AreasProtegidas` (6 contadores), `Leis` (5 contadores por situação), `Evento` (soma `total`), `Parcerias` (7 contadores por tipo), `Produtos` (8 contadores por tipo), `Contratos` (soma `valor_total`), e `Planos` — **o mais crítico**: além de calcular campos, atualiza `Plano.situacao` e cria registros de auditoria em `PlanoHistorico`. Em operações bulk, o histórico de mudanças de planos seria perdido silenciosamente. **Decisão necessária antes de implementar DRF:** mover a lógica dos `save()` para signals ou para os serializers DRF. |
| 4 | Estado dos testes? | Vazio. **Usuário confirmou: adicionar testes é prioridade.** |
| 5 | Form v1 vs v2? | **Só v2 está ativa.** v1 está registrada em urls.py mas não é mais usada em produção. |
| 6 | Catálogos via AJAX inline? | Confirmado. Parceria, Plano, Produto, Contrato, Lei, Modelo são criados apenas via AJAX JSON. O Django Admin é a única interface de gerenciamento completo. |
| 7 | Múltiplos idiomas? | **Por enquanto apenas `pt_BR`**, e a tradução está incompleta. Arquivos `.po`/`.mo` existem em `src/terralab_v2/locale/pt_BR/` mas não foram totalmente preenchidos. Sem outros idiomas previstos no momento. |
| 8 | Fluxo de deploy? | Docker Compose em produção (9 serviços confirmados). Vagrant disponível para dev local. |

---

## Itens de Ação (priorizados)

### Segurança — Alta prioridade

**A. Corrigir autenticação nas views AJAX**
- Arquivo: `src/ieb/views.py`
- Adicionar `@login_required` em: `load_componentes`, `load_atividades`, `load_subatividades`, `load_equipes`, `load_equipes_adicionais`
- Adicionar `@login_required` nas views principais: `atividade_registro_view`, `atividade_registro_view_v2`, `atividade_registro_detalhe_view`

**B. Remover `@csrf_exempt` e adicionar autenticação**
- Arquivo: `src/ieb/views.py`
- Views: `adicionar_lei`, `atualizar_situacao_lei`, `adicionar_modelo`
- Remover `@csrf_exempt`
- Adicionar `@login_required`
- Garantir que o JS (`script_v2.js`) envia o cookie/header `X-CSRFToken` nas chamadas `fetch()` correspondentes

### Limpeza — Média prioridade

**C. Remover legado v1**
- `src/ieb/urls.py`: remover a URL `atividade_registro/`
- `src/ieb/views.py`: remover `atividade_registro_view` e `_atividade_registro_process`
- Remover template: `src/ieb/templates/atividade_registro_form.html`
- Remover CSS/JS: `css/estilo.css`, `js/script.js`

**D. Redesign dos models geográficos** *(prioridade confirmada)*

Os models `UC`, `PA`, `TUC` e `TIs` são atualmente esqueletos mínimos. Precisam de duas frentes:

**D1. Adequação de atributos às camadas oficiais**
- Levantar atributos dos shapefiles/WFS das fontes (FUNAI para TIs, IBAMA para UCs, INCRA para PAs)
- Adicionar campos correspondentes (`cod_ti`, `cod_uc`, `categoria_uc`, `orgao_gestor`, `grupo_etnico`, etc.)
- `TIs` tem 6 campos hoje (`nome`, `area`, `fase`, `etnia`, `municipio`, `uf`, `modalidade`); UC/PA/TUC têm apenas `nome` + `area` — ambos insuficientes para espelhar as fontes oficiais

**D2. Adição do campo geométrico**
- Adicionar `geometry = gis_models.MultiPolygonField()` (ou PolygonField, conforme geometria das fontes)
- O campo `area = FloatField` pode ser derivado da geometria ou mantido para compatibilidade

**Atenção às dependências antes de migrar:**
- `TIs` é fortemente referenciado: `Aldeia`, `ProjetoTI`, `AtividadeTI`, `TIsIGATI`, `Area` (M2M)
- `UC`, `PA`, `TUC` são usados em `Area` (M2M)
- Migrations exigem cuidado para não quebrar registros existentes
- O import `gis_models` já está no lugar — **não remover**

### API REST — Prioridade confirmada pelo usuário

**F. Implementar API REST com DRF no `ieb`**

DRF já está instalado no ambiente (via GeoNode) — não há dependência nova a adicionar.

**Escopo inicial sugerido (por criticidade):**
1. `AtividadeRegistro` + resultados relacionados (Pessoas, Evento, Área, etc.) — núcleo do monitoramento
2. `TIs`, `UC`, `PA`, `TUC` — catálogos geográficos (especialmente relevante junto com item D)
3. `Indicador` / `IndicadorFinanciador` + `Meta` — dados de metas e indicadores
4. `Projeto` / `Componente` / `Atividade` — hierarquia de projetos

**Casos de uso que a API viabiliza:**
- Integração com ferramentas de análise (pandas, R, QGIS) sem acesso direto ao banco
- Atualizações em massa via scripts (ex: importação/sincronização das camadas oficiais FUNAI/IBAMA/INCRA — item D)
- Gestão programática de registros
- Futuras integrações com dashboards externos ou outros sistemas do IEB

**Arquivos a criar:**
- `src/ieb/serializers.py` — serializers por model
- `src/ieb/api_urls.py` — roteamento DRF (incluir em `urls.py` sob prefixo `/ieb/api/`)
- Atualizar `src/ieb/urls.py` para incluir as rotas da API

**Notas:**
- Autenticação via sessão Django (já disponível) ou token DRF — decidir conforme caso de uso
- Os endpoints de escrita devem exigir `@login_required` / permissões DRF (não repetir o bug do item A)
- Testes de API devem ser incorporados ao item E

**Pré-requisito: refatorar lógica dos `save()` overrides antes de implementar DRF**

Existem 9 overrides de `save()` com lógica de negócio que `bulk_create`/`bulk_update` ignoram silenciosamente. Abordagem recomendada por caso:

| Model | Lógica atual | Abordagem recomendada |
|---|---|---|
| `Area` | Soma `total_ha` via M2M | Service layer → chamado no serializer |
| `AreasProtegidas` | 6 contadores M2M | Service layer → chamado no serializer |
| `Leis` | 5 contadores por situação | Service layer → chamado no serializer |
| `Evento` | Soma `total` | Service layer → chamado no serializer |
| `Parcerias` | 7 contadores por tipo | Service layer → chamado no serializer |
| `Produtos` | 8 contadores por tipo | Service layer → chamado no serializer |
| `Contratos` | Soma `valor_total` M2M | Service layer → chamado no serializer |
| `Planos` | Atualiza `Plano.situacao` + cria `PlanoHistorico` | Service layer → controle explícito do estado anterior |
| `AtividadeRegistroFoto` | Geração de thumbnail (Pillow) | Manter em `save()` — operação sempre unitária |

**Service layer** = funções em `src/ieb/services.py` chamadas explicitamente pelo serializer DRF (e opcionalmente mantidas no `save()` para compatibilidade com admin/formulário). Evita duplicação de lógica e garante que operações bulk passem pela mesma regra de negócio.

---

### Testes — Prioridade confirmada pelo usuário

**E. Estrutura inicial de testes**
- Arquivo: `src/ieb/tests.py`
- Prioridades sugeridas:
  1. Testes de autenticação (verificar que views protegidas retornam 302 para anônimos)
  2. Testes de formulário (`AtividadeRegistroForm`) com datas válidas/inválidas
  3. Testes dos endpoints AJAX (status 200, estrutura JSON)
  4. Testes de criação de `AtividadeRegistro` com resultados (Pessoas, Evento, etc.)
  5. **Testes de áreas geográficas** (a implementar junto com o item D):
     - Consulta aos models `UC`, `PA`, `TUC`, `TIs` com geometria real ou fixture GIS
     - Verificar soma do atributo `area` para um conjunto de registros (ex: área total de TIs associadas a um `AtividadeRegistro` via `Area` M2M)
     - Após D2, validar que `area` derivado da geometria (`geometry.area`) bate com o valor armazenado em `FloatField`
     - Requer `django.test.TestCase` com `--keepdb` ou banco de teste com PostGIS habilitado (já disponível na stack)
- Runner já configurado em `pavement.py` (`paver test`)

---

## Verificação

Após as correções de segurança (A e B):
1. `docker compose exec django python manage.py shell` → verificar que views retornam 403/302 sem login
2. Testar o formulário v2 com usuário logado — confirmar que AJAX ainda funciona com CSRF token
3. Testar criação de Lei/Modelo via formulário — confirmar que funciona sem `@csrf_exempt`
