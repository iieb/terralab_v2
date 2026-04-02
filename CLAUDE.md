# terralab_v2

Sistema de gestão de dados para comunidades indígenas, construído sobre GeoNode/Django.

## Stack

- **Backend:** Django 4.2 + GeoNode 4.4 (Python 3.10)
- **DB:** PostgreSQL 15 + PostGIS
- **Tasks:** Celery + RabbitMQ
- **Cache:** Memcached
- **Geo:** GeoServer 2.24
- **Frontend:** Django templates + JS vanilla + Bootstrap
- **Infra:** Docker Compose (9 serviços), Nginx, uWSGI

## Estrutura

```
src/
  ieb/              # app principal (models, views, forms, templates, static)
  terralab_v2/      # config do projeto (settings.py, urls.py)
docker/             # configs por serviço (nginx, postgresql, geoserver)
fixtures/           # dados iniciais
```

## App `ieb` — domínios principais

- **Movimento Indígena:** OIsRegional, OIsLocal, TIs, Aldeia, Indigena, IGATI
- **Projetos:** Projeto > Componente > Atividade, Equipe, Financiador, Instituicao
- **Monitoramento:** AtividadeRegistro, Indicador, Meta, Treinados, Capacitados
- **Organizacional:** Parceria, Contrato, Lei, Produto, Plano

## Convenções

- Nomes de models e campos em **português**
- Views com sufixo `_view`; endpoints AJAX prefixados com `load_` ou hyphenated
- ForeignKey com `on_delete=CASCADE` por padrão
- `CharField(max_length=255)` como padrão para strings
- Formulários em `forms.py`; admin customizado com inlines

## Comandos úteis

```bash
# subir ambiente
docker compose up -d

# shell Django
docker compose exec django python manage.py shell

# migrations
docker compose exec django python manage.py makemigrations ieb
docker compose exec django python manage.py migrate
```

## Arquivos-chave

- `src/ieb/models.py` — modelos de dados (~750 linhas)
- `src/ieb/views.py` — views e endpoints AJAX (~1400 linhas)
- `src/ieb/forms.py` — formulários
- `src/terralab_v2/settings.py` — configurações
- `docker-compose.yml` — orquestração de serviços
- `.env` — variáveis de ambiente (não versionar)
