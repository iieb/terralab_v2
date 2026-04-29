# Onda D3 — Formulário, Admin e Relatório Danida

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Garantir que o usuário consiga lançar, conferir e validar os indicadores Danida no fluxo operacional real.

## Referências

- Onda D3 no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:158-173`
- Tipos no escopo: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:15-25`

## Pré-condições

- D0 concluída.
- D1 concluída.
- Correções essenciais de D2 aplicadas ou explicitamente descartadas.

## T-D3.1 — Ajustar `indicadores_config` para os tipos Danida

### Objetivo

Garantir que o formulário v2 renderize apenas os campos necessários para os indicadores Danida.

### Escopo

- `pessoas`;
- `organizacoes`;
- `area`;
- `fundos`;
- `planos`.

### Fora do escopo

- `redes`;
- `pequenos_projetos`;
- `modelos`;
- outros tipos sem indicador Danida.

### Critério de aceite

- Todos os indicadores Danida têm campos suficientes no formulário v2.

## T-D3.2 — Ajustar processamento POST para lacunas Danida

### Objetivo

Garantir que campos renderizados no formulário sejam persistidos corretamente.

### Executar somente para

- lacunas confirmadas na D1;
- campos definidos na matriz D0;
- correções necessárias após D2.

### Critério de aceite

- Cada tipo Danida salva corretamente registros de indicador IEB e financiador, se aplicável.

## T-D3.3 — Ajustar admin para cadastro e conferência Danida

### Objetivo

Facilitar cadastro, manutenção e validação de indicadores/metas/usuários/equipes para o projeto Danida.

### Verificar

- admin de `Equipe` com usuário de autenticação;
- admin de indicadores e metas;
- admin dos satélites Danida, se necessário;
- filtros por projeto/financiador;
- campos de busca úteis.

### Critério de aceite

- Operador consegue cadastrar e conferir dados Danida pelo admin quando necessário.

## T-D3.4 — Ajustar detalhe da atividade para auditoria

### Objetivo

Garantir que o detalhe mostre os dados necessários para validação funcional.

### Verificar

- responsável operacional (`EquipeProjeto`);
- equipe vinculada ao usuário, se aplicável;
- dados dos satélites Danida;
- indicador IEB/financiador;
- total usado no cálculo da meta.

### Critério de aceite

- Um lançamento pode ser auditado visualmente no detalhe.

## T-D3.5 — Validar relatório/exportação

### Objetivo

Confirmar se existe fluxo de relatório/exportação usado pelo cliente e se ele cobre os indicadores Danida.

### Verificar

- dashboard;
- exportação;
- PDF;
- e-mail;
- relatório por projeto/financiador.

### Critério de aceite

- Se houver relatório no escopo, ele mostra os cinco tipos Danida corretamente.
- Se não houver relatório no escopo, registrar que a conferência será feita por detalhe/admin/metas.

## T-D3.6 — Criar massa mínima de teste manual

### Objetivo

Ter exemplos mínimos para validar o fluxo inteiro.

### Massa mínima

- 1 atividade com indicador de `pessoas`;
- 1 atividade com indicador de `organizacoes`;
- 1 atividade com indicador de `area`;
- 1 atividade com indicador de `fundos`;
- 1 atividade com indicador de `planos`.

### Critério de aceite

- Dados simulados permitem validar cadastro, lançamento, detalhe e cálculo.

## Critério de saída da Onda D3

- Usuário consegue cadastrar e validar todos os indicadores Danida no fluxo real.
- Lacunas de UX ou relatório estão documentadas para homologação ou backlog.
