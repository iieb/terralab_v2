# Onda D0 — Congelamento do Escopo Danida

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Transformar a lista de indicadores Danida em uma matriz técnica executável antes de qualquer alteração de código.

## Referências

- Indicadores Danida: `insumos_gerais/indicadores.md:3-26`
- Escopo funcional Danida: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:15-25`
- Roadmap D0 no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:93-112`

## T-D0.1 — Mapear indicadores para tipos do sistema

### Objetivo

Criar uma matriz com cada indicador Danida e seu tipo técnico no sistema.

### Saída esperada

| Indicador Danida | Tipo | Unidade | Campo principal | Observações |
|---|---|---|---|---|

### Critério de aceite

- Todos os indicadores de `insumos_gerais/indicadores.md:3-26` estão mapeados.
- Nenhum tipo fora do escopo Danida foi incluído sem justificativa.

## T-D0.2 — Definir se cada indicador será IEB, financiador ou ambos

### Objetivo

Confirmar se cada indicador será cadastrado como `Indicador`, `IndicadorFinanciador` ou ambos.

### Pontos de decisão

- Danida precisa de indicadores próprios como financiador?
- Haverá consolidação institucional via `equivalente_ieb`?
- Algum indicador Danida já corresponde a indicador IEB existente?

### Critério de aceite

- Cada indicador tem decisão explícita: IEB, financiador ou ambos.
- Casos com roll-up indicam o `equivalente_ieb` necessário.

## T-D0.3 — Definir campos obrigatórios para `pessoas`

### Verificar

- total de pessoas;
- homens/mulheres;
- jovens;
- indígenas;
- extrativistas;
- quilombolas;
- servidor público;
- outras desagregações exigidas pelo cliente.

### Critério de aceite

- Cada indicador de pessoas informa se precisa apenas de total ou também de desagregações.

## T-D0.4 — Definir campos obrigatórios para `organizacoes`

### Verificar

- organizações indígenas;
- governo;
- foco de atuação;
- acesso a políticas públicas;
- gestão organizacional/incidência política.

### Critério de aceite

- Campos necessários para OIs estão definidos antes de validar/corrigir o modelo.

## T-D0.5 — Definir regra técnica para `area`

### Verificar

- hectares de agroflorestas implementados;
- hectares de TIs com autonomia no monitoramento e gestão da informação;
- necessidade de vínculo M2M com TIs;
- unidade e precisão decimal.

### Critério de aceite

- A regra de cálculo de hectares está definida.
- Está claro quando o total vem de campo manual e quando vem de M2M.

## T-D0.6 — Definir regra técnica para `planos`

### Verificar

- plano desenvolvido;
- plano implementado;
- PGTAs com ações implementadas;
- plano de negócios desenvolvido;
- score/situação usada para cálculo.

### Critério de aceite

- Cada indicador de planos tem situação ou regra de contagem definida.

## T-D0.7 — Definir regra técnica para `fundos`

### Verificar

- contagem de chamadas;
- valor total;
- tipo de fundo;
- vínculo com indicador financiador.

### Critério de aceite

- Está definido se o indicador de fundos mede quantidade, valor ou ambos.

## Critério de saída da Onda D0

- Matriz Danida validada e suficiente para orientar implementação.
- Nenhuma tarefa de código é iniciada sem essa matriz.
