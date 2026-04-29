# Plano Cirurgico v1.3 -- Indice de Tarefas

> **Origem:** `plans/2026-04-22-plano-cirurgico-priorizado-src-ieb-models-1.3.md`
> **Data:** 2026-04-27 | **Total:** 29 tarefas | **Migrations:** ~27
> **Revisao tecnica:** 2026-04-27 — correcoes C1-C5, A1-A7, M1-M4 aplicadas nos arquivos de ondas.
> **Ambiente local:** Docker/GeoNode validado em 2026-04-27 antes do inicio das subtasks.

---

## Registro de preparacao do ambiente local

Antes de iniciar qualquer subtask, o ambiente Docker local foi preparado e validado no estado atual do codigo.

| Item | Resultado |
|------|-----------|
| Arquivo `.env` | Gerado com `create-envfile.py` em modo `dev`, hostname `localhost` |
| Docker Compose | Configuracao validada com sucesso apos gerar `.env` |
| GeoNode/Nginx | `http://localhost/` respondeu HTTP 200 |
| GeoServer via proxy | `http://localhost/geoserver/` respondeu HTTP 302 para `/geoserver/index.html` |
| GeoServer direto | `http://localhost:8080/geoserver/` respondeu HTTP 302 |
| Rota customizada IEB | `http://localhost/ieb/atividade_registro/v2/` respondeu HTTP 200 |
| Django check | `python manage.py check` executado no container sem issues |

Observacoes operacionais:

- O terminal pode aparentar travar durante `docker compose up -d --build`, pois o build/startup do GeoNode e demorado.
- Se `geoserver` ou `celery` ficarem em estado `Created`, iniciar explicitamente com `docker compose up -d geoserver celery`.
- Se o proxy `/geoserver/` retornar 502 apos o GeoServer subir, reiniciar o Nginx com `docker compose restart geonode` para renovar a resolucao DNS interna.
- `letsencrypt` pode ficar reiniciando com `LETSENCRYPT_MODE=disabled`; isso e ruido esperado no ambiente HTTP local e nao bloqueia os testes.

---

## Registro das correcoes da revisao tecnica

As correcoes abaixo foram incorporadas nos arquivos executaveis das ondas em `plans/tarefas/`. Este registro serve como checklist obrigatorio antes de implementar codigo.

| ID | Severidade | Arquivo de tarefa | Decisao documentada |
|----|------------|-------------------|---------------------|
| C1 | Critica | `onda-1-correcoes-pontuais.md` | Onde o model nao tem `class Meta`, a tarefa manda **CRIAR** `class Meta`; `Mobilizados` preserva a `Meta` existente. |
| C2 | Critica | `onda-2-constraints-satelites.md` | T-2.2 separa Grupo A com `unique_together` existente e Grupo B sem `unique_together`; nao remover constraint inexistente. |
| C3 | Critica | `onda-3-sinais-m2m.md` | Em `Area` e `AreasProtegidas`, manter o primeiro `super().save()` para obter PK; mover apenas calculos para signals. |
| C4 | Critica | `onda-4-coerencia-dominio.md` | `Planos.save()` deve aceitar `usuario=None`; views passam `request.user`; sem usuario, gravar `None`. |
| C5 | Critica | `onda-5-qualidade-arquitetural.md` | Constantes transversais devem ir para `src/ieb/constants.py` para reduzir dependencia circular. |
| A1 | Alta | `onda-1-correcoes-pontuais.md` | Corrigida justificativa de `Evento.total`: problema e filtro falsy (`None` e `0`), nao soma de zeros em si. |
| A2 | Alta | `onda-1-correcoes-pontuais.md` | `Contratos.save()` deve usar `aggregate(... )['total'] or 0`. |
| A3 | Alta | `onda-2-constraints-satelites.md` | `DESAG_FIELDS` e lista; adicionar string `desag_org_governo`, alem de POST, config e admin. |
| A4 | Alta | `onda-4-coerencia-dominio.md` | Roll-up em `Meta.realizado` deve ser cirurgico; nao reescrever metodo inteiro. |
| A5 | Alta | `onda-4-coerencia-dominio.md` | `LeiHistorico.usuario` e `PlanoHistorico.usuario` usam `max_length=255` no estado atual; migration deve refletir campo real. |
| A6 | Alta | `onda-4-coerencia-dominio.md` | `Outro` nao esta registrado no admin; nenhuma remocao de admin e necessaria. |
| A7 | Alta | `bonus-planos-financiador.md` | Usar roteamento existente com marcador `is_fin`; evitar mapa paralelo desnecessario. |
| M1 | Media | `onda-2-constraints-satelites.md` | Testar explicitamente `Pessoas(total_pessoas=0, homens=None).save()` como caso OK em Postgres. |
| M2 | Media | `onda-5-qualidade-arquitetural.md` | Depois de `DecimalField`, usar `Decimal('0')` em agregacoes de area; nao usar `0.0`. |
| M3 | Media | `onda-5-qualidade-arquitetural.md` | Thumbnail via Celery deve usar `transaction.on_commit(...)`. |
| M4 | Media | `final-documentacao.md` | `FOCO_CHOICES` documentado com valores reais: `governanca`, `implementacao`, `ativ_prod`. |

---

## Regras operacionais para agentes de IA

| # | Regra |
|---|-------|
| 1 | Indexar codigo antes de implementar |
| 2 | Uma migration por tarefa, um arquivo por tarefa |
| 3 | Simples: direto. Complexo: `muse` planeja, `forge` executa |
| 4 | Cada tarefa e um sub-agente independente |
| 5 | Tarefas sem dependencia disparam em paralelo |

---

## Estrutura de arquivos

```
plans/tarefas/
  PLANO_CIRURGICO_TAREFAS.md      <- este indice
  onda-0-indexacao.md              <- 3 tarefas de levantamento
  onda-1-correcoes-pontuais.md     <- 9 tarefas independentes
  onda-2-constraints-satelites.md  <- 4 tarefas sequenciais
  onda-3-sinais-m2m.md             <- 1 tarefa
  onda-4-coerencia-dominio.md      <- 7 tarefas
  onda-5-qualidade-arquitetural.md <- 3 tarefas sequenciais
  bonus-planos-financiador.md      <- 1 tarefa extra
  final-documentacao.md            <- 1 tarefa
```

---

## Mapa de dependencias

```
Onda 0 (paralelo)          Onda 1 (paralelo)
  T-0.1 Indexar models       T-1.1  Evento.total
  T-0.2 Indexar views        T-1.2  Contratos default
  T-0.3 Indexar admin        T-1.3  AtividadeRegistro data
                             T-1.4  Meta data constraint
                             T-1.5  OIRegLoc unique
                             T-1.6  TIsIGATI unique
                             T-1.7  EquipeProjeto etc unique
                             T-1.8  Componente/Atividade unique
                             T-1.9  Subatividade unique
                             T-1.11 Mobilizados valor > 0

Onda 2 (sequencial)         Onda 3 (apos Onda 2)
  T-2.1 related_name          T-3.1 m2m_changed signals
  T-2.2 UniqueConstraint
  T-2.3 Pessoas constraints
  T-2.4 Organizacoes + org_governo

Onda 4 (parcial paralelo)   Bonus (apos Onda 2)
  T-4.1 equivalente_ieb       T-B.1 Planos + ind_fin formulario
  T-4.2 LeiHistorico FK
  T-4.3 PlanoHistorico FK
  T-4.4 PeqProj/Fundo constr  [dep Onda 2]
  T-4.5 Redesenho Rede        [complexo]
  T-4.6 Remover Outro
  T-4.7 AtivRegModelo + ind_fin [dep Onda 2]

Onda 5 (sequencial, por ultimo)
  T-5.1 FloatField -> DecimalField
  T-5.2 Thumbnail Celery
  T-5.3 Modularizar models.py  [ULTIMO]

Final
  T-F.1 Documentar contratos transversais
```

---

## Resumo quantitativo

| Onda | Tarefas | Paralelizaveis | Migrations |
|------|---------|---------------|------------|
| 0 | 3 | 3 | 0 |
| 1 | 9 | 9 | ~12 |
| 2 | 4 | 0 | ~5 |
| 3 | 1 | - | 0 |
| 4 | 7 | 5 | ~8 |
| 5 | 3 | 0 | ~2 |
| Bonus | 1 | - | 0 |
| Final | 1 | - | 0 |
| **Total** | **29** | **~17** | **~27** |

---

## Como usar com agentes de IA

1. **Tarefa especifica:** Leia o arquivo da onda e localize pelo codigo (ex: T-1.3)
2. **Onda inteira:** Execute na ordem indicada; ondas paralelas usam multiplos `forge`
3. **Tarefas ALTA complexidade (T-4.5, T-5.3):** `muse` planeja -> `forge` executa etapa por etapa
4. **Ordem recomendada:** Onda 0 -> 1 -> 2 -> 3 + 4 -> 5

### Contexto adicional

- `docs/PLANO_INDICADORES.md` -- redesign executado (migrations 0029-0032)
- `docs/GUIA_INDICADORES.md` -- guia funcional do sistema
- `plans/2026-04-22-plano-cirurgico-priorizado-src-ieb-models-1.3.md` -- plano original
