# Onda D1 — Validação do Fluxo Atual para os Tipos Danida

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Validar o que já funciona no sistema para os cinco tipos Danida antes de alterar código.

## Referências

- Onda D1 no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:114-131`
- Tipos no escopo: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:15-25`
- Indicadores Danida: `insumos_gerais/indicadores.md:3-26`

## Tipos a validar

1. `pessoas`
2. `organizacoes`
3. `area`
4. `fundos`
5. `planos`

## T-D1.1 — Validar cadastro de indicadores

### Verificar para cada tipo

- criação de `Indicador`;
- criação de `IndicadorFinanciador`, se aplicável;
- tipo correto selecionável;
- relação com projeto Danida;
- relação com financiador Danida, se aplicável.

### Critério de aceite

- Cada tipo pode ser cadastrado ou a lacuna está documentada.

## T-D1.2 — Validar vínculo com projeto e metas

### Verificar

- vínculo indicador ↔ projeto;
- criação de `Meta`;
- criação de `MetaFinanciador`, se aplicável;
- campos `base`, `meta`, datas e financiador.

### Critério de aceite

- Cada indicador mapeado na D0 consegue ter meta cadastrada ou tem lacuna objetiva.

## T-D1.3 — Validar renderização no formulário v2

### Verificar

- campos de `pessoas`;
- campos de `organizacoes`;
- campos de `area`;
- campos de `fundos`;
- campos de `planos`;
- comportamento para indicador IEB;
- comportamento para indicador financiador.

### Critério de aceite

- O formulário renderiza campos suficientes para lançar cada indicador Danida ou a lacuna fica documentada.

## T-D1.4 — Validar POST e persistência dos satélites

### Verificar

- `Pessoas`;
- `Organizacoes`;
- `Area`;
- `Fundo`;
- `Planos`;
- registros com `indicador`;
- registros com `indicador_financiador`.

### Critério de aceite

- Cada tipo persiste corretamente ou gera lacuna objetiva para D2.

## T-D1.5 — Validar detalhe da atividade

### Verificar

- detalhe da atividade;
- dados dos satélites;
- dados de financiador;
- responsável operacional via `EquipeProjeto`;
- campos necessários para auditoria.

### Critério de aceite

- Usuário consegue conferir os lançamentos Danida no detalhe.

## T-D1.6 — Validar cálculo de metas

### Verificar

- soma de pessoas;
- soma de organizações;
- soma de hectares;
- soma/contagem de fundos;
- contagem ou score de planos;
- roll-up via `equivalente_ieb`, se aplicável.

### Critério de aceite

- Cálculos corretos para todos os tipos Danida ou lacunas listadas para D2.

## Saída esperada da Onda D1

Criar uma lista de lacunas por tipo:

| Tipo | Cadastro | Meta | Formulário | POST | Detalhe | Cálculo | Lacuna D2 |
|---|---|---|---|---|---|---|---|

## Critério de saída da Onda D1

- Lacunas objetivas identificadas.
- Nenhuma correção estrutural ampla iniciada sem evidência de bloqueio Danida.
