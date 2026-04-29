# Plano Técnico — Protótipo de Dashboard DANIDA com django-plotly-dash

**Projeto**: TerraLab/IEB  
**Data**: 2026-04-29  
**Versão**: 1.0  
**Contexto**: Primeiro protótipo demonstrativo de dashboard interativo para parceiros, baseado nos indicadores do projeto DANIDA, integrado ao GeoNode existente sem modificar seu núcleo.

---

## 1. Arquitetura Proposta

### 1.1 Diagnóstico de infraestrutura atual

| Elemento | Situação atual | Implicação para django-plotly-dash |
|---|---|---|
| Servidor WSGI | uWSGI (`uwsgi.ini`) | ✅ Compatível com modo iframe do django-plotly-dash |
| ASGI | Inexistente no projeto | ❌ Sem WebSocket; callbacks server-side em tempo real exigiriam migração para Daphne/Uvicorn |
| Django | 4.x (via GeoNode 4.4.1) | ✅ Compatível com django-plotly-dash |
| Template engine | Django Templates (padrão) | ✅ Tags `{% plotly_app %}` funcionam |
| Static files | Coletados via `collectstatic`, servidos pelo Nginx | ✅ `dpd-static-support` resolve assets do Dash |

**Conclusão**: django-plotly-dash funciona no modo **iframe embedding** (`{% plotly_app %}`) sem alterar a infraestrutura uWSGI. A limitação é que callbacks Dash que dependem de WebSocket em tempo real não estarão disponíveis. Para o protótipo, isso é aceitável — os gráficos Plotly mantêm interatividade nativa (zoom, hover, seleção) sem callbacks.

### 1.2 Estratégia de integração

```
┌──────────────────────────────────────────────────────┐
│  GeoNode (geonode.urls)                              │
│  ├── /maps/, /layers/, /documents/, /admin/ ...      │
│  ├── /ieb/          → ieb.urls (app de negócio)      │
│  └── /danida/       → danida_dashboards.urls (NOVO)  │
│       └── /dashboard/   → template Django + Dash      │
│       └── /django_plotly_dash/ → rotas internas DPD   │
└──────────────────────────────────────────────────────┘
```

O app `danida_dashboards` é um módulo independente que:
- Lê dados dos modelos `ieb` (somente leitura, sem acoplamento de escrita);
- Gera visualizações com Dash/Plotly;
- Serve páginas Django com templates próprios;
- Injeta zero dependências no núcleo do GeoNode;
- Pode ser removido desregistrando `INSTALLED_APPS` e a rota `/danida/`.

### 1.3 Alternativa simplificada (fallback)

Caso a complexidade do django-plotly-dash se mostre excessiva para o protótipo inicial, existe a alternativa de usar **Plotly.py diretamente** em uma view Django. Nesse modo:
- Apenas `plotly` é necessário como dependência;
- A view gera HTML via `plotly.io.to_html()` ou `fig.to_html()`;
- O template injeta `{{ plot_div|safe }}`;
- Mantém interatividade nativa do Plotly (zoom, hover, tooltips);
- Não requer Dash, django-plotly-dash, nem mudanças em `INSTALLED_APPS`.

A recomendação é manter essa alternativa documentada e decidir entre as duas abordagens na etapa de implementação, com base na avaliação de esforço × benefício.

---

## 2. Estrutura de Arquivos Sugerida

### 2.1 Árvore do novo app

```
codigo/terralab_v2/src/danida_dashboards/
├── __init__.py
├── apps.py                    # DanidaDashboardsConfig
├── urls.py                    # Rotas do dashboard
├── views.py                   # Views Django (páginas + contexto)
├── dash_apps.py               # Definições dos apps Dash (layout + callbacks)
├── data.py                    # Camada de dados mockados + funções de agregação
├── templates/
│   └── danida_dashboards/
│       ├── base.html          # Template base do dashboard (herda do GeoNode ou standalone)
│       └── index.html         # Página principal "Dashboard DANIDA"
├── static/
│   └── danida_dashboards/
│       ├── css/
│       │   └── dashboard.css  # Estilos customizados
│       └── js/
│           └── (vazio ou helpers mínimos)
└── tests.py                   # Testes básicos
```

### 2.2 Arquivos existentes a modificar

| Arquivo | Tipo de alteração | Risco |
|---|---|---|
| `src/terralab_v2/settings.py:72-73` | Adicionar `'danida_dashboards'` e `'django_plotly_dash'` a `INSTALLED_APPS` | Baixo |
| `src/terralab_v2/settings.py:80-83` | Adicionar `static/` do novo app a `STATICFILES_DIRS` | Baixo |
| `src/terralab_v2/urls.py:33-39` | Adicionar `path('danida/', include(...))` a `custom_urlpatterns` | Baixo |
| `src/requirements.txt` | Adicionar dependências Python | Baixo |
| `src/uwsgi.ini` | **Nenhuma alteração** (modo iframe não exige ASGI) | Nulo |

### 2.3 Arquivos do GeoNode que **não** serão alterados

- Nenhum arquivo do pacote `geonode` será modificado.
- Nenhum model, view, ou template do GeoNode será sobrescrito.
- As rotas `/maps/`, `/layers/`, `/documents/` permanecem intocadas.

---

## 3. Instalação e Dependências

### 3.1 Pacotes Python necessários

Adicionar ao `src/requirements.txt`:

```
django-plotly-dash>=2.3,<3.0
dash>=2.14
plotly>=5.18
dash-bootstrap-components>=1.5
dpd-static-support>=1.1
pandas>=2.0
```

**Justificativa de cada dependência**:

| Pacote | Função |
|---|---|
| `django-plotly-dash` | Ponte Django ↔ Dash; template tags `{% plotly_app %}` |
| `dash` | Framework de visualização interativa (Plotly Dash) |
| `plotly` | Engine de renderização dos gráficos |
| `dash-bootstrap-components` | Componentes de UI responsivos (cards, grids, temas) |
| `dpd-static-support` | Gerencia arquivos estáticos do Dash no Django |
| `pandas` | Manipulação de dados; transformação de querysets em DataFrames |

### 3.2 Ajustes em `settings.py`

```python
# Linha ~72 — adicionar os novos apps
INSTALLED_APPS += (PROJECT_NAME, 'ieb', 'danida_dashboards', 'django_plotly_dash')

# Linha ~80 — adicionar diretório de estáticos
STATICFILES_DIRS = [
    os.path.join(LOCAL_ROOT, "static"),
    os.path.join(BASE_DIR, "ieb/static"),
    os.path.join(BASE_DIR, "danida_dashboards/static"),
] + STATICFILES_DIRS

# Configurações do django-plotly-dash (adicionar ao final do arquivo)
PLOTLY_DASH = {
    "ws_route": "ws/channel",            # Não utilizado em modo WSGI
    "http_route": "django_plotly_dash",  # Rota HTTP para iframe
    "serve_locally": True,               # Servir assets Dash localmente
    "cache_timeout_initial_arguments": 60,
}
```

### 3.3 Ajustes em `urls.py`

```python
# Linha 33-39 — adicionar rotas do dashboard
custom_urlpatterns = [
    path('ieb/', include('ieb.urls')),
    path('danida/', include('danida_dashboards.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
```

### 3.4 Template base do dashboard

O template `danida_dashboards/templates/danida_dashboards/base.html` deve:
- Carregar `{% load plotly_dash %}` no topo;
- Incluir `{% plotly_header %}` no `<head>`;
- Incluir `{% plotly_footer %}` antes de `</body>`;
- Herdar do layout base do GeoNode OU ser standalone, dependendo da decisão de integração visual.

### 3.5 Pontos de atenção para Docker

| Ponto | Ação |
|---|---|
| Build da imagem | `pip install -r requirements.txt` no Dockerfile já cobre as novas dependências |
| `collectstatic` | Deve ser executado após adicionar o app; o `dpd-static-support` gerencia os assets do Dash |
| Volume mount | O código fonte é montado em `./src:/usr/src/terralab_v2` (dev); em produção, rebuild da imagem |
| Nginx | Já configurado para servir `/mnt/volumes/statics`; sem alterações necessárias |
| uWSGI | Sem alterações; o modo iframe do Dash não exige ASGI |
| Hot reload | Em dev com volume mount, alterações em `dash_apps.py` exigem restart do uWSGI para refletir |

---

## 4. Protótipo Mínimo

### 4.1 Objetivo

Uma única página Django chamada **"Dashboard DANIDA"**, acessível em `/danida/dashboard/`, contendo um app Dash embutido com 3 gráficos Plotly baseados em dados mockados que representam os 5 tipos de indicadores do projeto DANIDA (fundos, área, organizações, pessoas, planos).

### 4.2 Dados mockados

Criar em `data.py` um dicionário com dados sintéticos que representem indicadores realistas, por exemplo:

- **Registros por tipo de indicador** (fundos: 2, área: 8, organizações: 5, pessoas: 45, planos: 3)
- **Evolução temporal** (12 meses de 2025-2026, com contagem mensal de registros)
- **Distribuição por território** (5-7 territórios/terras indígenas com contagens)
- **Status de metas** (percentuais de atingimento simulados por tipo)

Os dados devem ser suficientemente genéricos para não expor informação sensível, mas verossímeis o bastante para demonstrar o potencial.

### 4.3 Gráficos sugeridos

#### Gráfico 1 — Barras: Registros por tipo de indicador DANIDA

- **Tipo**: Bar chart (Plotly Express: `px.bar`)
- **Eixo X**: Tipo de indicador (Fundos, Área, Organizações, Pessoas, Planos)
- **Eixo Y**: Quantidade total de registros
- **Cor**: Por tipo (categorical color)
- **Interatividade**: Hover com valor exato, clique para isolar categoria
- **Propósito**: Demonstrar volume de dados por categoria

#### Gráfico 2 — Linha temporal: Evolução de coletas ao longo do projeto

- **Tipo**: Line chart (Plotly Express: `px.line`)
- **Eixo X**: Mês/ano (Jan 2025 – Dez 2026)
- **Eixo Y**: Número de registros
- **Múltiplas linhas**: Uma por tipo de indicador (ou agregado total)
- **Propósito**: Demonstrar progressão temporal e sazonalidade

#### Gráfico 3 — Pizza/Treemap: Distribuição por território/comunidade

- **Tipo**: Treemap ou Sunburst (Plotly Express: `px.treemap`)
- **Hierarquia**: Território → Tipo de indicador
- **Tamanho**: Quantidade de registros
- **Cor**: Por território
- **Propósito**: Demonstrar distribuição geográfica dos dados

### 4.4 Estrutura do app Dash

```python
# dash_apps.py
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
from .data import get_mock_data

# Inicialização com tema Bootstrap
app = DjangoDash('DanidaDashboard', external_stylesheets=[dbc.themes.BOOTSTRAP])

# Obter dados mockados
df_tipos, df_temporal, df_territorios = get_mock_data()

# Layout (usando dbc.Container, dbc.Row, dbc.Col para responsividade)
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard DANIDA — Indicadores"), className="mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.bar(df_tipos, ...)), md=6),
        dbc.Col(dcc.Graph(figure=px.line(df_temporal, ...)), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.treemap(df_territorios, ...)), md=12),
    ]),
], fluid=True)
```

### 4.5 View e template Django

**`views.py`**:
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    return render(request, 'danida_dashboards/index.html', {
        'titulo': 'Dashboard DANIDA',
    })
```

**`urls.py`**:
```python
from django.urls import path
from . import views

app_name = 'danida_dashboards'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
```

**`templates/danida_dashboards/index.html`**:
```django
{% extends 'danida_dashboards/base.html' %}
{% load plotly_dash %}

{% block content %}
<h1>{{ titulo }}</h1>
<p>Protótipo demonstrativo — Dados mockados. Projeto DANIDA / TerraLab.</p>
{% plotly_app name='DanidaDashboard' ratio=0.5 %}
{% endblock %}
```

**`templates/danida_dashboards/base.html`**:
```django
{% load plotly_dash %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{% block title %}Dashboard DANIDA{% endblock %}</title>
    {% plotly_header %}
    <link rel="stylesheet" href="...">
</head>
<body>
    {% block content %}{% endblock %}
    {% plotly_footer %}
</body>
</html>
```

---

## 5. Caminho de Evolução

### 5.1 Fase 1 — Protótipo atual (mock data)

- Todos os dados vêm de `data.py` com estruturas Python nativas (listas, dicionários).
- Zero dependência de banco de dados.
- Objetivo: demonstrar viabilidade visual e técnica para parceiros.

### 5.2 Fase 2 — Substituição por dados reais (leitura do banco)

Substituir `data.py` por um módulo `services.py` que consulta os modelos `ieb`:

```python
# services.py (conceitual)
from ieb.models import AtividadeRegistro, Meta, Indicador

def get_registros_por_tipo():
    """Agrega registros por tipo de indicador DANIDA."""
    tipos_danida = ['fundos', 'area', 'organizacoes', 'pessoas', 'planos']
    qs = AtividadeRegistro.objects.filter(
        indicador__tipo__in=tipos_danida
    ).values('indicador__tipo').annotate(total=Count('id'))
    return pd.DataFrame(qs)

def get_evolucao_temporal():
    """Série temporal mensal de registros."""
    qs = AtividadeRegistro.objects.filter(
        indicador__tipo__in=tipos_danida
    ).annotate(mes=TruncMonth('data')).values('mes', 'indicador__tipo').annotate(total=Count('id'))
    return pd.DataFrame(qs)
```

### 5.3 Possíveis fontes de dados

| Fonte | Tipo de acesso | Dados disponíveis | Complexidade |
|---|---|---|---|
| PostgreSQL/PostGIS do GeoNode | Django ORM direto (models `ieb`) | Todos os registros do sistema IEB | Baixa |
| API REST do GeoNode | HTTP/JSON | Layers, maps, documents (geoespaciais) | Média |
| KoboToolbox | API externa / exportação CSV | Dados de campo (coletas) | Alta (fora do escopo imediato) |
| Tabelas intermediárias | Django ORM (models `ieb`) | Metas, indicadores, agregações | Baixa |

**Recomendação para Fase 2**: Usar exclusivamente o Django ORM sobre os modelos `ieb`, que já contêm todos os tipos de indicadores DANIDA (`fundos`, `area`, `organizacoes`, `pessoas`, `planos`), conforme validado no plano Danida v2.0.

### 5.4 Camada de serviço (services.py)

A camada de serviço deve:
1. Receber chamadas das views ou dos apps Dash;
2. Consultar modelos `ieb` via Django ORM;
3. Transformar querysets em `pandas.DataFrame` ou `list[dict]`;
4. Aplicar agregações, filtros e cálculos;
5. Retornar dados prontos para visualização;
6. Ser cacheável (usar `@cached_property` ou cache do Django);
7. Ser testável isoladamente (sem dependência de request HTTP).

Essa camada desacopla a lógica de dados da lógica de apresentação, facilitando a evolução futura para outras fontes (APIs, data warehouses, etc.).

### 5.5 Evolução para dashboards com callbacks interativos

Quando houver necessidade de callbacks Dinâmicos (filtros interativos, drill-down), duas opções:

**Opção A — Migrar para ASGI** (recomendado para produção):
- Adicionar `daphne` ou `uvicorn` ao projeto;
- Criar `asgi.py` no projeto Django;
- Ajustar `docker-compose.yml` para usar ASGI no serviço `django`;
- Os apps Dash passam a suportar callbacks com WebSocket.

**Opção B — Usar HTMX + Plotly.py** (menos intrusivo):
- Manter uWSGI;
- Substituir django-plotly-dash por Plotly.py + HTMX;
- Filtros disparam requisições HTTP para endpoints que retornam novo HTML;
- Menor custo de infraestrutura, mas menos fluidez que Dash nativo.

---

## 6. Critérios de Qualidade

### 6.1 Simplicidade

- ✅ Um único app Django com arquivos enxutos (~6 arquivos Python, 2 templates, 1 CSS).
- ✅ Dados mockados em `data.py` mantêm o protótipo auto-contido.
- ✅ Nenhuma migração de banco de dados necessária.
- ✅ O app pode ser completamente removido em 3 passos (desregistrar app, remover rota, apagar diretório).

### 6.2 Baixo risco para o TerraLab

- ✅ Alterações limitadas a 4 arquivos existentes (settings.py, urls.py, requirements.txt, STATICFILES_DIRS), todas aditivas.
- ✅ Nenhum arquivo do GeoNode é modificado.
- ✅ O app `ieb` não sofre alterações.
- ✅ Em caso de falha, basta comentar a rota `/danida/` e o resto do sistema segue funcionando.

### 6.3 Código organizado

- ✅ Separação clara: `views.py` (Django), `dash_apps.py` (Dash), `data.py` (dados mockados), `services.py` (futuro: dados reais).
- ✅ Templates isolados em `danida_dashboards/templates/danida_dashboards/`.
- ✅ Estáticos isolados em `danida_dashboards/static/danida_dashboards/`.
- ✅ URL namespace `danida_dashboards` evita colisões.

### 6.4 Separação entre dados, visualização e templates

```
data.py / services.py     →  Camada de dados (mockados ou ORM)
       ↓
dash_apps.py              →  Camada de visualização (Dash/Plotly)
       ↓
views.py + templates/     →  Camada de apresentação (Django)
```

### 6.5 Compatibilidade com deploy em Docker

- ✅ Todas as dependências são declaradas em `requirements.txt`.
- ✅ `dpd-static-support` resolve assets do Dash via `collectstatic`.
- ✅ Modo WSGI (iframe) não exige mudanças no `docker-compose.yml`.
- ✅ Volume mount de desenvolvimento permite iteração rápida (apenas restart do uWSGI).

### 6.6 Apresentação sem dados sensíveis

- ✅ Na Fase 1, todos os dados são mockados — zero risco de exposição.
- ✅ Na Fase 2, a view pode ser protegida com `@login_required` e restrita a grupos específicos.
- ✅ O template pode incluir um banner "DADOS MOCKADOS — PROTÓTIPO" para evitar confusão.

---

## 7. Entregáveis e Plano de Implementação

### 7.1 Etapas

- [ ] **Etapa 0 — Setup inicial (15 min)**
  - Adicionar `danida_dashboards` e `django_plotly_dash` a `INSTALLED_APPS` em `src/terralab_v2/settings.py:72-73`
  - Adicionar `STATICFILES_DIRS` para o novo app em `src/terralab_v2/settings.py:80-83`
  - Adicionar `PLOTLY_DASH` config ao final de `settings.py`
  - Adicionar rotas em `src/terralab_v2/urls.py:33-39`
  - Adicionar dependências em `src/requirements.txt`
  - Executar `pip install -r requirements.txt` e `python manage.py collectstatic --noinput`

- [ ] **Etapa 1 — Estrutura do app (10 min)**
  - Criar diretório `src/danida_dashboards/`
  - Criar `__init__.py`, `apps.py` (DanidaDashboardsConfig), `urls.py`, `views.py`
  - Criar `templates/danida_dashboards/base.html` e `index.html`
  - Criar `static/danida_dashboards/css/dashboard.css`

- [ ] **Etapa 2 — Dados mockados (20 min)**
  - Criar `data.py` com função `get_mock_data()` retornando DataFrames para:
    - Registros por tipo de indicador (bar chart)
    - Evolução temporal mensal (line chart)
    - Distribuição por território (treemap)

- [ ] **Etapa 3 — App Dash com 3 gráficos (30 min)**
  - Criar `dash_apps.py` com app `DjangoDash('DanidaDashboard')`
  - Implementar layout Bootstrap com 3 gráficos Plotly Express
  - Configurar `external_stylesheets=[dbc.themes.BOOTSTRAP]`

- [ ] **Etapa 4 — View Django + template (10 min)**
  - Implementar `dashboard_view` com `@login_required`
  - Template `index.html` usando `{% plotly_app name='DanidaDashboard' %}`
  - Template `base.html` com `{% plotly_header %}` e `{% plotly_footer %}`

- [ ] **Etapa 5 — Teste local e ajustes (15 min)**
  - Subir container Django e acessar `/danida/dashboard/`
  - Verificar renderização dos 3 gráficos
  - Ajustar cores, títulos e layout conforme necessário
  - Confirmar que o restante do GeoNode não foi afetado

- [ ] **Etapa 6 — Documentação interna (10 min)**
  - Adicionar docstring em cada módulo Python
  - Comentar `data.py` indicando onde conectar dados reais futuramente
  - Incluir banner "PROTÓTIPO — DADOS MOCKADOS" no template

### 7.2 Lista de arquivos a criar/alterar

| Ação | Arquivo |
|---|---|
| **Criar** | `src/danida_dashboards/__init__.py` |
| **Criar** | `src/danida_dashboards/apps.py` |
| **Criar** | `src/danida_dashboards/urls.py` |
| **Criar** | `src/danida_dashboards/views.py` |
| **Criar** | `src/danida_dashboards/data.py` |
| **Criar** | `src/danida_dashboards/dash_apps.py` |
| **Criar** | `src/danida_dashboards/templates/danida_dashboards/base.html` |
| **Criar** | `src/danida_dashboards/templates/danida_dashboards/index.html` |
| **Criar** | `src/danida_dashboards/static/danida_dashboards/css/dashboard.css` |
| **Criar** | `src/danida_dashboards/tests.py` |
| **Alterar** | `src/terralab_v2/settings.py` (linhas 72-73, 80-83, + config PLOTLY_DASH) |
| **Alterar** | `src/terralab_v2/urls.py` (linhas 33-39) |
| **Alterar** | `src/requirements.txt` |

### 7.3 Exemplo de código inicial — `dash_apps.py`

```python
"""
App Dash para o Dashboard DANIDA — Protótipo Inicial.
Utiliza django-plotly-dash no modo iframe (compatível com WSGI/uWSGI).
Dados mockados em data.py; substituir por services.py na Fase 2.
"""
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
from .data import get_mock_data

# Inicialização
app = DjangoDash('DanidaDashboard', external_stylesheets=[dbc.themes.BOOTSTRAP])

# Dados
df_tipos, df_temporal, df_territorios = get_mock_data()

# Gráfico 1: Barras — Registros por tipo de indicador
fig_tipos = px.bar(
    df_tipos,
    x='tipo', y='total',
    color='tipo',
    title='Registros por Tipo de Indicador DANIDA',
    labels={'tipo': 'Tipo', 'total': 'Quantidade'},
    color_discrete_sequence=px.colors.qualitative.Set2,
)

# Gráfico 2: Linhas — Evolução temporal
fig_temporal = px.line(
    df_temporal,
    x='mes', y='total',
    color='tipo',
    title='Evolução Mensal de Coletas',
    labels={'mes': 'Mês', 'total': 'Registros', 'tipo': 'Indicador'},
    markers=True,
)

# Gráfico 3: Treemap — Distribuição por território
fig_territorios = px.treemap(
    df_territorios,
    path=['territorio', 'tipo'],
    values='total',
    title='Distribuição por Território e Tipo',
    color='territorio',
    color_discrete_sequence=px.colors.qualitative.Pastel,
)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard DANIDA — Indicadores", className="text-center my-4"), width=12),
    ]),
    dbc.Alert("⚠️ PROTÓTIPO — Dados mockados para demonstração.", color="warning", className="text-center"),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_tipos), md=6),
        dbc.Col(dcc.Graph(figure=fig_temporal), md=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_territorios), md=12),
    ]),
], fluid=True)
```

### 7.4 Exemplo de código inicial — `data.py`

```python
"""
Dados mockados para o protótipo do Dashboard DANIDA.
Representam indicadores dos 5 tipos: fundos, area, organizacoes, pessoas, planos.

Na Fase 2, substituir por services.py que consulta ieb.models via Django ORM.
"""
import pandas as pd

def get_mock_data():
    """Retorna DataFrames mockados para os 3 gráficos do protótipo."""

    # Gráfico 1: Registros por tipo de indicador
    df_tipos = pd.DataFrame({
        'tipo': ['Fundos', 'Área', 'Organizações', 'Pessoas', 'Planos'],
        'total': [2, 8, 5, 45, 3],
    })

    # Gráfico 2: Evolução temporal (12 meses, 5 tipos)
    meses = pd.date_range('2025-01-01', periods=12, freq='ME')
    dados_temporal = []
    for tipo, base in [('Fundos', 0.1), ('Área', 0.5), ('Organizações', 0.3),
                        ('Pessoas', 3.0), ('Planos', 0.2)]:
        for i, mes in enumerate(meses):
            dados_temporal.append({
                'mes': mes,
                'tipo': tipo,
                'total': int(base * (i + 1) + (i % 3)),
            })
    df_temporal = pd.DataFrame(dados_temporal)

    # Gráfico 3: Distribuição por território
    df_territorios = pd.DataFrame({
        'territorio': [
            'TI Rio Branco', 'TI Rio Branco', 'TI Rio Branco',
            'TI Sete de Setembro', 'TI Sete de Setembro',
            'TI Zoró', 'TI Zoró',
            'TI Aripuanã', 'TI Aripuanã',
            'TI Parque do Xingu', 'TI Parque do Xingu',
        ],
        'tipo': [
            'Área', 'Pessoas', 'Organizações',
            'Pessoas', 'Planos',
            'Área', 'Pessoas',
            'Pessoas', 'Área',
            'Organizações', 'Pessoas',
        ],
        'total': [3, 12, 2, 8, 1, 2, 6, 9, 1, 3, 10],
    })

    return df_tipos, df_temporal, df_territorios
```

### 7.5 Comandos básicos

```bash
# 1. Instalar dependências
cd codigo/terralab_v2/src
pip install -r requirements.txt

# 2. Coletar estáticos do Dash
python manage.py collectstatic --noinput

# 3. Iniciar servidor de desenvolvimento
python manage.py runserver 0.0.0.0:8000

# 4. Acessar no navegador
# http://localhost:8000/danida/dashboard/

# 5. Com Docker (após rebuild)
docker compose build django
docker compose up -d django
docker compose exec django python manage.py collectstatic --noinput
```

---

## 8. Riscos e Limitações do django-plotly-dash

| Risco | Gravidade | Mitigação |
|---|---|---|
| **Modo iframe sem callbacks WebSocket**: dashboards puramente estáticos no iframe; sem interatividade server-side | Média | Aceitável para o protótipo; callbacks podem ser simulados com recarga da página ou evoluídos para ASGI na Fase 2 |
| **Conflito de versões com GeoNode**: django-plotly-dash depende de Django 3.2+ e pode conflitar com dependências do GeoNode 4.4.1 | Baixa | GeoNode 4.4.1 usa Django 4.x, compatível; testar `pip install` antes de commit |
| **Peso de assets Dash**: ~5 MB de JavaScript adicionais carregados na página | Baixa | O Nginx já serve estáticos com compressão; impacto desprezível para carga esperada |
| **Ausência de ASGI**: impossibilidade de usar callbacks com estados compartilhados entre sessões | Média | Para o protótipo inicial, dados mockados e estáticos eliminam essa necessidade |
| **Manutenção futura**: django-plotly-dash tem comunidade menor que Plotly.py puro | Baixa | A alternativa de fallback (Plotly.py direto) está documentada e é simples de migrar |
| **Template base do GeoNode**: o dashboard pode herdar CSS/JS conflitantes se estender templates GeoNode | Baixa | Recomendação: usar template base standalone no protótipo; integrar ao layout GeoNode posteriormente |

---

## 9. Resumo para Decisão

O plano acima propõe criar um app Django `danida_dashboards` com as seguintes características:

- **Tempo estimado**: ~2 horas para o protótipo completo (Etapas 0–6).
- **Arquivos criados**: 10 novos arquivos dentro do diretório do app.
- **Arquivos alterados**: 3 arquivos existentes, apenas com adições (sem alteração de comportamento).
- **Risco para o GeoNode**: Nulo — zero alterações no core.
- **Removibilidade**: Total — basta comentar a rota e remover o diretório.
- **Caminho de evolução**: Claro e documentado, de dados mockados para dados reais do banco.
- **Apresentabilidade**: Pronto para demonstração a parceiros com dados não sensíveis.

**Recomendação**: Prosseguir com o protótipo usando django-plotly-dash em modo iframe. Se durante a implementação o overhead do Dash se mostrar excessivo para o ganho percebido, migrar para a alternativa Plotly.py direto (etapa adicional de ~30 minutos).
