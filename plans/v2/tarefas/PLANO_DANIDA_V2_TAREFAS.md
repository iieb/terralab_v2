# Plano v2 — Tarefas por Onda

Data: 2026-04-29
Versão: 2.0
Plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Organizar o Plano de Desenvolvimento v2 em arquivos executáveis por onda, seguindo o mesmo padrão de organização do Plano Cirúrgico v1.3, mas com foco exclusivo no recorte Danida.

## Base autoritativa

- Plano v2 Danida: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:1-401`
- Indicadores Danida: `insumos_gerais/indicadores.md:3-26`
- Plano Cirúrgico v1.3 consolidado: `codigo/terralab_v2/plans/v1/2026-04-22-plano-cirurgico-priorizado-src-ieb-models-1.3.md:1-21`
- Revisão técnica final: `codigo/terralab_v2/plans/v1/2026-04-27-revisao-tarefas-plano-cirurgico-2.1.md:1-12`
- Índice v1 de tarefas: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:1-6`

## Estrutura de arquivos v2

```text
plans/v2/tarefas/
  PLANO_DANIDA_V2_TAREFAS.md       <- este índice
  v2-onda-d0-escopo-danida.md      <- congelamento da matriz técnica
  v2-onda-d1-validacao-fluxo.md    <- validação do fluxo atual
  v2-onda-d2-correcoes-dominio.md  <- correções essenciais de domínio
  v2-onda-d3-formulario-admin.md   <- formulário, admin e relatório
  v2-onda-d4-homologacao.md        <- homologação funcional
  v2-backlog-pos-danida.md         <- backlog pós-Danida organizado
```

## Mapa de dependências v2

```text
D0 — Congelar escopo Danida
  ↓
D1 — Validar fluxo atual dos cinco tipos
  ↓
D2 — Corrigir apenas lacunas essenciais
  ↓
D3 — Ajustar formulário, admin e relatório
  ↓
D4 — Homologar funcionalmente
  ↓
Backlog pós-Danida
```

## Ondas

| Onda | Arquivo | Objetivo |
|---|---|---|
| D0 | `v2-onda-d0-escopo-danida.md` | Converter indicadores Danida em matriz técnica fechada |
| D1 | `v2-onda-d1-validacao-fluxo.md` | Validar o fluxo atual antes de alterar código |
| D2 | `v2-onda-d2-correcoes-dominio.md` | Executar correções essenciais nos tipos Danida |
| D3 | `v2-onda-d3-formulario-admin.md` | Ajustar experiência operacional, admin e conferência |
| D4 | `v2-onda-d4-homologacao.md` | Validar ponta a ponta com dados simulados |
| Backlog | `v2-backlog-pos-danida.md` | Preservar tarefas fora do caminho crítico |

## Política de priorização

### Categoria A — Fazer agora

Entram tarefas que afetam diretamente `fundos`, `area`, `organizacoes`, `pessoas` ou `planos`.

### Categoria B — Fazer agora somente se bloquear Danida

Entram apenas dependências diretas para o recorte Danida, como constraints necessárias, cálculo de metas, infraestrutura do formulário v2 ou M2M de `Area` quando afetar hectares vinculados a TI.

### Categoria C — Backlog pós-Danida

Vão para backlog tipos fora da lista Danida, refatorações amplas, migrations complexas sem ganho direto e melhorias arquiteturais que não bloqueiam a entrega.

## Regra operacional

1. Não executar D2 antes de D0 e D1.
2. Não executar tarefa de tipo fora do escopo Danida sem evidência de bloqueio direto.
3. Tarefas herdadas do v1 devem ser lidas pela versão consolidada em `codigo/terralab_v2/plans/v1/` e pela revisão técnica 2.1.
4. T-4.5 `Rede` permanece fora do caminho crítico e deve ficar no backlog pós-Danida.
5. O vínculo `User` Django ↔ `Equipe` deve ser tratado como base para política futura de acesso por equipe/organização.
