# Backlog Pós-Danida — Plano v2

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Preservar tarefas tecnicamente relevantes que saíram do caminho crítico por não afetarem diretamente os indicadores Danida.

## Referências

- Backlog no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:193-220`
- Decisões sobre tarefas antigas: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:222-242`
- T-4.5 Rede: `codigo/terralab_v2/plans/v1/tarefas/onda-4-coerencia-dominio.md:308-317`
- Onda 5: `codigo/terralab_v2/plans/v1/tarefas/onda-5-qualidade-arquitetural.md:1-7`
- Planejamento específico de T-4.5: `codigo/terralab_v2/plans/v2/2026-04-28-planejamento-t4-5-redesenho-rede-1.0.md:1-168`

## Regra de backlog

Uma tarefa fica no backlog pós-Danida quando:

- o tipo de indicador não está em `insumos_gerais/indicadores.md:3-26`;
- a tarefa melhora arquitetura, mas não desbloqueia entrega Danida;
- a tarefa envolve migration complexa sem valor imediato para o cliente;
- a tarefa pertence à Onda 5 original e não é pré-requisito para `fundos`, `area`, `organizacoes`, `pessoas` ou `planos`.

## B1 — Alta prioridade pós-Danida

| Item | Origem | Motivo | Condição para retomar |
|---|---|---|---|
| T-4.5 Redesenho de `Rede` | Onda 4 | Relevante tecnicamente, mas `redes` não aparece no Danida e a tarefa é de alta complexidade | Retomar quando houver projeto com indicador de redes |
| T-5.3 Modularizar `models.py` | Onda 5 | Refatoração estrutural ampla; deve acontecer após estabilizar entrega funcional | Retomar após Danida validado e sem migrations pendentes |
| T-5.2 Thumbnail via Celery | Onda 5 | Melhoria de performance; não bloqueia indicadores Danida | Retomar quando performance/assíncrono virar prioridade |

## B2 — Média prioridade pós-Danida

| Item | Origem | Motivo | Condição para retomar |
|---|---|---|---|
| T-4.6 Remover `Outro` | Onda 4 | Limpeza de código morto; pode afetar legado | Retomar após auditoria de dados legados |
| T-4.7 `AtividadeRegistroModelo` com indicador financiador | Onda 4 | Tipo `modelos` não aparece no Danida | Retomar se projeto futuro usar modelos |
| Parte de T-4.4 referente a `PequenoProjeto` | Onda 4 | `pequenos_projetos` não aparece no Danida | Retomar se indicador de pequenos projetos entrar no escopo |
| Ajustes em `leis_politicas` | Plano geral | Tipo não aparece no Danida | Retomar sob demanda |
| Ajustes em `parcerias`, `produtos`, `contratos`, `mobilizados` | Plano geral | Tipos não aparecem no Danida | Retomar sob demanda |

## B3 — Baixa prioridade / sob demanda

| Item | Motivo | Condição para retomar |
|---|---|---|
| Melhorias em `redes` além da T-4.5 | Só entram quando houver uso real de redes | Projeto com indicador de redes |
| Melhorias em `areas_protegidas` | Não aparece no Danida atual | Indicador específico de áreas protegidas |
| Refatorações cosméticas | Não competem com entrega funcional | Janela de manutenção |
| Documentação transversal ampla | Fazer ao final, se ainda fizer sentido | Após estabilização do produto |

## T-4.5 — Decisão específica

### Status

Backlog pós-Danida. Não executar agora.

### Justificativa

- `redes` não aparece em `insumos_gerais/indicadores.md:3-26`.
- A tarefa altera modelo, views, formulário, JS, admin e migrations.
- O risco é alto e não gera valor direto para a entrega Danida atual.

### Como retomar no futuro

1. Revisar `codigo/terralab_v2/plans/v2/2026-04-28-planejamento-t4-5-redesenho-rede-1.0.md`.
2. Confirmar que existe demanda real de indicador `redes`.
3. Validar dados legados antes da migration.
4. Executar em fases, com testes de cálculo de metas.

## Onda 5 original — Decisão específica

### Status

Suspensa como sequência obrigatória no ciclo Danida.

### Reclassificação

- T-5.1 pode entrar em D2 somente se precisão de área/metas bloquear Danida.
- T-5.2 fica em backlog.
- T-5.3 fica em backlog e deve ser uma das últimas refatorações.

## Critério para sair do backlog

Uma tarefa só sai do backlog pós-Danida quando:

- houver demanda funcional real;
- a tarefa for necessária para projeto ativo;
- existir janela de validação/migration;
- o risco for compatível com o valor entregue.
