# Planejamento T-4.5 — Redesenho de `Rede`

Data: 2026-04-28
Origem: planejamento anterior do muse recuperado antes do desenvolvimento.
Escopo: T-4.5 da Onda 4 — alta complexidade.

## Objetivo

Redesenhar `Rede` para atuar como entidade cadastral reutilizável e criar `AtividadeRegistroRede` como tabela de ligação entre atividade, indicador e rede, preservando dados existentes e mantendo o cálculo de metas, views, formulário e administração funcionando.

## Referências verificadas

- Plano da Onda 4: `codigo/terralab_v2/plans/v1/tarefas/onda-4-coerencia-dominio.md:308-465`
- Índice do plano cirúrgico: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:113`
- Regra operacional para alta complexidade: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:148`
- Modelo atual `Rede`: `codigo/terralab_v2/src/ieb/models.py:963-983`
- Uso de `Rede` no cálculo de metas: `codigo/terralab_v2/src/ieb/models.py:499-518` e `codigo/terralab_v2/src/ieb/models.py:583-601`
- Uso de `Rede` nas views e formulário: `codigo/terralab_v2/src/ieb/views.py:140-145`, `codigo/terralab_v2/src/ieb/views.py:489-613`, `codigo/terralab_v2/src/ieb/views.py:704-707`, `codigo/terralab_v2/src/ieb/views.py:793-796`, `codigo/terralab_v2/src/ieb/views.py:918-927`
- Renderização dinâmica do formulário v2: `codigo/terralab_v2/src/terralab_v2/static/ieb/js/script_v2.js:216-335`
- Admin atual: `codigo/terralab_v2/src/ieb/admin.py:267-309`

## Avaliação da tarefa

### Classificação

Alta complexidade.

A própria tarefa está marcada como ALTA e recomenda planejamento prévio antes da execução. O plano cirúrgico também classifica T-4.5 como tarefa complexa e orienta planejamento antes de execução etapa por etapa.

### Problema identificado

O modelo atual `Rede` é um modelo satélite vinculado diretamente a `AtividadeRegistro`, com campos de indicador, financiador, nome, tipo e quantidade. Isso gera duplicação semântica: a mesma rede, quando relacionada a múltiplas atividades, precisa ser cadastrada várias vezes.

### Mudança proposta no plano original

Redesenhar o domínio em duas entidades:

- `Rede` como entidade cadastral mestre, sem vínculo direto com `AtividadeRegistro`.
- `AtividadeRegistroRede` como tabela de ligação satélite, contendo `atividade_registro`, `rede`, indicador, indicador_financiador e quantidade.

Também é necessário atualizar o `SUM_MAP`, trocando o cálculo de `Rede.quantidade` para `AtividadeRegistroRede.quantidade`.

## Project Structure Summary

A T-4.5 afeta uma aplicação Django localizada em `codigo/terralab_v2`, com os seguintes pontos principais:

- Domínio/modelos: `src/ieb/models.py`, onde `Rede` está definida como satélite de atividade e usada diretamente no cálculo de metas.
- Views/formulário: `src/ieb/views.py`, onde redes são exibidas no detalhe, parseadas do POST e criadas para indicadores IEB e indicadores de financiador.
- Admin: `src/ieb/admin.py`, onde vários modelos de registros estão registrados, mas `Rede` não aparece registrada diretamente no trecho atual analisado.
- JavaScript: `src/terralab_v2/static/ieb/js/script_v2.js`, que renderiza campos dinamicamente com base em `indicadores_config`.
- Migrations: a tarefa exige alteração de schema e migração de dados, pois o modelo atual será dividido em entidade cadastral e tabela de ligação.

## Relevant Files Examination

### `models.py`

O modelo atual `Rede` tem `atividade_registro`, `indicador`, `indicador_financiador`, `nome`, `tipo` e `quantidade`. Usa constraints satélite genéricas via `_satellite_constraints('rede')`. O cálculo de `Meta.realizado` e `MetaFinanciador.realizado` soma `Rede.quantidade` quando o tipo é `redes`.

Implicação: a migração não é apenas estrutural; ela impacta diretamente cálculo de metas, roll-up de financiadores e consistência dos relatórios.

### `views.py`

A view de detalhe atualmente busca redes diretamente por `Rede.objects.filter(atividade_registro=...)`.

O processamento POST mantém dois mapas: `redes_map` para indicadores IEB e `fin_redes_map` para indicadores de financiador. O parse atual espera campos `nome`, `tipo` e `quantidade`. A criação atual persiste `Rede` diretamente para indicador IEB e para indicador financiador.

A configuração atual do formulário para redes expõe `nome`, `tipo` e `quantidade`.

Implicação: a mudança deve alterar o contrato do POST para passar uma `rede_id` ou equivalente, além de quantidade. Também será necessário decidir se o formulário permitirá criar rede nova ou apenas selecionar rede existente.

### `script_v2.js`

O JS renderiza campos dinamicamente por tipo, a partir de `indicadoresConfig`. Campos do tipo `number` e `text` viram inputs simples. Campos do tipo `select` são renderizados atualmente como grupo de radio buttons, não como `<select>` HTML.

Implicação: se `rede_id` for implementado como `select`, o comportamento atual renderizará opções como radio buttons. Isso pode ser aceitável, mas precisa ser intencional; caso a expectativa seja dropdown/autocomplete, o JS precisa ser ajustado.

### `admin.py`

O admin usa `from .models import *`. Há registros de vários modelos de atividade e indicadores, mas no trecho analisado não há `admin.site.register(Rede)`.

Implicação: a proposta original diz atualizar `RedeAdmin` com inline de `AtividadeRegistroRede`, mas o admin atual não registra `Rede`. Será necessário criar registro explícito para `Rede` e decidir se `AtividadeRegistroRede` também será registrado separadamente.

## Priorização de riscos e desafios

1. Risco crítico — perda ou duplicação de dados na migration.
   - A tarefa altera a semântica do modelo `Rede`, separando cadastro mestre e vínculo com atividade.
   - O plano prevê deduplicação por nome normalizado.
   - Essa deduplicação é heurística e pode mesclar redes distintas com nomes iguais ou manter separadas redes semanticamente iguais com nomes diferentes.

2. Risco alto — quebra de cálculo de metas.
   - `Meta.realizado` e `MetaFinanciador.realizado` dependem atualmente de `Rede.quantidade`.
   - Se `SUM_MAP` for atualizado antes da migration estar consistente, os totais podem quebrar.

3. Risco alto — quebra do formulário de registro.
   - O POST atual envia `nome`, `tipo` e `quantidade`; o novo desenho deve enviar `rede_id` e `quantidade`.
   - A configuração atual do formulário ainda descreve campos antigos.

4. Risco médio — incompatibilidade visual/UX no JS.
   - O JS trata `select` como radio buttons.
   - Se houver muitas redes cadastradas, radio buttons podem degradar a usabilidade.

5. Risco médio — admin incompleto.
   - A proposta prevê `RedeAdmin` com inline, mas o admin atual não registra `Rede` diretamente no bloco de registros de atividade.
   - Sem admin adequado, a manutenção das redes cadastrais fica limitada.

## Plano estratégico

- [ ] Confirmar pré-condições da Onda 4. Validar que a Onda 2 foi concluída, pois a tarefa declara dependência das constraints da Onda 2 para `AtividadeRegistroRede`.
- [ ] Definir contrato final dos modelos. Transformar `Rede` em cadastro mestre com `nome`, `tipo` e `descricao`, e criar `AtividadeRegistroRede` com `atividade_registro`, `rede`, `indicador`, `indicador_financiador` e `quantidade`.
- [ ] Planejar migration em fases. Criar primeiro `AtividadeRegistroRede`, migrar os dados antigos e só depois remover os campos satélite de `Rede`.
- [ ] Especificar deduplicação de redes. Usar normalização por `nome.strip().lower()` como ponto de partida, mas registrar que isso é heurístico.
- [ ] Atualizar cálculos de metas. Substituir o uso de `Rede` por `AtividadeRegistroRede` nos mapas de soma de `Meta.realizado` e `MetaFinanciador.realizado`.
- [ ] Atualizar view de detalhe. Trocar a consulta atual de redes por atividade para consultar `AtividadeRegistroRede` com `select_related('rede')`.
- [ ] Atualizar processamento POST. Alterar o parse de redes para receber `rede_id` e `quantidade`, substituindo o contrato atual baseado em `nome`, `tipo` e `quantidade`.
- [ ] Atualizar criação de resultados para indicadores IEB e financiador. Substituir `Rede.objects.create(...)` por criação de `AtividadeRegistroRede`.
- [ ] Atualizar `indicadores_config`. Trocar os campos atuais de redes (`nome`, `tipo`, `quantidade`) por um seletor de rede cadastrada e campo de quantidade.
- [ ] Avaliar ajuste no JavaScript. Decidir se o seletor de redes será radio, dropdown ou autocomplete, considerando que o JS atual renderiza `select` como radio buttons.
- [ ] Atualizar admin. Criar administração explícita para `Rede` e incluir inline ou registro separado para `AtividadeRegistroRede`.
- [ ] Verificar templates/PDF/e-mail. Confirmar se o contexto de redes precisa entrar também no PDF ou e-mail.
- [ ] Executar validação funcional e de dados. Confirmar que uma mesma `Rede` pode ser ligada a múltiplas atividades e que o total de metas soma `AtividadeRegistroRede.quantidade`.

## Verification Criteria

- [ ] `Rede` deixa de ter vínculo direto com `AtividadeRegistro`, `Indicador`, `IndicadorFinanciador` e `quantidade`.
- [ ] `AtividadeRegistroRede` existe e representa a ligação entre atividade, rede, indicador/financiador e quantidade.
- [ ] Dados antigos de `Rede` são preservados em ligações equivalentes.
- [ ] `Meta.realizado` soma redes usando `AtividadeRegistroRede.quantidade`.
- [ ] `MetaFinanciador.realizado` soma redes usando `AtividadeRegistroRede.quantidade`.
- [ ] O formulário de registro permite selecionar uma rede existente e informar quantidade.
- [ ] O detalhe da atividade exibe redes por meio da tabela de ligação.
- [ ] O admin permite gerenciar redes cadastrais e visualizar/criar vínculos.
- [ ] Uma mesma rede cadastral pode ser vinculada a mais de uma atividade sem duplicação cadastral.
- [ ] A migration é reversível ou, se não for plenamente reversível por deduplicação, documenta claramente essa limitação na própria migration.

## Potential Risks and Mitigations

1. Perda de dados durante deduplicação.
   - Mitigação: migrar em fases, preservar todos os registros antigos como ligações e deduplicar apenas por regra explícita de nome normalizado.

2. Mescla indevida de redes com mesmo nome.
   - Mitigação: manter deduplicação conservadora e permitir revisão manual posterior pelo admin.

3. Quebra dos cálculos de metas.
   - Mitigação: atualizar `SUM_MAP` somente após garantir que `AtividadeRegistroRede` está populada e testada.

4. Formulário incompatível com o novo contrato.
   - Mitigação: alterar `indicadores_config`, parser POST e criação dos objetos na mesma etapa funcional.

5. Interface ruim para muitas redes.
   - Mitigação: preferir dropdown ou autocomplete se o volume de redes for significativo; usar radio apenas se o cadastro for pequeno.

## Alternative Approaches

### Abordagem recomendada — Entidade cadastral + tabela de ligação

Mantém `Rede` como cadastro mestre e cria `AtividadeRegistroRede`. Melhor normalização e reutilização. Maior custo de migration e ajustes em formulário/views.

### Abordagem incremental compatível — Criar `RedeCatalogo` separada

Mantém `Rede` antiga como satélite e cria novo cadastro paralelo. Menor risco imediato, mas mantém dívida técnica e exige compatibilidade por mais tempo.

### Abordagem mínima — Apenas deduplicar por nome mantendo modelo atual

Baixa alteração estrutural. Não resolve o problema de domínio, pois cada atividade continuaria criando registros satélite. Não recomendada para T-4.5, pois não cumpre o redesenho previsto.

## Conclusão

A avaliação recuperada confirma que T-4.5 deve ser tratada como tarefa de alta complexidade, com execução faseada e sem desenvolvimento direto antes de consolidar o desenho. O ponto mais sensível é a migration de dados, seguida pela atualização coordenada de cálculo de metas, formulário, views, JS e admin.