# Indice de Codigo — terralab_v2

> Gerado em: 2026-04-02
> Branch base: `retomada` (iieb/retomada, commit `d4590ea`)
> Versao GeoNode: 4.4.1 | Versao projeto: 4.2.0-dev

---

## 1. Visao Geral da Arquitetura

```
terralab_v2/                     # Raiz do repositorio
  docker/                        # Dockerfiles auxiliares (nginx, postgresql, geoserver, letsencrypt)
  src/
    terralab_v2/                 # Projeto Django principal (configuracao GeoNode)
    ieb/                         # App customizada — modulo de monitoramento IIEB
    fixtures/                    # Dados iniciais (oauth, celery beat, admin, sites)
    scripts/                     # Scripts auxiliares (apache, cleanup)
    manage.py                    # Entry point Django
    setup.py                     # Empacotamento do projeto
    tasks.py                     # Tasks invoke/paver
    pavement.py                  # Paver tasks
    requirements.txt             # Dependencias Python
    entrypoint.sh                # Entrypoint Docker (django + celery)
    uwsgi.ini                    # Configuracao uWSGI
    celery.sh / celery-cmd       # Scripts Celery worker
  docker-compose.yml             # Orquestracao dos servicos
  Dockerfile                     # Imagem Django (base: geonode/geonode-base)
  .env.sample                    # Template de variaveis de ambiente
  geonode-stack.yml              # Docker stack (swarm)
  Vagrantfile / Vagrantfile.stack # Provisionamento Vagrant
  playbook.yml                   # Ansible playbook
```

### Stack de infraestrutura (docker-compose)

| Servico | Imagem/Papel | Porta |
|---|---|---|
| `django` | App Django + uWSGI | 8000 (interno) |
| `celery` | Worker Celery (mesma imagem) | — |
| `geonode` (nginx) | Reverse proxy + estaticos | 80/443 |
| `geoserver` | GeoServer 2.24.4 | 8080 |
| `db` | PostgreSQL 15 + PostGIS | 5432 (interno) |
| `rabbitmq` | Broker AMQP para Celery | 5672 (interno) |
| `memcached` | Cache (opcional) | 11211 (interno) |
| `letsencrypt` | Certificados SSL | — |
| `data-dir-conf` | Configuracao GeoServer (sidecar) | — |

---

## 2. Modulos/Pacotes

### 2.1 `src/terralab_v2/` — Projeto Django (configuracao GeoNode)

| Arquivo | Responsabilidade |
|---|---|
| `__init__.py` | Versao (4.2.0-dev), registra `AppConfig` |
| `settings.py` | Settings do projeto; herda de `geonode.settings`; adiciona app `ieb`; configura locale, templates, logging, LDAP, dashboard centralizado |
| `urls.py` | URL root; inclui `geonode.urls` + `ieb.urls` sob prefixo `/ieb/` |
| `apps.py` | `AppConfig` — injeta templates dir e celeryapp no `ready()` |
| `celeryapp.py` | Configuracao Celery (`terralab_v2`), autodiscover |
| `wsgi.py` | WSGI entry point |
| `version.py` | Utilitario de versao baseado em git changeset |

### 2.2 `src/ieb/` — App de Monitoramento IIEB

| Arquivo | Responsabilidade |
|---|---|
| `models.py` | **50+ models** — dominio completo de monitoramento (ver secao 3) |
| `views.py` | Views function-based: formulario registro, dashboard, AJAX endpoints, PDF, email |
| `urls.py` | 18 URLs sob prefixo `/ieb/` |
| `forms.py` | `AtividadeRegistroForm` (ModelForm) com validacao de datas |
| `admin.py` | Registro extensivo de models com inlines e fieldsets |
| `apps.py` | `IebConfig` — AppConfig padrao |
| `tests.py` | Tests (vazio — sem testes escritos) |

### 2.3 Templates (`src/ieb/templates/`)

| Template | View associada | Funcao |
|---|---|---|
| `atividade_registro_form.html` | `atividade_registro_view` | Formulario v1 de registro de atividade |
| `atividade_registro_form_v2.html` | `atividade_registro_view_v2` | Formulario v2 (wizard por etapas) |
| `atividade_registro_detalhe.html` | `atividade_registro_detalhe_view` | Pagina de detalhe do registro |
| `atividade_registro_pdf.html` | `gerar_pdf` | Template para geracao de PDF |
| `monitoramento_registros.html` | `monitoramento_registros_view` | Dashboard de listagem de registros |
| `monitoramento_metas.html` | `monitoramento_metas_view` | Dashboard de metas com % cumprimento |
| `apresentacao_moore.html` | `apresentacao_moore` | Pagina estatica de apresentacao |
| `teste_parcerias.html` | `teste_parcerias_view` | Pagina de teste de parcerias |

### 2.4 Static (`src/terralab_v2/static/ieb/`)

| Arquivo | Funcao |
|---|---|
| `css/estilo.css` | Estilos gerais do formulario v1 |
| `css/form_v2.css` | Estilos do formulario v2 (wizard) |
| `css/detalhe.css` | Estilos da pagina de detalhe |
| `css/monitoramento.css` | Estilos dos dashboards |
| `css/indicadores.css` | Estilos da secao de indicadores |
| `css/lightbox.css` | Estilos do lightbox de fotos |
| `js/script.js` | JS do formulario v1 |
| `js/script_v2.js` | JS do formulario v2 (wizard) |
| `js/lightbox.js` | JS do lightbox de fotos |

---

## 3. Modelos de Dados (`src/ieb/models.py`)

### 3.1 Dominio — Organizacoes Indigenas

| Model | Descricao |
|---|---|
| `OIsRegional` | Organizacao Indigena Regional |
| `OIsLocal` | Organizacao Indigena Local |
| `OIRegLoc` | Relacao N:N entre OI Regional e Local |
| `TIs` | Terras Indigenas |
| `Aldeia` | Aldeias (FK → TIs) |
| `Indigena` | Individuos indigenas (FK → Aldeia) |
| `IGATI` | Instancia de Gestao Ambiental e Territorial Indigena |
| `TIsIGATI` | Relacao N:N TIs ↔ IGATI |

### 3.2 Gestao de Projetos

| Model | Descricao |
|---|---|
| `Programa` | Area tematica institucional |
| `Projeto` | Projeto (M2M → Programa, Financiador; FK → Projeto pai para subprojetos) |
| `Componente` | Componente de projeto (FK → Projeto, Instituicao) |
| `Atividade` | Atividade (FK → Componente) |
| `Subatividade` | Subatividade (FK → Atividade) |
| `Equipe` | Membro de equipe (FK → Instituicao) |
| `EquipeProjeto` | Alocacao de equipe em projeto |
| `ProjetoOI` | Vinculo Projeto ↔ OIsLocal |
| `ProjetoTI` | Vinculo Projeto ↔ TIs |
| `Financiador` | Financiador de projetos |
| `Instituicao` | Instituicao parceira |
| `AreaTematica` | Classificacao tematica de atividades |
| `AtividadeAreaTematica` | N:N Atividade ↔ AreaTematica |
| `AtividadeOILocal` | N:N Atividade ↔ OIsLocal |
| `AtividadeOIRegional` | N:N Atividade ↔ OIsRegional |
| `AtividadeTI` | N:N Atividade ↔ TIs |

### 3.3 Indicadores e Metas

| Model | Descricao |
|---|---|
| `Indicador` | Indicador base com 15 tipos e ~25 flags de desagregacao |
| `IndicadorFinanciador` | Indicador especifico por financiador (mesma estrutura de desagregacoes) |
| `Meta` | Meta por atividade + indicador (base, meta, data, data_inicio) |
| `MetaFinanciador` | Meta por atividade + indicador de financiador |
| `ProjetoIndicador` | N:N Projeto ↔ Indicador |
| `ProjetoIndicadorFin` | N:N Projeto ↔ IndicadorFinanciador |

**Tipos de indicador** (`INDICADOR_TIPO_CHOICES`):
`pessoas`, `organizacoes`, `area`, `areas_protegidas`, `eventos`, `planos`, `parcerias`, `mobilizados`, `produtos`, `contratos`, `redes`, `pequenos_projetos`, `fundos`, `leis_politicas`, `outro`

### 3.4 Registros de Atividade e Resultados

| Model | Descricao |
|---|---|
| `AtividadeRegistro` | Registro central de atividade realizada |
| `AtividadeRegistroFoto` | Fotos anexadas ao registro |
| `AtividadeRegistroListaPresenca` | Lista de presenca anexada |
| `Pessoas` | Resultado tipo "pessoas" (com desagregacoes) |
| `Organizacoes` | Resultado tipo "organizacoes" |
| `Area` | Resultado tipo "area" (HA, M2M com TIs/UCs/PAs/TUCs) |
| `AreasProtegidas` | Resultado tipo "areas protegidas" |
| `Evento` | Resultado tipo "eventos" (formacoes, seminarios, etc.) |
| `Rede` | Resultado tipo "redes" |
| `PequenoProjeto` | Resultado tipo "pequenos projetos" |
| `Fundo` | Resultado tipo "fundos" |
| `Outro` | Resultado generico |
| `Plano` | Catalogo de planos (PGTA, Manejo, etc.) com situacao |
| `Planos` | Resultado tipo "planos" (vinculo registro ↔ plano) |
| `PlanoHistorico` | Historico de mudancas de situacao de planos |
| `Parceria` | Catalogo de parcerias |
| `Parcerias` | Resultado tipo "parcerias" |
| `Lei` | Catalogo de leis/politicas |
| `Leis` | Resultado tipo "leis_politicas" |
| `LeiHistorico` | Historico de mudancas de leis |
| `Mobilizados` | Resultado tipo "recursos mobilizados" |
| `Produto` | Catalogo de produtos |
| `Produtos` | Resultado tipo "produtos" |
| `Contrato` | Catalogo de contratos |
| `Contratos` | Resultado tipo "contratos" |
| `Modelo` | Catalogo de modelos |
| `AtividadeRegistroModelo` | Vinculo registro ↔ modelo |

### 3.5 Catalogos Geograficos

| Model | Descricao |
|---|---|
| `UC` | Unidade de Conservacao |
| `PA` | Projeto de Assentamento |
| `TUC` | Territorio de Uso Comum |

### 3.6 Politicas Publicas Indigenas

| Model | Descricao |
|---|---|
| `CR` | Coordenacia Regional (FUNAI) |
| `CTL` | Coordenacia Local (FUNAI, FK → CR) |
| `DSEI` | Distrito Sanitario Especial Indigena |
| `Posto` | Posto de saude (FK → DSEI, Aldeia) |
| `Casai` | Casa de Saude Indigena (FK → DSEI) |
| `Polo` | Polo Base (FK → DSEI) |
| `AIS` | Agente Indigena de Saude (FK → DSEI) |
| `Escola` | Escola Indigena (FK → Aldeia) |
| `Professores` | Professor (FK → Escola) |
| `FormacaoIndigena` | Formacao de indigena (FK → Indigena) |

### 3.7 Diagrama de Dependencias dos Models

```
Programa ←── M2M ──→ Projeto ←── M2M ──→ Financiador
                    Projeto ←── FK ──── Projeto (subprojetos)
                    Projeto ←── Componente ←── Atividade ←── Subatividade
                    Projeto ←── EquipeProjeto
                    Projeto ←── ProjetoOI → OIsLocal
                    Projeto ←── ProjetoTI → TIs
                    Projeto ←── ProjetoIndicador → Indicador
                    Projeto ←── ProjetoIndicadorFin → IndicadorFinanciador

Atividade ←── Meta → Indicador
Atividade ←── MetaFinanciador → IndicadorFinanciador
Atividade ←── AtividadeAreaTematica → AreaTematica
Atividade ←── AtividadeOILocal → OIsLocal
Atividade ←── AtividadeOIRegional → OIsRegional
Atividade ←── AtividadeTI → TIs

AtividadeRegistro → Projeto, Componente, Atividade, Subatividade, EquipeProjeto
AtividadeRegistro ←── AtividadeRegistroFoto
AtividadeRegistro ←── AtividadeRegistroListaPresenca
AtividadeRegistro ←── Pessoas → Indicador ou IndicadorFinanciador
AtividadeRegistro ←── Organizacoes → Indicador ou IndicadorFinanciador
AtividadeRegistro ←── Area (M2M TIs, UCs, PAs, TUCs) → Indicador ou IndicadorFinanciador
AtividadeRegistro ←── AreasProtegidas → Indicador ou IndicadorFinanciador
AtividadeRegistro ←── Evento → Indicador ou IndicadorFinanciador
AtividadeRegistro ←── [todos os demais resultados] → Indicador ou IndicadorFinanciador
```

---

## 4. URLs e Endpoints (`/ieb/`)

### Formulario e CRUD

| URL | View | Metodo | Auth |
|---|---|---|---|
| `ieb/atividade_registro/` | `atividade_registro_view` | GET/POST | — |
| `ieb/atividade_registro/v2/` | `atividade_registro_view_v2` | GET/POST | — |
| `ieb/atividade/<int:pk>/` | `atividade_registro_detalhe_view` | GET | — |
| `ieb/atividade/<int:pk>/anterior/` | `atividade_registro_anterior` | GET | — |
| `ieb/atividade/<int:pk>/proximo/` | `atividade_registro_proximo` | GET | — |

### AJAX — Carregamento dinamico

| URL | View | Descricao |
|---|---|---|
| `ieb/ajax/load-componentes/` | `load_componentes` | Componentes por projeto |
| `ieb/ajax/load-atividades/` | `load_atividades` | Atividades por componente |
| `ieb/ajax/load-subatividades/` | `load_subatividades` | Subatividades por atividade |
| `ieb/ajax/load-equipes/` | `load_equipes` | Equipes por projeto |
| `ieb/ajax/load-equipes-adicionais/` | `load_equipes_adicionais` | Equipes adicionais por projeto |
| `ieb/load_indicadores/` | `load_indicadores` | Indicadores + desagregacoes por projeto/atividade |

### AJAX — CRUD inline

| URL | View | Descricao |
|---|---|---|
| `ieb/adicionar_parceria/` | `adicionar_parceria` | Criar Parceria via JSON |
| `ieb/adicionar-plano/` | `adicionar_plano` | Criar Plano via JSON |
| `ieb/atualizar_situacao_plano/` | `atualizar_situacao_plano` | Atualizar situacao do Plano |
| `ieb/adicionar_produto/` | `adicionar_produto` | Criar Produto via JSON |
| `ieb/adicionar_contrato/` | `adicionar_contrato` | Criar Contrato via JSON |
| `ieb/atualizar_estado_contrato/` | `atualizar_estado_contrato` | Atualizar estado do Contrato |
| `ieb/adicionar_lei/` | `adicionar_lei` | Criar Lei via JSON |
| `ieb/atualizar_situacao_lei/` | `atualizar_situacao_lei` | Atualizar situacao da Lei |
| `ieb/adicionar_modelo/` | `adicionar_modelo` | Criar Modelo via JSON |

### Dashboard

| URL | View | Descricao |
|---|---|---|
| `ieb/monitoramento/registros/` | `monitoramento_registros_view` | Listagem de registros com filtros |
| `ieb/monitoramento/metas/` | `monitoramento_metas_view` | Dashboard de metas com % cumprimento |

### Outros

| URL | View | Descricao |
|---|---|---|
| `ieb/apresentacao_moore/` | `apresentacao_moore` | Pagina estatica |
| `ieb/teste_parcerias/` | `teste_parcerias_view` | Pagina de teste |

---

## 5. Dependencias Internas (Imports)

```
terralab_v2/settings.py
  ← geonode.settings (fallback via except ImportError)
  ← terralab_v2.local_settings (opcional)

terralab_v2/urls.py
  ← geonode.urls (urlpatterns base do GeoNode)
  ← ieb.urls (inclusao sob /ieb/)

terralab_v2/apps.py
  ← terralab_v2.celeryapp (registra celery app)

ieb/views.py
  ← ieb.forms (AtividadeRegistroForm)
  ← ieb.models (todos os models)
  ← django.core.mail, xhtml2pdf, django.template.loader

ieb/forms.py
  ← ieb.models (AtividadeRegistro, Meta, Indicador, Projeto, Subatividade)

ieb/admin.py
  ← ieb.models (import * — todos os models)

ieb/urls.py
  ← ieb.views (todas as views)
```

---

## 6. Integracoes Externas

| Biblioteca/Servico | Versao | Uso |
|---|---|---|
| **GeoNode** | 4.4.1 | Plataforma base (GIS, catalogo, upload, auth, OGC) |
| **Django** | (via GeoNode) | Framework web |
| **GeoServer** | 2.24.4 | Servidor OGC (WMS, WFS, WCS) |
| **PostgreSQL/PostGIS** | 15.3 | Banco de dados espacial |
| **Celery** + RabbitMQ | — | Processamento assincrono |
| **uWSGI** | — | Servidor WSGI em producao |
| **Nginx** | 1.25.3 | Reverse proxy + estaticos |
| **xhtml2pdf** | 0.2.16 | Geracao de PDF a partir de HTML |
| **Pillow (PIL)** | — | Processamento de imagens (thumbnails) |
| **MapStore** | (via GeoNode) | Cliente GIS (mapas, previews) |
| **django.contrib.gis** | — | GIS models (importado mas nao utilizado ativamente) |
| **Memcached** | — | Cache (opcional, desabilitado por padrao) |
| **LDAP** | (opcional) | Autenticacao via LDAP (geonode_ldap) |
| **Logstash** | (opcional) | Dashboard centralizado (geonode_logstash) |

---

## 7. Pontos de Extensao

| Ponto | Arquivo | Descricao |
|---|---|---|
| **Settings override** | `src/terralab_v2/settings.py:40-44` | Tenta importar `local_settings`; fallback para `geonode.settings` |
| **INSTALLED_APPS** | `src/terralab_v2/settings.py:72-73` | Adiciona `terralab_v2` e `ieb` |
| **STATICFILES_DIRS** | `src/terralab_v2/settings.py:80-83` | Inclui `ieb/static` |
| **TEMPLATES** | `src/terralab_v2/settings.py:88-95` | Injeta dir de templates do projeto |
| **URL patterns** | `src/terralab_v2/urls.py:33-39` | `custom_urlpatterns` para adicionar rotas |
| **MapStore config** | `src/terralab_v2/templates/geonode-mapstore-client/_geonode_config.html` | Override do `localConfig` do MapStore |
| **Celery autodiscover** | `src/terralab_v2/celeryapp.py:33` | Descobre tasks automaticamente |
| **LDAP toggle** | `src/terralab_v2/settings.py:173-175` | Ativado via env `LDAP_ENABLED` |
| **Dashboard toggle** | `src/terralab_v2/settings.py:158-166` | Ativado via env `CENTRALIZED_DASHBOARD_ENABLED` |
| **MONITORING_EMAIL** | `src/terralab_v2/settings.py:181` | Email fixo para notificacoes (env var) |
| **Locale** | `src/terralab_v2/settings.py:63-66` | `en` + `pt-BR`; arquivos em `locale/pt_BR/` |

---

## 8. Migrations

32 migrations no app `ieb`, evoluindo desde o schema inicial ate a fase F:

| Range | Fase |
|---|---|
| `0001` | Schema inicial |
| `0002-0009` | Ajustes de campos, remocao de legados |
| `0010-0017` | Parcerias, planos, fotos, email |
| `0018-0020` | Area tematica, indicador tipo, subatividade, fotos/lista presenca |
| `0021-0025` | Fix imagefield, programa, financiadores, redesign indicadores |
| `0026-0029` | Redesign Planos, IndicadorFinanciador, tipo choices rename |
| `0030-0032` | Desagregacoes, result models redesign, meta periodo |

---

## 9. Pontos Cegos

Areas que nao foi possivel indexar completamente com varredura estatica:

1. **GeoNode internals**: O projeto herda a maior parte da funcionalidade de `geonode.settings` (que e instalado como pacote pip). Nao temos visibilidade dos models, views, signals e middlewares que o GeoNode registra automaticamente.

2. **`src/tasks.py` e `src/pavement.py`**: Tasks invoke/paver que rodam no entrypoint Docker (update, migrations, fixtures, statics). Nao foram lidos — podem conter logica de inicializacao importante.

3. **`src/ieb/tests.py`**: Arquivo existe mas esta vazio. Nao ha testes automatizados para nenhum dos 50+ models ou views.

4. **Templates HTML**: A analise foi apenas por nome de arquivo. O conteudo dos templates (heranca de blocks, includes, JS inline) nao foi examinado. O formulario v2 (`atividade_registro_form_v2.html`) provavelmente contem logica JS significativa (wizard por etapas).

5. **JavaScript (`script.js`, `script_v2.js`)**: Nao foram lidos. Provavelmente contem a logica de carregamento dinamico de indicadores e construcao do formulario de resultados.

6. **`django.contrib.gis`**: Importado em `models.py` como `gis_models` mas nenhum model usa campos espaciais (GeometryField, etc.). Os models usam apenas FloatField para areas. Incerto se ha uso planejado de GIS ou se e legado.

7. **Email/SMTP**: A view `enviar_email_notificacao` configura SMTP diretamente via `EmailBackend`. As credenciais vem de `settings.EMAIL_*` (definidos no `.env`), mas o fluxo real de envio depende de configuracao de infraestrutura que nao pode ser validada estaticamente.

8. **CSRF exempt**: Views `adicionar_lei`, `atualizar_situacao_lei`, `adicionar_modelo` usam `@csrf_exempt` — risco de seguranca se expostas publicamente.

9. **`load_indicadores`**: Usa `@login_required` mas as demais views AJAX nao usam decoradores de autenticacao.

10. **Vagrant/Ansible**: `Vagrantfile`, `Vagrantfile.stack`, `playbook.yml` nao foram analisados — podem conter logica de provisionamento relevante.

---

## 10. Perguntas para Esclarecimento

1. **Qual a versao de Python alvo?** O Dockerfile usa `geonode/geonode-base:latest-ubuntu-22.04` — presumivelmente Python 3.10+, mas nao confirmado.

2. **O app `ieb` usa alguma API REST (DRF)?** Nao ha `serializers.py` nem referencia ao Django REST Framework nos arquivos analisados. Todo o CRUD e feito via views function-based e JSON manual.

3. **Ha algum signal Django registrado?** Nao ha `signals.py` no projeto. Os models usam `save()` overrides para logica de calculo (totais, historicos). Confirmar se nao ha signals no `__init__.py` ou via GeoNode.

4. **Qual o estado dos testes?** `tests.py` esta vazio. Ha intenção de implementar testes? Isso impacta qualquer refatoracao.

5. **O formulario v1 (`atividade_registro_form.html`) ainda e usado?** Ha v1 e v2. A v2 e a versao ativa ou ambas coexistem?

6. **Os catalogos (Parceria, Plano, Produto, Contrato, Lei, Modelo) sao gerenciados apenas via AJAX inline?** Nao ha views de listagem/edicao dedicadas para esses catalogos — apenas criacao via JSON. O admin Django e a unica interface de gerenciamento completa?

7. **Ha necessidade de suporte a multiplos idiomas alem de pt-BR?** Os arquivos de locale existem mas nao esta claro se as traducoes estao completas.

8. **Qual o fluxo de deploy atual?** Docker Compose em producao? Vagrant para desenvolvimento? Ambos?

---

## 11. Recomendacao

**Sim, recomendo iniciar uma sessao nova (passo 4) antes de prosseguir para o passo 2.** Motivos:

- O indice acima da uma visao completa do estado atual do codigo
- As perguntas na secao 10 devem ser respondidas antes de quebrar tarefas, pois podem mudar o escopo do trabalho
- A sessao nova pode carregar este indice como contexto, evitando re-analise
- O projeto tem complexidade suficiente (50+ models, views monoliticas de ~1000 linhas, sem testes) para que um planejamento cuidadoso seja essencial
