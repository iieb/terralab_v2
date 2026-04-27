# Plano Cirurgico v1.3 -- Indice de Tarefas

> **Origem:** `plans/2026-04-22-plano-cirurgico-priorizado-src-ieb-models-1.3.md`
> **Data:** 2026-04-27 | **Total:** 29 tarefas | **Migrations:** ~27
> **Revisao tecnica:** 2026-04-27 — correcoes C1-C5, A1-A7, M1-M4 aplicadas nos arquivos de ondas.

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
