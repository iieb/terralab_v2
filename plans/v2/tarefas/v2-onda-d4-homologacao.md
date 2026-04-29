# Onda D4 — Homologação Funcional Danida

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Fechar a entrega Danida validando o fluxo ponta a ponta sem puxar dívidas técnicas fora do escopo.

## Referências

- Onda D4 no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:175-191`
- Critério de sucesso do plano v2: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:371-381`

## Pré-condições

- D0 concluída.
- D1 concluída.
- D2 concluída ou com decisões explícitas de não execução.
- D3 concluída.

## T-D4.1 — Rodar validação Django

### Objetivo

Garantir que o projeto passa na validação estrutural do Django.

### Comandos esperados

- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`

### Critério de aceite

- Comandos passam sem erros ou geram lista objetiva de correções.

## T-D4.2 — Validar migrations localmente

### Objetivo

Confirmar que migrations necessárias aplicam em ambiente local.

### Verificar

- migrations criadas na D2/D3;
- ausência de migration inesperada fora do escopo;
- dados existentes preservados;
- rollback quando aplicável.

### Critério de aceite

- Migrations aplicam sem erro.
- Mudanças fora do escopo Danida são justificadas ou removidas.

## T-D4.3 — Testar formulário v2 por tipo Danida

### Objetivo

Validar lançamento manual dos cinco tipos.

### Testes mínimos

- `pessoas`;
- `organizacoes`;
- `area`;
- `fundos`;
- `planos`.

### Critério de aceite

- Cada tipo pode ser lançado sem erro.
- Dados aparecem no detalhe da atividade.

## T-D4.4 — Testar cálculo de metas com dados simulados

### Objetivo

Confirmar que os valores lançados impactam corretamente `Meta.realizado` e `MetaFinanciador.realizado`.

### Verificar

- meta IEB;
- meta de financiador;
- roll-up via `equivalente_ieb`, se ativado;
- soma/contagem por tipo.

### Critério de aceite

- Valores calculados batem com a massa manual de teste.

## T-D4.5 — Revisar escopo alterado

### Objetivo

Garantir que nenhum tipo fora da lista Danida foi alterado sem necessidade.

### Verificar

- migrations;
- models;
- views;
- formulário;
- admin;
- JS.

### Critério de aceite

- Alterações fora do escopo estão ausentes ou justificadas por dependência direta.

## T-D4.6 — Preparar pendências para backlog pós-Danida

### Objetivo

Encerrar a fase Danida com pendências organizadas.

### Saída esperada

Tabela com:

| Pendência | Tipo | Prioridade | Motivo | Origem |
|---|---|---|---|---|

### Critério de aceite

- Backlog pós-Danida atualizado sem bloquear entrega Danida.

## Critério de saída da Onda D4

- Escopo Danida validado ponta a ponta.
- Indicadores Danida mapeados, lançados, calculados e conferidos.
- Backlog pós-Danida organizado para retomada posterior.
