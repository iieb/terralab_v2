# Análise Arquitetural: Desacoplamento GeoNode + Avaliação Wagtail (v1 — arquivo)

> Arquivo gerado em 2026-05-05. Documento de referência para decisões arquiteturais.
> O plano de implementação do desacoplamento está em `desacoplamento_geonode.md`.
> A análise Wagtail permanece aqui como referência para decisão futura.

---

## Contexto

O app `ieb` está acoplado ao GeoNode como framework base do projeto, mas esse acoplamento é **superficial e concentrado em apenas dois arquivos de configuração**. O GeoNode foi adotado como plataforma geo, mas na prática o `ieb` não usa GeoServer, não usa campos geoespaciais, e carrega ~30 apps desnecessárias em memória. O objetivo é desacoplar para ganhar autonomia de evolução (sem depender do ciclo de release do GeoNode), reduzir overhead operacional, e preparar a base para adoção do Wagtail como ferramenta de gestão de informação e colaboração.

---

## Estado Atual (descobertas da análise)

### Acoplamento GeoNode — inventário completo

| Local | Acoplamento |
|---|---|
| `src/terralab_v2/settings.py` linha 44 | `from geonode.settings import *` (fallback quando não há `local_settings.py`) |
| `src/terralab_v2/urls.py` linha 21 | `from geonode.urls import urlpatterns` |
| `src/ieb/models.py` linha 7 | `from django.contrib.gis.db import models as gis_models` — importado mas **nunca usado** |
| `requirements.txt` | `GeoNode==4.4.1` |

**O app `ieb` em si tem ZERO dependências do GeoNode**: nenhum import em `views.py`, `forms.py`, `admin.py`, `signals.py`. Todos os models herdam de `models.Model` Django puro.

### GeoServer — uso real: nenhum

- Container consome `GEOSERVER_JAVA_OPTS=-Xms4G -Xmx4G` (4GB RAM base)
- `ieb` não faz requisições WMS/WFS
- Mapa em `apresentacao_moore.html` usa Leaflet + dados hardcoded, sem chamada ao GeoServer local
- `TIs`, `UC`, `PA`, `TUC`: armazenam apenas `area` (FloatField), sem campos de geometry

### Mecanismo de desacoplamento já existe

```python
# settings.py linhas 40-44
try:
    from terralab_v2.local_settings import *   # ← prioridade
except ImportError:
    from geonode.settings import *              # ← fallback atual
```

### Formulários narrativos — limitação atual

| Campo | Tipo atual | Problema |
|---|---|---|
| `desafios`, `propostas`, `sucesso`, `melhores_praticas` | `CharField(max_length=255)` | Narrativas de campo truncadas em 255 chars |
| `descricao`, `comentarios` | `TextField()` | Sem limite, sem markup |

---

## Análise Técnica: Desacoplamento GeoNode

### Ganhos concretos

- **4GB+ de RAM liberados** (GeoServer JVM)
- Eliminação de 3 containers desnecessários: `geoserver`, `data-dir-conf`, segundo banco `terralab_v2_data`
- Redução de ~30 apps no `INSTALLED_APPS` → boot mais rápido, admin mais limpo
- Controle total sobre autenticação, middleware, logging e URLs
- Ciclo de atualização independente do GeoNode
- Base limpa para adicionar Wagtail, DRF e outros pacotes sem conflitos

### Riscos críticos

**Risco 1 (alto): AUTH_USER_MODEL**
`LeiHistorico.usuario` e `PlanoHistorico.usuario` referenciam `settings.AUTH_USER_MODEL`. Se o modelo atual é `geonode.people.Profile` (não `auth.User`), a migração exige data migration cuidadosa.

**Risco 2 (médio): mapa `apresentacao_moore.html`**
O template carrega layers por nome via Leaflet/JS. Verificar se o JS faz chamadas ao GeoServer local antes de desligar o container.

**Risco 3 (médio): Dockerfile baseado em `geonode/geonode-base`**
Mudar para imagem Python pura requer instalar explicitamente GDAL, libpq-dev, bindings PostGIS.

**Risco 4 (baixo): fixture `django_celery_beat.json`**
Contém `"task": "geonode.security.tasks.synch_guardian"`. Substituir/remover ao desacoplar.

---

## Análise Técnica: Integração Wagtail

### Campos com potencial Wagtail — mapeamento completo

| Modelo | Campo | Tipo atual | Problema |
|---|---|---|---|
| `AtividadeRegistro` | `desafios` | CharField(255) | Truncado em 255 chars |
| `AtividadeRegistro` | `propostas` | CharField(255) | Truncado em 255 chars |
| `AtividadeRegistro` | `sucesso` | CharField(255) | Truncado em 255 chars |
| `AtividadeRegistro` | `melhores_praticas` | CharField(255) | Truncado em 255 chars |
| `AtividadeRegistro` | `descricao` | TextField | Sem limite, mas sem markup |
| `AtividadeRegistro` | `comentarios` | TextField | Sem limite, sem auditoria |
| `Programa` | `descricao` | TextField | Editado só via admin |
| `AreaTematica` | `descricao` | TextField | Editado só via admin |
| `Atividade` | `descricao` | CharField(255) | Truncado |
| `Indicador` | `descricao` | CharField(255) | Truncado |

**Modelos estruturais (`Produto`, `Plano`, `Lei`, `Contrato`, `Parceria`)** — não têm campos narrativos. São apenas identificadores e estados. **Sem ganho em Wagtail.**

**Arquivos e documentos existentes:**

| Modelo | Campo | Problema atual |
|---|---|---|
| `AtividadeRegistroFoto` | `foto` + `foto_thumbnail` | Thumbnail manual via PIL; sem título/descrição; sem categorização |
| `AtividadeRegistroListaPresenca` | `arquivo` | FileField simples; sem metadata; sem link a múltiplos registros |

### Arquitetura recomendada: CMS complementar, não substituto

```
/admin/   → Django admin: dados operacionais (Projetos, Indicadores, Metas, TIs...)
/cms/     → Wagtail admin: conteúdo narrativo, mídia, documentos
```

### Padrão recomendado: Snippets + StreamField (não Pages)

- Registrar `AtividadeRegistro` como **Wagtail Snippet** (`@register_snippet`)
- Converter os 4 campos narrativos de 255 chars para **`StreamField([('texto', RichTextBlock())])`**
- Adicionar **`RevisionMixin`** para versionamento de edições
- Opcional: **`WorkflowMixin`** para fluxo draft → revisão → aprovado

### Ganhos concretos por área

**1. Campos narrativos de AtividadeRegistro**

| Funcionalidade | Hoje | Com Wagtail Snippet + StreamField |
|---|---|---|
| Limite de texto | 255 chars | Ilimitado |
| Markup | Plain text | Bold, itálico, listas, links, imagens inline |
| Versionamento | Nenhum | Revisões com autoria + data |
| Workflow | Submit direto | Draft → Em revisão → Aprovado |
| Interface | Textarea simples | Editor Draftail |

**2. Gestão de fotos**

| Funcionalidade | Hoje | Com wagtailimages.Image |
|---|---|---|
| Thumbnail | Manual via PIL | Automático com rendições |
| Metadata | Nenhum | Título, alt text, tags |
| Busca | Impossível | Full-text por título/tag |

**3. Gestão de documentos**

| Funcionalidade | Hoje | Com wagtaildocs.Document |
|---|---|---|
| Metadata | Apenas arquivo | Título, tags, coleção |
| Busca | Impossível | Por título e tags |

**4. Relatórios colaborativos (potencial futuro)**

Wagtail Pages com dados dinâmicos para relatórios periódicos por projeto/financiador, editados colaborativamente pela equipe.

### O que Wagtail não resolve

- Dados estruturados e contabilização de indicadores — responsabilidade do Django ORM
- Formulário multi-step de campo — o stepper v2 é mais adequado para captura
- Permissões de dados por projeto/programa — responsabilidade do Django

### Wagtail só funciona bem após o desacoplamento do GeoNode

Wagtail + GeoNode simultâneos geram conflitos estruturais de autenticação, INSTALLED_APPS e interfaces de admin. **Sequência obrigatória: desacoplamento GeoNode primeiro.**

### Alternativa simples (se Wagtail for adiado)

```python
desafios = models.TextField(blank=True)
propostas = models.TextField(blank=True)
sucesso = models.TextField(blank=True)
melhores_praticas = models.TextField(blank=True)
```

**Wagtail vale o investimento** quando houver demanda real por: formatação rich text, histórico auditável de edições, workflow de revisão/aprovação, ou relatórios colaborativos como documentos vivos.

---

## Estratégia: GeoNode como serviço externo (futuro)

Quando `TIs`, `UC`, `PA`, `TUC` receberem campos `geometry`, a publicação WMS/WFS pode usar **GeoServer com DataStore PostGIS** apontando diretamente para o banco do terralab_v2 — sem reinstalar GeoNode como framework web.

---

## Arquivos críticos

- [src/terralab_v2/settings.py](src/terralab_v2/settings.py)
- [src/terralab_v2/urls.py](src/terralab_v2/urls.py)
- [src/ieb/models.py](src/ieb/models.py)
- [src/ieb/views.py](src/ieb/views.py) — `_atividade_registro_process()` (~linha 492)
- [src/ieb/forms.py](src/ieb/forms.py)
- [docker-compose.yml](docker-compose.yml)
- [src/ieb/templates/apresentacao_moore.html](src/ieb/templates/apresentacao_moore.html)
