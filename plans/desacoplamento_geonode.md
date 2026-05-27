# Plano: Desacoplamento GeoNode — Novo Repositório Django

> Revisado em 2026-05-27.
> Contexto revisado: projeto em fase de desenvolvimento, zero dados reais em produção.
> Análise arquitetural completa em `analise_arquitetural_geonode_wagtail_v1.md`.

---

## Diagnóstico

O app `ieb` tem **zero dependências do GeoNode**. Auditoria concluída:

| Arquivo | Referências GeoNode |
|---|---|
| `ieb/models.py` | Um único import não-utilizado: `gis_models` (linha 7) |
| `ieb/views.py` | Nenhuma |
| `ieb/forms.py` | Nenhuma |
| `ieb/admin.py` | Nenhuma |
| `ieb/signals.py` | Nenhuma |

O acoplamento existe **apenas** nos arquivos de configuração do projeto (`terralab_v2/settings.py` e `terralab_v2/urls.py`), que serão substituídos integralmente no novo repositório.

**GeoServer** não é utilizado por nenhum template ou endpoint do app. O container JVM de 4 GB é desperdício puro.

---

## Contexto revisado: desenvolvimento sem dados reais

Como o projeto está em desenvolvimento e não há dados reais, toda a complexidade do plano anterior foi eliminada:

- ~~Ambiente paralelo com rollback de 30 dias~~ → não necessário
- ~~Cópia de banco de produção~~ → banco novo, migrations do zero
- ~~Auditoria de AUTH_USER_MODEL em produção~~ → `auth.User` direto, sem data migration
- ~~Fase de virada de produção~~ → o novo repositório **é** o projeto de produção
- ~~Verificação de chamadas GeoServer no mapa~~ → descartado do escopo

**O processo é:** criar o novo repositório → subir → usar.

---

## Objetivo

Criar um repositório Django autônomo (`terralab-ieb` ou nome equivalente) que:

1. Contém o app `ieb` copiado sem modificações relevantes
2. Roda sem GeoNode, GeoServer, Haystack, MapStore
3. Usa PostgreSQL + PostGIS (para compatibilidade futura com camadas TIs/UC/PA/TUC)
4. Tem Docker Compose enxuto: Django + Celery + RabbitMQ + PostgreSQL + Nginx

---

## Estrutura do novo repositório

```
terralab-ieb/
  manage.py
  requirements.txt
  .env.example
  .gitignore
  README.md
  docker-compose.yml
  docker/
    Dockerfile
    nginx/
      nginx.conf
    entrypoint.sh
  src/
    ieb_project/            ← nova config do projeto (substitui terralab_v2/)
      __init__.py
      settings.py
      urls.py
      wsgi.py
      celery.py
    ieb/                    ← app copiado de src/ieb/ com 1 linha removida
      (models, views, forms, admin, signals, urls, templates, static, migrations)
  fixtures/                 ← dados iniciais (fixtures existentes se houver)
```

---

## Passo 1 — Criar o repositório

```bash
# Opção A: novo repositório vazio
mkdir terralab-ieb && cd terralab-ieb
git init

# Opção B: branch isolado no repositório atual (testar antes de criar novo repo)
git checkout -b standalone-django
```

Criar a estrutura de diretórios:

```bash
mkdir -p src/ieb_project src/ieb docker/nginx
touch manage.py requirements.txt .env.example .gitignore docker-compose.yml
```

---

## Passo 2 — Copiar o app ieb

```bash
# De dentro de terralab_v2/
cp -r src/ieb/ ../terralab-ieb/src/ieb/
```

**Uma única alteração no app** — remover o import não utilizado em [src/ieb/models.py](src/ieb/models.py#L7):

```python
# REMOVER esta linha (linha 7 — importada mas nunca usada):
from django.contrib.gis.db import models as gis_models
```

Nenhuma outra alteração em `models.py`, `views.py`, `forms.py`, `admin.py` ou `signals.py`.

---

## Passo 3 — requirements.txt limpo

```txt
Django==4.2.*
psycopg2-binary
Pillow
celery[redis]
django-celery-beat
django-celery-results
kombu
xhtml2pdf
django-allauth
# Para PostGIS (compatibilidade futura com geometry em TIs/UC/PA/TUC):
# GDAL e dependências instaladas via Dockerfile, não via pip
```

**Fora do requirements** (não incluir):
- `GeoNode`, `owslib`, `pycsw`, `MapStore`, `Haystack`
- Qualquer pacote com prefixo `geonode-`

---

## Passo 4 — settings.py Django puro

```python
# src/ieb_project/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',          # manter: futuro geometry em TIs/UC/PA/TUC
    'allauth',
    'allauth.account',
    'django_celery_beat',
    'django_celery_results',
    'ieb',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'ieb_project.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB', 'terralab'),
        'USER': os.environ.get('POSTGRES_USER', 'terralab'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': '5432',
    }
}

AUTH_USER_MODEL = 'auth.User'      # Django padrão — sem GeoNode Profile
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/ieb/'

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'ieb' / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Celery
CELERY_BROKER_URL         = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/')
CELERY_RESULT_BACKEND     = 'django-db'
CELERY_BEAT_SCHEDULER     = 'django_celery_beat.schedulers.DatabaseScheduler'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST    = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT    = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', '')
MONITORING_EMAIL    = os.environ.get('MONITORING_EMAIL', '')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ   = True
```

---

## Passo 5 — urls.py

```python
# src/ieb_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ieb/', include('ieb.urls')),
    path('', include('ieb.urls')),  # redirecionar raiz se necessário
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Passo 6 — Dockerfile

```dockerfile
FROM python:3.10-slim

# Dependências do sistema: PostGIS + Pillow + PDF
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

ENV PYTHONPATH=/app/src
ENV DJANGO_SETTINGS_MODULE=ieb_project.settings
```

---

## Passo 7 — docker-compose.yml

```yaml
services:
  django:
    build: .
    command: >
      sh -c "python src/manage.py migrate &&
             python src/manage.py collectstatic --noinput &&
             uwsgi --ini docker/uwsgi.ini"
    env_file: .env
    volumes:
      - media:/app/media
      - static:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy

  celery:
    build: .
    command: celery -A ieb_project worker -l info
    env_file: .env
    depends_on: [django, rabbitmq]

  celery-beat:
    build: .
    command: celery -A ieb_project beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    depends_on: [django, rabbitmq]

  db:
    image: postgis/postgis:15-3.3
    env_file: .env
    environment:
      POSTGRES_DB:       ${POSTGRES_DB}
      POSTGRES_USER:     ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}"]
      interval: 5s
      retries: 10
    volumes:
      - pgdata:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static:/app/staticfiles:ro
      - media:/app/media:ro
    depends_on: [django]

volumes:
  pgdata:
  media:
  static:
```

---

## Passo 8 — Subir e validar

```bash
# 1. Copiar o .env.example e preencher as variáveis
cp .env.example .env
# Editar: SECRET_KEY, POSTGRES_PASSWORD, EMAIL_*

# 2. Subir o ambiente
docker compose up -d

# 3. Criar superuser
docker compose exec django python src/manage.py createsuperuser

# 4. Verificar
# http://localhost/admin/    → admin Django
# http://localhost/ieb/atividade_registro/    → formulário
# http://localhost/ieb/monitoramento/registros/    → dashboard
```

**Critério de sucesso:**
```bash
docker compose exec django python src/manage.py check      # sem erros
docker compose exec django python src/manage.py showmigrations  # ieb: todas aplicadas
```

---

## Checklist de validação funcional

Depois do ambiente subir, verificar as funcionalidades principais:

**Autenticação:**
- [ ] Login via `/accounts/login/`
- [ ] Admin Django acessível em `/admin/`
- [ ] `@login_required` bloqueia sem login

**Formulários e AJAX:**
- [ ] `/ieb/atividade_registro/` — formulário v1 carrega
- [ ] `/ieb/atividade_registro/v2/` — formulário v2 carrega
- [ ] AJAX: `load-componentes`, `load-atividades`, `load-subatividades`, `load-equipes`, `load-indicadores`
- [ ] Submit completo do formulário salva AtividadeRegistro + satélites

**Dashboards:**
- [ ] `/ieb/monitoramento/registros/` carrega
- [ ] `/ieb/monitoramento/metas/` carrega
- [ ] `/ieb/monitoramento/danida/` carrega

**Endpoints de adição rápida (modais):**
- [ ] `adicionar-parceria`, `adicionar-plano`, `adicionar-produto`
- [ ] `adicionar-contrato`, `adicionar-lei`, `adicionar-modelo`
- [ ] Atualização de situação: plano, lei, contrato

**Arquivos:**
- [ ] Upload de foto gera thumbnail
- [ ] Upload de lista de presença salva e download funciona

**Email:**
- [ ] Criação de registro dispara email com PDF (testar com `EMAIL_BACKEND = console` primeiro)

---

## Problemas esperados e resoluções rápidas

| Sintoma | Causa provável | Resolução |
|---|---|---|
| `ModuleNotFoundError: gis_models` | Import esquecido em models.py | Remover linha 7 de `ieb/models.py` |
| `OperationalError: no postgis extension` | Banco sem PostGIS | `docker compose exec db psql -U ... -c "CREATE EXTENSION postgis;"` |
| Template não encontrado | `TEMPLATES[DIRS]` incorreto | Ajustar `BASE_DIR` no settings.py |
| Estáticos 404 | `collectstatic` não rodou ou `STATICFILES_DIRS` errado | Rodar `collectstatic` e verificar nginx |
| Celery não processa | `CELERY_BROKER_URL` apontando host errado | Verificar `.env` — hostname deve ser `rabbitmq` |
| `allauth` erro de URL | Middleware `AccountMiddleware` ausente | Adicionar `allauth.account.middleware.AccountMiddleware` em `MIDDLEWARE` |

---

## Cronograma

| Passo | Atividade | Estimativa |
|---|---|---|
| 1–2 | Criar repositório + copiar app | 30 min |
| 3–5 | requirements + settings + urls | 1–2 h |
| 6–7 | Dockerfile + docker-compose | 1–2 h |
| 8 | Subir ambiente + verificar `manage.py check` | 30 min |
| Checklist | Validação funcional completa | 1 dia |

**Total: 1–2 dias de trabalho efetivo.**

---

## Próximos passos após desacoplamento

1. **Fixtures de dados iniciais:** exportar dados de referência do banco atual (OIsRegional, TIs, Financiadores, Projetos, Indicadores) com `dumpdata` e incluir no novo repositório.
2. **API REST (DRF):** com o projeto limpo, implementar serializers — ver `project_drf_priority.md`.
3. **GIS futuro:** quando TIs/UC/PA/TUC receberem campos `geometry`, o `django.contrib.gis` já está configurado; adicionar GeoServer como serviço separado sem reinstalar GeoNode.

---

## Arquivos críticos no projeto atual (referência para a migração)

- [src/ieb/models.py](src/ieb/models.py) — linha 7: único ponto a alterar no app
- [src/ieb/views.py](src/ieb/views.py) — copiar sem alterações
- [src/ieb/forms.py](src/ieb/forms.py) — copiar sem alterações
- [src/ieb/urls.py](src/ieb/urls.py) — copiar sem alterações
- [src/ieb/templates/](src/ieb/templates/) — copiar integralmente
- [src/ieb/static/](src/ieb/static/) — copiar integralmente
- [src/ieb/migrations/](src/ieb/migrations/) — copiar integralmente
- [src/terralab_v2/settings.py](src/terralab_v2/settings.py) — **substituir** pelo novo settings.py acima
- [src/terralab_v2/urls.py](src/terralab_v2/urls.py) — **substituir** pelo novo urls.py acima
