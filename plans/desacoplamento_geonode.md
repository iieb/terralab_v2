# Plano: Desacoplamento GeoNode — Projeto Django Autônomo

> Criado em 2026-05-05.
> Análise completa e avaliação Wagtail em `analise_arquitetural_geonode_wagtail_v1.md`.

---

## Contexto

O app `ieb` tem ZERO dependências diretas do GeoNode (models, views, forms, signals são Django puro). O acoplamento existe apenas nos dois arquivos de configuração do projeto (`settings.py` e `urls.py`). O GeoNode carrega ~30 apps desnecessárias, exige um container GeoServer com 4GB de RAM JVM que não é utilizado, e bloqueia a evolução independente do sistema.

**Objetivo:** extrair o app `ieb` para um projeto Django autônomo, rodando em ambiente paralelo ao GeoNode atual. O GeoNode permanece em produção enquanto o novo projeto é validado. A virada acontece quando o novo ambiente estiver comprovado.

**Princípio:** nenhuma mudança em produção até a validação completa estar feita.

---

## Arquitetura do ambiente paralelo

```
[Produção atual]                    [Novo projeto — em desenvolvimento]
 GeoNode + ieb                       Django puro + ieb
 docker-compose.yml (existente)      docker-compose.ieb.yml (novo)
 porta 80 (nginx atual)              porta 8100 (nginx novo, local/staging)
 banco: terralab_v2                  banco: terralab_v2 (mesmo, leitura compartilhada)
                                     ou: terralab_v2_dev (cópia para testes)
```

Os dois ambientes coexistem. O novo não toca nos dados de produção durante o desenvolvimento. A virada de produção é um único passo final com rollback imediato disponível.

---

## Pré-requisitos obrigatórios (fazer antes de qualquer código)

### P1 — Auditar AUTH_USER_MODEL no banco de produção

`LeiHistorico.usuario` e `PlanoHistorico.usuario` usam FK para `settings.AUTH_USER_MODEL`.
Se o modelo atual for `geonode.people.Profile` (não `auth.User`), a mudança de auth exige data migration.

```bash
docker compose exec db psql -U terralab_v2 terralab_v2 -c "
  SELECT app_label, model FROM django_content_type 
  WHERE app_label IN ('people', 'auth') AND model IN ('profile', 'user');
"

# Verificar qual tabela os IDs referenciam:
docker compose exec db psql -U terralab_v2 terralab_v2 -c "
  SELECT user_id FROM ieb_planohistorico LIMIT 5;
"
# Cruzar com: SELECT id, username FROM auth_user LIMIT 10;
#         e:  SELECT id, username FROM people_profile LIMIT 10;
```

**Resultado esperado:** se os user_ids existem em `auth_user`, auth.User é o model real → sem data migration.
**Se existem em `people_profile`:** requer step adicional de data migration antes da virada.

### P2 — Verificar o mapa em apresentacao_moore.html

Confirmar se o JavaScript do template faz chamadas HTTP ao GeoServer local ou usa apenas dados embutidos.

```bash
grep -n "geoserver\|WMS\|WFS\|localhost:8080\|/geoserver" \
  src/ieb/templates/apresentacao_moore.html \
  src/terralab_v2/static/ieb/js/script.js 2>/dev/null
```

**Se houver chamadas ao GeoServer:** o template precisa ser adaptado antes da virada (substituir por endpoint Django que serve GeoJSON).
**Se não houver:** o mapa funciona sem GeoServer. Remover apenas o container.

### P3 — Inventariar usuários e permissões ativos

```bash
docker compose exec db psql -U terralab_v2 terralab_v2 -c "
  SELECT COUNT(*) FROM auth_user WHERE is_active = true;
  SELECT COUNT(*) FROM auth_user WHERE is_staff = true;
"
```

Documentar grupos e permissões que a equipe usa no admin atual.

---

## Fase 1 — Novo projeto Django (estrutura base)

**Duração estimada: 2-3 dias**
**Resultado:** projeto Django rodando localmente sem nenhum vestígio do GeoNode, apontando para um banco de desenvolvimento.

### 1.1 — Criar estrutura do novo projeto

O novo projeto vive como um branch (`standalone-django`) no mesmo repositório, ou em um diretório separado. A estrutura mínima:

```
ieb_standalone/           # novo diretório raiz (ou branch)
  manage.py
  requirements.txt        # limpo, sem GeoNode
  .env.example
  docker/
    Dockerfile
    nginx.conf
    entrypoint.sh
  docker-compose.ieb.yml
  src/
    ieb_project/          # configuração do projeto (substitui terralab_v2/)
      __init__.py
      settings.py
      urls.py
      celery.py
      wsgi.py
    ieb/                  # app copiado de src/ieb/ sem modificações
```

### 1.2 — requirements.txt limpo

Remover `GeoNode==4.4.1` e todas as dependências exclusivas do GeoNode. Manter:

```
Django==4.2.*
psycopg2-binary
Pillow
celery
django-celery-beat
django-celery-results
kombu
xhtml2pdf           # geração de PDF
django-allauth      # autenticação (independente do GeoNode)
# NÃO incluir: GeoNode, GeoServer REST, Haystack, owslib, pycsw, MapStore
```

**Nota sobre PostGIS:** `django.contrib.gis` pode permanecer em `INSTALLED_APPS` para compatibilidade com migrations existentes que referenciam o engine PostGIS, mesmo sem campos geoespaciais ativos. O engine `django.contrib.gis.db.backends.postgis` funciona com PostgreSQL+PostGIS sem GeoNode.

### 1.3 — settings.py Django puro

Construir do zero (sem herdar do GeoNode). Seções obrigatórias:

```python
# ieb_project/settings.py

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',      # manter para migrations existentes
    'allauth',
    'allauth.account',
    'django_celery_beat',
    'django_celery_results',
    'ieb',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': '5432',
    }
}

AUTH_USER_MODEL = 'auth.User'           # confirmar com P1 antes de fixar
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/ieb/'

# MEDIA, STATIC, EMAIL, CELERY, CACHES — valores do .env
```

### 1.4 — urls.py Django puro

```python
# ieb_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ieb/', include('ieb.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 1.5 — Limpeza mínima no app ieb (sem quebrar nada)

Uma única mudança no código do app:

```python
# ieb/models.py linha 7 — remover import não utilizado
# ANTES: from django.contrib.gis.db import models as gis_models
# DEPOIS: (linha removida)
```

Nenhuma outra mudança em `models.py`, `views.py`, `forms.py`, `admin.py`, `signals.py`.

**Critério de sucesso da Fase 1:**
```bash
python manage.py check          # sem erros
python manage.py showmigrations # todas as migrations do ieb aparecem
python manage.py runserver      # sobe sem erro na porta configurada
```

---

## Fase 2 — Docker do ambiente paralelo

**Duração estimada: 2-3 dias**
**Resultado:** novo ambiente Docker rodando em paralelo com o GeoNode, apontando para banco de desenvolvimento, acessível em porta local separada.

### 2.1 — Dockerfile sem geonode-base

```dockerfile
FROM python:3.10-slim

# Dependências do sistema para PostGIS e Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

### 2.2 — docker-compose.ieb.yml

Serviços necessários (sem GeoServer, sem data-dir-conf, sem segundo banco):

```yaml
services:
  django-ieb:
    build: .
    environment:
      - POSTGRES_DB=terralab_v2_dev    # banco de desenvolvimento (cópia)
      - POSTGRES_HOST=db-ieb
    depends_on:
      db-ieb:
        condition: service_healthy
    ports:
      - "8001:8000"   # porta local para acesso paralelo

  db-ieb:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: terralab_v2_dev
      # ...
    healthcheck:
      test: pg_isready -U ...
    volumes:
      - dbdata-ieb:/var/lib/postgresql/data

  celery-ieb:
    build: .
    command: celery -A ieb_project worker -l info
    depends_on: [django-ieb, rabbitmq-ieb]

  rabbitmq-ieb:
    image: rabbitmq:3-alpine

  memcached-ieb:
    image: memcached:alpine

  nginx-ieb:
    image: nginx:alpine
    ports:
      - "8100:80"    # acesso HTTP paralelo
    volumes:
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf

volumes:
  dbdata-ieb:
```

### 2.3 — Banco de desenvolvimento

Criar cópia do banco de produção para desenvolvimento sem risco:

```bash
# No servidor de produção ou staging:
docker compose exec db pg_dump -U terralab_v2 terralab_v2 > backup_prod.sql

# No novo ambiente:
docker compose -f docker-compose.ieb.yml exec db-ieb \
  psql -U terralab_v2 -d terralab_v2_dev < backup_prod.sql
```

**Critério de sucesso da Fase 2:**
```bash
docker compose -f docker-compose.ieb.yml up -d
# Acessar http://localhost:8100/ieb/ → responde
# Acessar http://localhost:8100/admin/ → admin Django funcional
# Login com usuário da base copiada → funciona
```

---

## Fase 3 — Validação completa em paralelo

**Duração estimada: 3-5 dias**
**Resultado:** cada funcionalidade do `ieb` verificada e aprovada no novo ambiente.

### Checklist de validação

**Autenticação:**
- [ ] Login via `/accounts/login/` com credenciais de produção
- [ ] Logout e redirecionamento correto
- [ ] `@login_required` bloqueia acesso não autenticado
- [ ] Admin Django acessível apenas para `is_staff=True`

**Rotas ieb (todas as ~30 URLs de `ieb/urls.py`):**
- [ ] `/ieb/atividade_registro/` — formulário v1 e v2 carregam
- [ ] Endpoints AJAX: `load-componentes`, `load-atividades`, `load-subatividades`, `load-equipes`, `load-indicadores`
- [ ] Criação de AtividadeRegistro (submit completo do formulário)
- [ ] Detalhe: `/ieb/atividade_registro/<pk>/`
- [ ] Dashboards: `/ieb/monitoramento/registros/`, `/ieb/monitoramento/metas/`
- [ ] `dash_danida` carrega sem erro
- [ ] Endpoints AJAX de criação: `adicionar-parceria`, `adicionar-plano`, `adicionar-produto`, `adicionar-contrato`, `adicionar-lei`, `adicionar-modelo`
- [ ] Endpoints de atualização de situação: plano, lei, contrato

**Dados e integridade:**
- [ ] Criação de AtividadeRegistro salva todos os 16 tipos de indicadores (Pessoas, Area, Planos, etc.)
- [ ] M2M signals funcionam (Parcerias, Produtos, Contratos, Leis)
- [ ] Cálculo de `total_ha` em Area.save() funciona
- [ ] Histórico de PlanoHistorico e LeiHistorico registra mudanças

**Arquivos e mídia:**
- [ ] Upload de fotos gera thumbnail automaticamente
- [ ] Upload de lista de presença salva e link de download funciona
- [ ] `MEDIA_ROOT` configurado e arquivos acessíveis

**Email:**
- [ ] Criação de AtividadeRegistro dispara email com PDF anexado
- [ ] PDF renderiza sem erro (verificar com `MONITORING_EMAIL`)

**Mapa (apresentacao_moore.html):**
- [ ] Página carrega sem erro de console JS
- [ ] Layers aparecem no mapa (confirmar resultado do P2 — se não usa GeoServer, funciona direto)

### Problemas esperados e resoluções

| Problema | Causa provável | Resolução |
|---|---|---|
| `ImproperlyConfigured: AUTH_USER_MODEL` | Migrations antigas com referência ao `people.Profile` | Verificar resultado do P1; se necessário, adicionar data migration |
| `ModuleNotFoundError: geonode.*` | Import esquecido em algum arquivo | `grep -r "from geonode" src/ieb/` para localizar |
| `OperationalError: no postgis extension` | Banco sem extensão PostGIS | `docker compose exec db-ieb psql -c "CREATE EXTENSION postgis;"` |
| Template não encontrado | `TEMPLATES[0][DIRS]` aponta para path antigo | Ajustar `TEMPLATES` no settings.py com `BASE_DIR` correto |
| Estáticos não carregam | `STATICFILES_DIRS` ou `STATIC_ROOT` incorretos | Rodar `collectstatic` e verificar nginx config |
| Celery não processa tasks | `CELERY_BROKER_URL` apontando para host errado | Verificar `.env` e hostname do rabbitmq |

---

## Fase 4 — Preparação para virada de produção

**Duração estimada: 1-2 dias**
**Resultado:** ambiente novo pronto para receber tráfego real. Rollback garantido em < 5 minutos.

### 4.1 — Apontar para banco de produção (readonly primeiro)

Antes de qualquer virada, testar o novo projeto contra o banco real em modo read-only:

```python
# settings.py — temporário para validação
DATABASES = {
    'default': {
        # banco de produção real
        'NAME': 'terralab_v2',
        'HOST': os.environ.get('PROD_DB_HOST'),
        # ...
    }
}
```

Executar apenas operações de leitura (GET requests, dashboards) e verificar que dados reais aparecem corretamente.

### 4.2 — Plano de virada (zero downtime)

```
1. [10 min] Tirar backup completo do banco de produção
2. [5 min]  Rodar migrations do novo projeto contra banco de produção
             (as migrations do ieb são as mesmas — não há novas migrations aqui)
3. [2 min]  Redirecionar nginx da porta 80 para o novo container Django
4. [5 min]  Smoke test: login, criar um registro de teste, verificar email
5. [disponível] Rollback: redirecionar nginx de volta para o container GeoNode antigo
```

### 4.3 — Rollback garantido

O container GeoNode permanece ativo (apenas sem tráfego) por **30 dias após a virada**. Se qualquer problema for detectado, o rollback é mudar uma linha no nginx.conf e recarregar o nginx — tempo estimado: 2 minutos.

```bash
# Rollback imediato se necessário:
# Editar nginx.conf: proxy_pass de volta para django-geonode:8000
docker compose exec nginx nginx -s reload
```

---

## Fase 5 — Descomissionamento do GeoNode (após 30 dias estável)

**Duração estimada: 1 dia**

1. Confirmar que nenhum usuário depende de funcionalidade do GeoNode (layers públicos, MapStore, etc.)
2. Parar e remover containers: `geoserver`, `data-dir-conf`, `letsencrypt` (se movido para o novo stack)
3. Remover banco `terralab_v2_data` (geodatabase do GeoNode) após confirmar que está vazio ou contém apenas dados do GeoNode, não do ieb
4. Arquivar o `docker-compose.yml` original (manter no git como referência)
5. Remover `GeoNode==4.4.1` do requirements (já não está no novo projeto)
6. Fechar branch ou diretório do projeto antigo

---

## Estratégia: GeoNode como serviço externo (futuro)

Quando os modelos `TIs`, `UC`, `PA`, `TUC` receberem campos `geometry` (plano futuro: integração FUNAI/IBAMA/INCRA), a publicação de layers WMS/WFS pode ser feita com **GeoServer configurado como DataStore PostGIS**:

- GeoServer aponta diretamente para as tabelas do banco do projeto ieb via PostGIS DataStore
- Layers publicados automaticamente sem código Python adicional
- GeoServer roda como serviço separado (`docker compose --profile geo up`) sem interferir no projeto principal
- Nenhuma necessidade de reinstalar GeoNode como framework web

O desacoplamento agora cria exatamente essa arquitetura limpa: Django autônomo + GeoServer opcional.

---

## Cronograma resumido

| Fase | Atividade | Duração | Garantia |
|---|---|---|---|
| Pré-requisitos | Auditoria auth + mapa + usuários | 1 dia | Sem surpresas na implementação |
| Fase 1 | Novo projeto Django (settings + urls + app) | 2-3 dias | `manage.py check` passa |
| Fase 2 | Docker paralelo com banco dev | 2-3 dias | Stack sobe em `localhost:8100` |
| Fase 3 | Validação de todas as funcionalidades | 3-5 dias | Checklist 100% |
| Fase 4 | Virada de produção com rollback disponível | 1-2 dias | Rollback em 2 min |
| Fase 5 | Descomissionamento GeoNode | 1 dia | 30 dias após virada |

**Total: 3-4 semanas do início ao GeoNode descomissionado.**

---

## Arquivos críticos

**Projeto atual (referência/leitura):**
- [src/terralab_v2/settings.py](src/terralab_v2/settings.py) — settings a serem reescritas
- [src/terralab_v2/urls.py](src/terralab_v2/urls.py) — urls a serem reescritas
- [docker-compose.yml](docker-compose.yml) — referência para novo docker-compose
- [src/ieb/models.py](src/ieb/models.py) linha 7 — único ponto a alterar no app
- [src/ieb/templates/apresentacao_moore.html](src/ieb/templates/apresentacao_moore.html) — verificar chamadas ao GeoServer

**A criar:**
- `ieb_standalone/src/ieb_project/settings.py`
- `ieb_standalone/src/ieb_project/urls.py`
- `ieb_standalone/requirements.txt`
- `ieb_standalone/docker-compose.ieb.yml`
- `ieb_standalone/docker/Dockerfile`
