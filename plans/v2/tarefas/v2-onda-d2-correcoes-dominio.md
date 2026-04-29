# Onda D2 — Correções Essenciais de Domínio para Danida

Plano: Desenvolvimento Danida v2.0
Data: 2026-04-29
Arquivo principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md`

## Objetivo

Executar somente correções necessárias para que os tipos Danida sejam lançados, persistidos, calculados e auditados corretamente.

## Referências

- Onda D2 no plano principal: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:133-156`
- Modelo de autenticação/equipe/acesso: `codigo/terralab_v2/plans/v2/2026-04-29-plano-desenvolvimento-danida-v2.0.md:244-360`
- Revisão técnica final: `codigo/terralab_v2/plans/v1/2026-04-27-revisao-tarefas-plano-cirurgico-2.1.md:1-120`
- Índice v1 consolidado: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:108-120`

## Pré-condições

- Onda D0 concluída.
- Onda D1 concluída.
- Lacunas por tipo documentadas.

## T-D2.0 — Definir e implementar vínculo `User` Django ↔ `Equipe`

### Objetivo

Usar o `User` Django para autenticação e `Equipe` como identidade operacional ligada à `Instituicao`.

### Decisão inicial recomendada

Usar `OneToOneField` opcional de `Equipe` para `settings.AUTH_USER_MODEL`, salvo se houver caso real de um mesmo login atuar por múltiplas instituições.

### Modelo conceitual

```python
usuario = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='perfil_equipe',
    verbose_name='Usuário de autenticação',
)
```

### Tarefas

- [ ] Confirmar 1:1 ou 1:N para o ciclo Danida.
- [ ] Adicionar campo `usuario` em `Equipe`.
- [ ] Criar migration.
- [ ] Ajustar admin de `Equipe` para busca/seleção de usuário.
- [ ] Criar helper para resolver equipe do usuário autenticado.
- [ ] Definir comportamento para usuário autenticado sem equipe vinculada.

### Critério de aceite

- `request.user` pode ser convertido de forma segura para a `Equipe` operacional.
- A relação não é específica do IEB; serve para qualquer instituição.

## T-D2.1 — Preparar política mínima de acesso por equipe/organização

### Objetivo

Preparar base de acesso por `Equipe`, `Instituicao` e `EquipeProjeto`.

### Regra mínima Danida

- usuário comum acessa apenas projetos onde sua `Equipe` está vinculada via `EquipeProjeto`;
- equipe adicional deve ser selecionável apenas dentro do mesmo projeto;
- perfis IEB administrativos podem ter acesso ampliado via grupos/permissões Django ou marca administrativa;
- registros preservam `EquipeProjeto` como responsável operacional;
- históricos preservam a `Equipe` derivada do usuário autenticado.

### Critério de aceite

- Existe regra documentada e helper/base técnica para aplicar filtros por equipe/projeto.

## T-D2.2 — Replanejar históricos de Lei/Plano para `Equipe`

### Origem

Reclassificação de T-4.2/T-4.3 do Plano Cirúrgico v1.3.

### Objetivo

Evitar que histórico funcional dependa apenas de `User`; preservar a identidade operacional de domínio via `Equipe`.

### Diretriz

- manter `User` como origem técnica de autenticação;
- adicionar campo `equipe` nos históricos de domínio, se a lacuna for confirmada;
- manter `usuario` como legado/técnico se necessário;
- views devem resolver equipe a partir de `request.user.perfil_equipe`.

### Critério de aceite

- Histórico funcional mostra a equipe/instituição responsável pela ação.

## T-D2.3 — Avaliar e executar `equivalente_ieb`

### Origem

T-4.1 do Plano Cirúrgico v1.3.

### Objetivo

Permitir roll-up de indicador financiador Danida para indicador institucional IEB, se D0/D1 confirmarem necessidade.

### Executar somente se

- Danida usar `IndicadorFinanciador`; e
- houver indicador institucional equivalente; e
- a consolidação IEB for necessária no ciclo atual.

### Critério de aceite

- `Meta.realizado` contabiliza corretamente registros de financiador com `equivalente_ieb`.

## T-D2.4 — Corrigir `Fundo` somente no recorte Danida

### Origem

Parte de T-4.4 do Plano Cirúrgico v1.3.

### Objetivo

Garantir que o indicador de fundos do Danida seja lançado e calculado corretamente.

### Escopo

- incluir parte de `Fundo` se D1 confirmar lacuna;
- não incluir `PequenoProjeto` salvo se virar dependência direta Danida.

### Critério de aceite

- Indicador de chamadas do fundo Rutî funciona ponta a ponta.

## T-D2.5 — Corrigir suporte a `Planos` com indicador financiador

### Origem

T-B.1 do Plano Cirúrgico v1.3.

### Objetivo

Permitir que indicadores Danida de planos funcionem como `IndicadorFinanciador`, se necessário.

### Executar somente se

- D0 definir planos como indicador financiador; ou
- D1 mostrar falha no formulário/POST/cálculo de planos com financiador.

### Critério de aceite

- `Planos` pode ser lançado e calculado para indicador financiador.

## T-D2.6 — Validar/corrigir `Pessoas`

### Origem

T-2.3 do Plano Cirúrgico v1.3.

### Objetivo

Garantir integridade das desagregações necessárias aos indicadores Danida de pessoas.

### Executar somente se

- constraints ainda não estiverem concluídas; ou
- D1 mostrar risco nos lançamentos; ou
- D0 exigir desagregações específicas.

### Critério de aceite

- Indicadores de pessoas aceitam os dados exigidos e calculam corretamente.

## T-D2.7 — Validar/corrigir `Organizacoes`

### Origem

T-2.4 do Plano Cirúrgico v1.3.

### Objetivo

Garantir integridade de organizações e, se necessário, suporte a `org_governo`.

### Executar somente se

- D0 confirmar necessidade de subgrupos; ou
- D1 mostrar lacuna em cadastro, formulário, POST ou cálculo.

### Critério de aceite

- Indicadores de OIs funcionam ponta a ponta.

## T-D2.8 — Validar/corrigir `Area` e M2M com TIs

### Origem

Parte de T-3.1 do Plano Cirúrgico v1.3.

### Objetivo

Garantir cálculo de hectares e relação com TIs quando exigido pelo indicador Danida.

### Executar somente se

- indicador de TIs com autonomia exigir vínculo M2M; ou
- D1 mostrar divergência de cálculo de hectares.

### Critério de aceite

- Hectares Danida são calculados corretamente e podem ser auditados.

## T-D2.9 — Avaliar DecimalField para áreas/metas

### Origem

T-5.1 do Plano Cirúrgico v1.3, reclassificada como candidata Danida.

### Objetivo

Evitar erro de precisão em hectares e metas, se isso afetar diretamente Danida.

### Executar somente se

- D1 mostrar risco real de precisão; ou
- o cliente exigir precisão decimal formal; ou
- cálculos de hectares/metas divergirem por `FloatField`.

### Critério de aceite

- Precisão de hectares/metas é suficiente para relatório Danida.

## Critério de saída da Onda D2

- Os cinco tipos Danida podem ser lançados, persistidos e calculados.
- Usuário operacional pode ser resolvido para `Equipe` e `Instituicao`.
- Histórico/auditoria preserva identidade de domínio quando aplicável.
- Nenhum tipo fora do escopo foi alterado sem justificativa explícita.
