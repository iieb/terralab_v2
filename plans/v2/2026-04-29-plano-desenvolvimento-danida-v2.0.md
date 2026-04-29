# Plano de Desenvolvimento v2 — Recorte Danida e Backlog Pós-Danida

Data: 2026-04-29
Versão: 2.0
Origem: Replanejamento do Plano Cirúrgico v1.3 após validação de escopo com cliente Danida/Dinamarca, usando como base autoritativa os planos consolidados em `codigo/terralab_v2/plans/v1/` e `codigo/terralab_v2/plans/v2/`.

## 1. Decisão estratégica

O desenvolvimento deixa de seguir a lógica de executar integralmente as ondas restantes do Plano Cirúrgico v1.3 e passa a seguir uma lógica de entrega orientada aos indicadores do projeto Danida. A base documental autoritativa para esta leitura é a pasta `codigo/terralab_v2/plans/`, organizada em `v1/`, `v2/` e `apoio/`, não a antiga pasta `plans/` da raiz do repositório.

A lista de indicadores de referência é `insumos_gerais/indicadores.md:3-26`.

Essa mudança justifica criar uma versão v2 do plano, e não apenas uma revisão 1.4, porque o critério de priorização mudou: antes o plano era orientado à melhoria estrutural ampla do domínio; agora o plano é orientado ao menor conjunto necessário para entregar o projeto Danida com segurança.

## 2. Escopo funcional Danida

### 2.1 Tipos de indicador dentro do escopo

| Tipo no sistema | Motivo de entrada no escopo | Indicadores relacionados |
|---|---|---|
| `fundos` | Necessário para chamadas do fundo Rutî | Número de chamadas do fundo Rutî |
| `area` | Necessário para hectares e relação com Terras Indígenas | Agroflorestas; TIs com autonomia no monitoramento/gestão |
| `organizacoes` | Necessário para OIs | Acesso a políticas públicas; gestão organizacional/incidência política |
| `pessoas` | Necessário para beneficiários e treinamentos | Castanheiros, criadores de gado, indígenas em monitoramento, treinamentos, fortalecimento institucional |
| `planos` | Necessário para planos, PGTAs e plano de negócios | Planos de adaptação; PGTAs; plano de negócios da pecuária sustentável |

### 2.2 Tipos fora do escopo imediato

Os tipos abaixo não aparecem na lista Danida atual e passam para backlog pós-Danida, salvo se forem descobertos como dependência técnica direta durante a validação:

- `redes`
- `pequenos_projetos`
- `areas_protegidas`
- `eventos`
- `leis_politicas`
- `parcerias`
- `produtos`
- `contratos`
- `mobilizados`
- `modelos`
- `outro`

## 3. Situação do plano anterior e base documental autoritativa

O Plano Cirúrgico v1.3 organizava 29 tarefas em ondas. O índice consolidado em `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md` registra que a Onda 4 ainda continha as tarefas T-4.1 a T-4.7 e que a Onda 5 seria executada por último com T-5.1, T-5.2 e T-5.3.

Este plano v2 deve ser lido a partir dos arquivos consolidados dentro de `codigo/terralab_v2/plans/v2/`, usando `codigo/terralab_v2/plans/v1/` apenas como fonte histórica/técnica do Plano Cirúrgico anterior. Qualquer referência residual à pasta raiz `plans/` em documentos antigos deve ser interpretada como legado de organização anterior, não como fonte atual de execução.

Fontes autoritativas usadas para este replanejamento:

- Plano Cirúrgico v1.3 consolidado: `codigo/terralab_v2/plans/v1/2026-04-22-plano-cirurgico-priorizado-src-ieb-models-1.3.md:1-21`
- Revisão técnica final das tarefas: `codigo/terralab_v2/plans/v1/2026-04-27-revisao-tarefas-plano-cirurgico-2.1.md:1-12`
- Índice executável das ondas v1: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:1-6`

Referências operacionais atuais:

- Mapa de dependências da Onda 4 e Onda 5: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:108-120`
- Regra original para tarefas complexas: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:144-149`
- Correções técnicas incorporadas nos arquivos executáveis das ondas: `codigo/terralab_v2/plans/v1/tarefas/PLANO_CIRURGICO_TAREFAS.md:33-54`
- T-4.5 Rede classificada como alta complexidade: `codigo/terralab_v2/plans/v1/tarefas/onda-4-coerencia-dominio.md:308-317`
- Onda 5 marcada como sequencial e posterior a todas as ondas anteriores: `codigo/terralab_v2/plans/v1/tarefas/onda-5-qualidade-arquitetural.md:1-7`

## 4. Nova política de priorização

### Categoria A — Fazer agora

Entram no ciclo Danida as tarefas que:

1. afetam diretamente `pessoas`, `organizacoes`, `area`, `fundos` ou `planos`;
2. corrigem cálculo de metas desses tipos;
3. viabilizam indicador financiador para esses tipos;
4. corrigem formulário, POST, detalhe ou admin usados por esses tipos;
5. reduzem risco de erro em lançamento ou relatório do projeto Danida.

### Categoria B — Fazer agora somente se bloquear Danida

Entram apenas se forem dependência direta:

1. constraints genéricas que o código exige para funcionar nos tipos Danida;
2. ajustes transversais em `Meta.realizado` e `MetaFinanciador.realizado`;
3. correções em infraestrutura de formulário v2;
4. correções em M2M de `Area` quando afetarem hectares vinculados a TI.

### Categoria C — Backlog pós-Danida

Vão para backlog:

1. tarefas de tipos não usados pelo Danida;
2. refatorações arquiteturais amplas;
3. migrations complexas sem ganho direto para o projeto atual;
4. melhorias de qualidade que podem esperar sem comprometer a entrega.

## 5. Novo roadmap v2

O detalhamento operacional das ondas v2 está organizado em arquivos próprios, seguindo o padrão do Plano Cirúrgico v1.3:

| Onda | Arquivo de tarefas | Objetivo |
|---|---|---|
| Índice v2 | `codigo/terralab_v2/plans/v2/tarefas/PLANO_DANIDA_V2_TAREFAS.md` | Mapa geral de dependências e regras operacionais |
| D0 | `codigo/terralab_v2/plans/v2/tarefas/v2-onda-d0-escopo-danida.md` | Congelar matriz técnica dos indicadores Danida |
| D1 | `codigo/terralab_v2/plans/v2/tarefas/v2-onda-d1-validacao-fluxo.md` | Validar fluxo atual antes de alterar código |
| D2 | `codigo/terralab_v2/plans/v2/tarefas/v2-onda-d2-correcoes-dominio.md` | Executar correções essenciais de domínio |
| D3 | `codigo/terralab_v2/plans/v2/tarefas/v2-onda-d3-formulario-admin.md` | Ajustar formulário, admin e relatório |
| D4 | `codigo/terralab_v2/plans/v2/tarefas/v2-onda-d4-homologacao.md` | Homologar fluxo ponta a ponta |
| Backlog | `codigo/terralab_v2/plans/v2/tarefas/v2-backlog-pos-danida.md` | Organizar tarefas pós-Danida |

### Onda D0 — Congelamento do escopo Danida

Objetivo: transformar a lista de indicadores em matriz técnica executável.

Tarefas:

- [ ] Mapear cada indicador Danida para `tipo`, campos, unidade de medida e regra de cálculo.
- [ ] Confirmar se os indicadores serão cadastrados como `Indicador` IEB, `IndicadorFinanciador` ou ambos.
- [ ] Confirmar se Danida exige roll-up para indicador IEB via `equivalente_ieb`.
- [ ] Confirmar os campos necessários para `pessoas`, incluindo desagregações obrigatórias.
- [ ] Confirmar os campos necessários para `organizacoes`, incluindo foco e governo se aplicável.
- [ ] Confirmar regra de hectares para `area`, especialmente relação M2M com TIs.
- [ ] Confirmar regra de `planos`: quais situações contam como desenvolvido/implementado.
- [ ] Confirmar regra de `fundos`: se será contagem de chamadas, valor total ou ambos.

Critério de saída:

- Matriz Danida validada e suficiente para orientar implementação.

### Onda D1 — Validação do fluxo atual para os cinco tipos Danida

Objetivo: antes de alterar código, verificar o que já funciona e onde estão as lacunas.

Tarefas:

- [ ] Validar cadastro de indicadores dos tipos `pessoas`, `organizacoes`, `area`, `fundos`, `planos`.
- [ ] Validar vínculo dos indicadores ao projeto Danida.
- [ ] Validar criação de metas para cada tipo.
- [ ] Validar renderização no formulário v2.
- [ ] Validar processamento POST e persistência dos satélites.
- [ ] Validar detalhe da atividade.
- [ ] Validar cálculo de `Meta.realizado`.
- [ ] Validar cálculo de `MetaFinanciador.realizado`, se Danida usar indicadores de financiador.

Critério de saída:

- Lista objetiva de lacunas por tipo de indicador.

### Onda D2 — Correções essenciais de domínio para Danida

Objetivo: implementar apenas correções necessárias para os tipos Danida.

Tarefas candidatas herdadas do Plano Cirúrgico v1.3 consolidado em `codigo/terralab_v2/plans/v1/`, da revisão técnica 2.1 e do novo ajuste de autenticação/acesso:

| Tarefa | Decisão v2 | Justificativa |
|---|---|---|
| Nova T-D2.0 `Equipe.usuario` | Incluir antes dos ajustes de histórico/acesso | Conectar `Equipe` ao usuário Django e usar `Equipe` como identidade operacional do sistema; o vínculo não é exclusivo do IEB, vale para equipes de qualquer instituição |
| Nova T-D2.1 política base de acesso por equipe/organização | Planejar e preparar, implementar apenas regras mínimas para Danida | Acesso futuro deve considerar `Equipe`, `Instituicao` e vínculo ao projeto |
| T-4.1 `equivalente_ieb` em `IndicadorFinanciador` | Manter se Danida usar indicador financiador com consolidação IEB | Pode ser essencial para roll-up de metas |
| T-4.2/T-4.3 históricos de Lei/Plano | Replanejar: histórico deve apontar para `Equipe`, não diretamente para `User`, quando a ação vier de usuário autenticado com equipe vinculada | O usuário Django autentica; a `Equipe` representa pessoa/equipe/instituição no domínio do IEB |
| T-4.4 constraints em `Fundo` | Manter parcialmente para `Fundo`; avaliar se `PequenoProjeto` entra ou fica fora | Danida tem indicador de fundos |
| T-B.1 Planos com `IndicadorFinanciador` | Manter se Danida usar planos como indicador financiador | Lacuna diretamente relacionada a `planos` |
| T-2.3 constraints em `Pessoas` | Manter se ainda não estiver concluída e se houver risco nos lançamentos | Danida tem vários indicadores de pessoas |
| T-2.4 `Organizacoes` + `org_governo` | Manter se ainda não estiver concluída e se o campo for necessário | Danida tem indicadores de OIs |
| T-3.1 sinais M2M para `Area` | Manter somente a parte que afeta `Area`/TIs se necessário | Danida tem hectares com relação M2M com TI |
| T-5.1 DecimalField para áreas/metas | Reclassificar como candidata Danida, não como onda final | Pode melhorar precisão dos hectares e metas |

Critério de saída:

- Os cinco tipos Danida podem ser lançados, persistidos e calculados corretamente.
- Todo usuário operacional usado no fluxo Danida pode ser resolvido para uma `Equipe` vinculada a uma `Instituicao`.
- Histórico e auditoria deixam de depender apenas do `User` Django e passam a preservar a identidade de domínio via `Equipe`, mantendo o `User` como mecanismo de autenticação.

### Onda D3 — Ajustes de formulário, admin e relatório Danida

Objetivo: garantir usabilidade e conferência pelo cliente.

Tarefas:

- [ ] Ajustar `indicadores_config` apenas para campos dos tipos Danida que estiverem incompletos.
- [ ] Ajustar processamento POST apenas para lacunas dos tipos Danida.
- [ ] Ajustar admin dos indicadores/metas para facilitar cadastro Danida.
- [ ] Garantir que o detalhe da atividade exiba os dados necessários para auditoria.
- [ ] Validar relatório/exportação, se existir no fluxo de entrega.
- [ ] Criar massa mínima de teste manual com um exemplo por tipo Danida.

Critério de saída:

- Usuário consegue cadastrar e validar todos os indicadores Danida no fluxo real.

### Onda D4 — Homologação funcional Danida

Objetivo: fechar a entrega sem puxar dívidas técnicas não essenciais.

Tarefas:

- [ ] Rodar `python manage.py check`.
- [ ] Rodar `python manage.py makemigrations --check --dry-run`.
- [ ] Rodar migrations em ambiente local.
- [ ] Testar formulário v2 para cada tipo Danida.
- [ ] Testar cálculo de metas com dados simulados.
- [ ] Revisar se nenhum tipo fora do escopo foi alterado desnecessariamente.
- [ ] Preparar lista de pendências para backlog pós-Danida.

Critério de saída:

- Escopo Danida validado ponta a ponta.

## 6. Backlog organizado pós-Danida

### B1 — Alta prioridade pós-Danida

| Item | Origem | Motivo |
|---|---|---|
| T-4.5 Redesenho de `Rede` | Onda 4 | Tarefa tecnicamente relevante, mas fora da lista Danida e de alta complexidade |
| T-5.3 Modularizar `models.py` | Onda 5 | Refatoração estrutural ampla; deve ocorrer só após estabilizar entrega Danida |
| T-5.2 Thumbnail via Celery | Onda 5 | Melhoria de performance; não bloqueia indicadores Danida |

### B2 — Média prioridade pós-Danida

| Item | Origem | Motivo |
|---|---|---|
| T-4.6 Remover `Outro` | Onda 4 | Limpeza de código morto; fazer depois se não houver risco para dados legados |
| T-4.7 `AtividadeRegistroModelo` com indicador financiador | Onda 4 | Tipo `modelos` não aparece no Danida |
| Parte de T-4.4 referente a `PequenoProjeto` | Onda 4 | `pequenos_projetos` não aparece no Danida |
| Ajustes em `leis_politicas` | Plano geral | Tipo não aparece no Danida |
| Ajustes em `parcerias`, `produtos`, `contratos`, `mobilizados` | Plano geral | Tipos não aparecem no Danida |

### B3 — Baixa prioridade / sob demanda

| Item | Motivo |
|---|---|
| Melhorias em `redes` além da T-4.5 | Só entram quando houver projeto com indicadores de redes |
| Melhorias em `areas_protegidas` | Só entram se houver indicador específico de áreas protegidas |
| Refatorações cosméticas | Não devem competir com entrega funcional |
| Documentação transversal ampla | Fazer ao final, se ainda fizer sentido |

## 7. Decisões específicas sobre tarefas antigas

### T-4.5 — Rede

Decisão: mover para backlog pós-Danida.

Motivo:

- `redes` não está em `insumos_gerais/indicadores.md:3-26`.
- A tarefa altera modelo, views, formulário, JS, admin e migrations.
- O risco é alto e o benefício é nulo para a entrega Danida atual.

### Onda 5

Decisão: cancelar a execução sequencial original da Onda 5 neste momento.

Nova classificação:

- T-5.1 pode ser antecipada ou recortada se a validação de `area` e metas mostrar risco real de precisão.
- T-5.2 vai para backlog pós-Danida.
- T-5.3 vai para backlog pós-Danida e só deve ser executada depois de estabilizar todas as entregas funcionais.

## 8. Modelo de autenticação, equipe e política de acesso

### 8.1 Diretriz de domínio

O `User` do Django deve ser usado como mecanismo de autenticação, senha, sessão, permissões administrativas e integração com a estrutura padrão do Django. Porém, para as regras de negócio do sistema, a identidade operacional deve ser a `Equipe`.

Essa diretriz não significa criar uma “equipe IEB” especial. O IEB será uma `Instituicao` com maior perfil de acesso, mas outras organizações também terão suas próprias equipes. Portanto, `Equipe` deve ser entendida como perfil institucional de uma pessoa usuária dentro de qualquer organização cadastrada.

No modelo atual, `Equipe` já representa a pessoa/equipe institucional e está vinculada a `Instituicao`. `EquipeProjeto` vincula `Equipe` a `Projeto`, e `AtividadeRegistro` já usa `EquipeProjeto` como responsável pelo registro.

Referências verificadas:

- `Equipe` possui `nome`, `cargo`, `cpf` e FK para `Instituicao`: `codigo/terralab_v2/src/ieb/models.py:125-132`
- `EquipeProjeto` vincula `Equipe` a `Projeto`: `codigo/terralab_v2/src/ieb/models.py:203-211`
- `AtividadeRegistro` usa `equipe_projeto`: `codigo/terralab_v2/src/ieb/models.py:640-641`
- `LeiHistorico.usuario` e `PlanoHistorico.usuario` estão hoje ligados diretamente ao `User` Django: `codigo/terralab_v2/src/ieb/models.py:892-900` e `codigo/terralab_v2/src/ieb/models.py:1107-1115`

### 8.2 Decisão sobre criar outro model de usuário

Não criar um novo model de usuário próprio neste momento.

Motivos:

- o projeto já está integrado à estrutura de autenticação do Django/GeoNode;
- trocar `AUTH_USER_MODEL` depois de migrations existentes costuma ser uma mudança estrutural de alto risco;
- o objetivo de negócio não é substituir autenticação, mas associar o usuário autenticado a uma pessoa/equipe institucional;
- o Django já resolve bem login, senha, sessão, grupos e permissões;
- `Equipe` já carrega a dimensão organizacional necessária para regras de acesso.

O caminho recomendado é manter o `User` padrão como conta de autenticação e vincular `Equipe` ao `User` por uma FK/OneToOne opcional.

### 8.3 Mudança proposta

Adicionar a relação entre `Equipe` e `User` Django:

```python
class Equipe(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_equipe',
        verbose_name='Usuário de autenticação',
    )
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=255)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
```

A escolha por `related_name='perfil_equipe'` evita a leitura equivocada de que a relação pertence apenas ao IEB. O vínculo vale para qualquer equipe de qualquer instituição cadastrada.

Regra de uso:

- autenticação: `request.user`;
- identidade de domínio: `request.user.perfil_equipe`;
- organização/instituição do usuário: `request.user.perfil_equipe.instituicao`;
- projetos autorizados: `EquipeProjeto.objects.filter(equipe=request.user.perfil_equipe)`.

### 8.4 Alternativa futura: múltiplos perfis por usuário

Se no futuro uma mesma pessoa precisar atuar por mais de uma organização ou em múltiplos papéis institucionais, trocar o `OneToOneField` por `ForeignKey` em `Equipe.usuario`, permitindo várias equipes para o mesmo `User`.

Para o ciclo Danida, a recomendação é começar com `OneToOneField`, porque simplifica autenticação e política de acesso. Se houver caso real de um mesmo login atuar em múltiplas instituições, a decisão deve ser reaberta antes da migration.

### 8.5 Replanejamento de T-4.2 e T-4.3

A ideia original de trocar `LeiHistorico.usuario` e `PlanoHistorico.usuario` para FK direta em `User` deve ser reavaliada.

Novo desenho recomendado:

- manter `User` apenas como origem técnica de autenticação;
- adicionar campo `equipe` nos históricos de domínio, apontando para `Equipe`;
- opcionalmente manter `usuario` como FK técnica ou legado, mas o campo preferencial para auditoria funcional deve ser `equipe`;
- nas views, resolver a equipe a partir de `request.user.perfil_equipe` e gravar `equipe=...`.

Exemplo conceitual:

```python
equipe = getattr(request.user, 'perfil_equipe', None)
PlanoHistorico.objects.create(
    plano=plano,
    situacao_anterior=plano.situacao,
    situacao_nova=nova_situacao,
    equipe=equipe,
)
```

### 8.6 Política de acesso por equipe e instituição

A política de acesso deve ser construída em camadas:

1. usuário autenticado precisa ter `Equipe` vinculada;
2. `Equipe` determina a `Instituicao` do usuário;
3. `EquipeProjeto` determina quais projetos o usuário pode acessar;
4. perfis da instituição IEB podem ter escopo ampliado, usando grupos/permissões do Django ou uma marca administrativa na própria instituição/equipe;
5. formulários e listagens devem filtrar projetos, atividades, equipes e registros por esses vínculos;
6. perfis administrativos podem continuar usando permissões/grupos do Django para acesso amplo.

Regra mínima para Danida:

- usuário comum só deve lançar ou visualizar registros de projetos aos quais sua `Equipe` está vinculada via `EquipeProjeto`;
- equipe adicional deve ser selecionável apenas entre equipes vinculadas ao mesmo projeto;
- equipe IEB com permissão administrativa pode acessar todos os projetos Danida;
- registros devem preservar o responsável operacional (`EquipeProjeto`) e, quando houver ação de histórico, a `Equipe` derivada do usuário autenticado.

### 8.7 Nova ordem dentro da Onda D2

Antes de mexer nos históricos de Lei/Plano, executar:

1. confirmar se a relação `User` ↔ `Equipe` será 1:1 ou 1:N para o ciclo Danida;
2. criar `Equipe.usuario` com `related_name='perfil_equipe'`;
3. configurar admin de `Equipe` para buscar/selecionar usuário Django;
4. criar helper de resolução de equipe do usuário autenticado;
5. validar usuários sem equipe vinculada;
6. só então alterar históricos e políticas de acesso.

## 9. Ordem recomendada de execução

1. Executar Onda D0.
2. Executar Onda D1.
3. A partir das lacunas, selecionar tarefas da Onda D2.
4. Executar D3 para formulário, admin e conferência.
5. Executar D4 para homologação.
6. Só depois retomar backlog pós-Danida.

## 10. Critério de sucesso do plano v2

O plano v2 será considerado concluído quando:

- todos os indicadores de `insumos_gerais/indicadores.md:3-26` estiverem mapeados no sistema;
- todos puderem ser lançados em atividade;
- metas forem calculadas corretamente;
- dados puderem ser conferidos em detalhe/admin/relatório;
- nenhuma tarefa de alto risco fora do escopo Danida tiver sido executada sem necessidade;
- backlog pós-Danida estiver organizado para retomada posterior.
- usuários operacionais estiverem vinculados a `Equipe` e `Instituicao`, permitindo política de acesso por projeto/equipe.

## 11. Resumo executivo

O Plano Cirúrgico v1.3 consolidado em `codigo/terralab_v2/plans/v1/` continua válido como fonte técnica, mas deixa de ser o roteiro principal de execução. O novo roteiro é o Plano v2, orientado ao projeto Danida, organizado em `codigo/terralab_v2/plans/v2/`. A prioridade deixa de ser completar ondas 4 e 5 e passa a ser entregar com segurança os tipos `fundos`, `area`, `organizacoes`, `pessoas` e `planos`.

Além disso, o plano passa a tratar autenticação e autorização como parte do domínio: o `User` Django autentica, mas a `Equipe` representa a identidade operacional ligada à `Instituicao` e aos projetos autorizados. O vínculo proposto não é específico do IEB; `perfil_equipe` deve funcionar para equipes de qualquer instituição cadastrada.

A principal decisão é retirar a T-4.5 do caminho crítico e colocá-la no backlog pós-Danida, junto com a modularização de `models.py` e outras melhorias estruturais sem impacto direto nos indicadores atuais.
