# Consulta ao Cliente — Pontos Abertos para o Desenvolvimento Danida v2

**Data:** 2026-04-29
**Versão:** 1.0
**Finalidade:** Subsidiar decisões do cliente (IEB/Danida) para direcionar o planejamento de desenvolvimento.
**Instruções:** Cada ponto contém contexto técnico e uma ou mais perguntas. As respostas do cliente devem ser registradas na coluna **Resposta do Cliente**. Pontos sem resposta serão tratados conforme a premissa padrão indicada ou, na ausência desta, ficarão bloqueados.

---

## Sumário

| Seção | Conteúdo | Quantidade | Impacto se não respondido |
|-------|----------|-----------|--------------------------|
| [A](#a-decisões-bloqueantes) | Decisões Bloqueantes | 7 | Desenvolvimento não pode começar |
| [B](#b-decisões-técnicas-críticas) | Decisões Técnicas Críticas | 5 | Entrega sai com bugs ou cálculos incorretos |
| [C](#c-decisões-de-escopo-e-design) | Decisões de Escopo e Design | 6 | Escopo ambíguo, retrabalho ou lacunas não detectadas |
| [D](#d-decisões-de-segurança) | Decisões de Segurança | 3 | Dados expostos ou contaminados por usuários não autorizados |
| [E](#e-decisões-operacionais) | Decisões Operacionais | 4 | Prestação de contas imprecisa, documentação desatualizada |

---

## A. Decisões Bloqueantes

*Estes pontos precisam de resposta antes do início de qualquer implementação. Sem eles, a Onda D0 não pode ser concluída e todo o desenvolvimento fica parado.*

---

### A.1 — Quais indicadores serão IEB, quais serão financiador, quais serão ambos?

**Contexto técnico:** O sistema distingue dois tipos de indicador:
- `Indicador` (institucional IEB): usado para consolidar estatísticas entre projetos ao longo do tempo.
- `IndicadorFinanciador` (financiador): específico de um financiador; pode ter métricas diferentes do IEB.

É possível cadastrar o mesmo indicador nos dois papéis (ex: um `Indicador` IEB e um `IndicadorFinanciador` Danida equivalentes), com roll-up automático via campo `equivalente_ieb`.

**Referência:** `insumos_gerais/indicadores.md:3-26`, `v2-onda-d0-escopo-danida.md:33-48`

**Perguntas para cada indicador abaixo:**

| # | Indicador Danida | Tipo no sistema | Deve ser IEB? | Deve ser financiador (Danida)? | Ambos? | Se ambos, qual o indicador IEB equivalente? |
|---|------------------|-----------------|---------------|-------------------------------|--------|---------------------------------------------|
| 1 | Número de chamadas do fundo Rutî | `fundos` | ☐ | ☐ | ☐ | |
| 2 | Hectares de agroflorestas implementados | `area` | ☐ | ☐ | ☐ | |
| 3 | Hectares de TIs com autonomia no monitoramento e gestão da informação | `area` | ☐ | ☐ | ☐ | |
| 4 | OIs com aumento no acesso a políticas públicas para geração de renda | `organizacoes` | ☐ | ☐ | ☐ | |
| 5 | OIs com melhoria na gestão organizacional e participação ativa em incidência política para proteção territorial | `organizacoes` | ☐ | ☐ | ☐ | |
| 6 | Castanheiros com aumento na geração de renda | `pessoas` | ☐ | ☐ | ☐ | |
| 7 | Indígenas criadores de gado com aumento da geração de renda | `pessoas` | ☐ | ☐ | ☐ | |
| 8 | Indígenas realizando ações de monitoramento e proteção territorial | `pessoas` | ☐ | ☐ | ☐ | |
| 9 | Indígenas treinados para promover ações de mitigação de mudança climática | `pessoas` | ☐ | ☐ | ☐ | |
| 10 | Indígenas treinados para diversificação da produção e cooperativismo para segurança alimentar | `pessoas` | ☐ | ☐ | ☐ | |
| 11 | Indivíduos treinados em áreas relacionadas ao fortalecimento institucional de OIs | `pessoas` | ☐ | ☐ | ☐ | |
| 12 | Planos de adaptação a mudanças climáticas desenvolvidos e implementados | `planos` | ☐ | ☐ | ☐ | |
| 13 | PGTAs com ações implementadas para mitigação das mudanças climáticas | `planos` | ☐ | ☐ | ☐ | |
| 14 | Plano de negócios da pecuária sustentável desenvolvida | `planos` | ☐ | ☐ | ☐ | |

**Premissa padrão (se não responder):** Bloqueado — não é possível avançar sem esta definição.

**Resposta do Cliente:**

> 

---

### A.2 — Quais desagregações de `pessoas` são obrigatórias para cada indicador?

**Contexto técnico:** O modelo `Pessoas` suporta as seguintes desagregações:
- `total_pessoas` (obrigatório)
- `homens` e `mulheres` (devem somar `total_pessoas` quando ambos preenchidos)
- `jovens` (subconjunto, ≤ total)
- `pct_indigenas`, `pct_extrativistas`, `pct_quilombolas` (percentuais independentes)
- `servidor_publico` (subconjunto, ≤ total)

**Referência:** `v2-onda-d0-escopo-danida.md:51-66`, `v1.3.md:109-118`

**Perguntas para cada indicador de pessoas:**

| # | Indicador | Precisa de total? | Precisa de homens/mulheres? | Precisa de jovens? | Precisa de indígenas? | Precisa de extrativistas? | Precisa de quilombolas? | Precisa de servidor público? |
|---|-----------|-------------------|----------------------------|--------------------|-----------------------|--------------------------|------------------------|------------------------------|
| 1 | Castanheiros com aumento na geração de renda | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Indígenas criadores de gado com aumento da geração de renda | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Indígenas realizando ações de monitoramento e proteção territorial | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Indígenas treinados — mitigação de mudança climática | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Indígenas treinados — diversificação da produção e cooperativismo | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Indivíduos treinados — fortalecimento institucional de OIs | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**Premissa padrão (se não responder):** Assumir apenas `total_pessoas` para todos. Cliente poderá solicitar desagregações adicionais após a entrega.

**Resposta do Cliente:**

> 

---

### A.3 — Quais campos de `organizacoes` são obrigatórios para cada indicador?

**Contexto técnico:** O modelo `Organizacoes` suporta:
- `total_organizacoes` (obrigatório)
- `org_indigena`
- `org_governo` (campo a ser adicionado se necessário)
- `org_foco` (foco de atuação: `implementacao`, `ativ_prod`, `governanca`)
- `org_acesso_politicas_publicas`
- `org_gestao_organizacional`

**Referência:** `v2-onda-d0-escopo-danida.md:67-79`, `v1.3.md:121-130`

**Perguntas:**

| # | Indicador | Precisa de total? | Precisa de org_indigena? | Precisa de org_governo? | Precisa de foco de atuação? | Precisa de acesso a políticas? | Precisa de gestão organizacional? |
|---|-----------|-------------------|-------------------------|------------------------|----------------------------|-------------------------------|----------------------------------|
| 1 | OIs com aumento no acesso a políticas públicas para geração de renda | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | OIs com melhoria na gestão organizacional e incidência política | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**Premissa padrão (se não responder):** Assumir `total_organizacoes` + `org_gestao_organizacional` para o indicador 2; `total_organizacoes` + `org_acesso_politicas_publicas` para o indicador 1.

**Resposta do Cliente:**

> 

---

### A.4 — Qual a regra técnica para hectares de TIs com autonomia? Exige vínculo M2M com Terras Indígenas?

**Contexto técnico:** O modelo `Area` pode registrar hectares de duas formas:
1. **Campo manual:** o usuário digita o valor de `total_ha` diretamente.
2. **Vínculo M2M com TIs:** o sistema soma automaticamente a área das Terras Indígenas selecionadas (via `m2m_changed` signal). Esse mecanismo está planejado mas ainda não foi implementado no código atual.

O indicador "hectares de TIs com autonomia no monitoramento e gestão da informação" sugere que o valor depende de quais TIs estão vinculadas à atividade.

**Referência:** `v2-onda-d0-escopo-danida.md:81-93`, `v1.3.md:147-163`

**Perguntas:**

1. O valor de hectares para o indicador de TIs com autonomia será:
   - ☐ Digitado manualmente pelo usuário em `total_ha`
   - ☐ Calculado automaticamente a partir das TIs vinculadas à atividade (M2M)
   - ☐ Ambos (manual como referência, M2M como valor oficial)

2. Se for M2M, a seleção de TIs será feita:
   - ☐ No formulário de registro de atividade
   - ☐ No admin do Django
   - ☐ Em ambos

3. Qual a unidade e precisão desejada para hectares?
   - ☐ Número inteiro (hectares)
   - ☐ Decimal com 2 casas (hectares com precisão de 0,01 ha)
   - ☐ Decimal com 4 casas (hectares com precisão de 0,0001 ha)

**Premissa padrão (se não responder):** Implementar M2M no formulário. Caso o mecanismo de sinais M2M não esteja pronto, usar campo manual como contingência e migrar para M2M no backlog. Precisão: inteiro.

**Resposta do Cliente:**

> 

---

### A.5 — Qual a regra de contagem para `planos`? Quais situações contam como "desenvolvido" e "implementado"?

**Contexto técnico:** O modelo `Planos` tem os campos:
- `situacao` (estado atual do plano)
- `score` (pontuação)
- `link` (URL para o documento)

O sistema atual calcula metas de planos por contagem de registros ou score, dependendo da configuração. Para os indicadores Danida, precisamos saber o critério exato.

**Referência:** `v2-onda-d0-escopo-danida.md:96-108`, `insumos_gerais/indicadores.md:23-26`

**Perguntas:**

1. Para "planos de adaptação desenvolvidos e implementados", a contagem deve considerar:
   - ☐ Apenas planos com situação "implementado"
   - ☐ Planos com situação "desenvolvido" + "implementado" (contagem cumulativa)
   - ☐ Planos "desenvolvido" contam separado de "implementado" (dois valores)

2. Quais valores de `situacao` o sistema deve usar?
   - ☐ Usar as situações já existentes no sistema
   - ☐ Definir novas situações específicas para o projeto Danida
   - Se novas, quais?

3. Para "PGTAs com ações implementadas", a contagem é:
   - ☐ Número de PGTAs (planos do tipo PGTA) com situação "implementado"
   - ☐ Número de ações dentro de cada PGTA que foram implementadas
   - ☐ Outro critério:

4. Para "plano de negócios da pecuária sustentável desenvolvida", a contagem é:
   - ☐ Número de planos de negócios com situação "desenvolvido"
   - ☐ Score ou pontuação de maturidade do plano
   - ☐ Outro critério:

**Premissa padrão (se não responder):** Contar registros de `Planos` cuja `situacao` seja "implementado" para indicadores que mencionam "implementados"; contar "desenvolvido" para indicadores que mencionam "desenvolvida". Usar situações existentes no sistema.

**Resposta do Cliente:**

> 

---

### A.6 — Qual a regra técnica para `fundos`? Contagem de chamadas, valor total, ou ambos?

**Contexto técnico:** O modelo `Fundo` tem os campos:
- `chamada` (identificador da chamada)
- `valor` (valor da chamada)
- `tipo_fundo` (tipo de fundo)
- Outros campos de detalhamento

O indicador Danida é "número de chamadas do fundo Rutî". É necessário confirmar se a métrica é apenas quantidade, ou se valor também será monitorado.

**Referência:** `v2-onda-d0-escopo-danida.md:110-120`, `insumos_gerais/indicadores.md:3-4`

**Perguntas:**

1. O indicador "número de chamadas do fundo Rutî" mede:
   - ☐ Apenas quantidade de chamadas (contagem de registros)
   - ☐ Quantidade + valor total das chamadas
   - ☐ Apenas valor total

2. O tipo de fundo "Rutî" deve ser:
   - ☐ Um valor na lista de `tipo_fundo` existente
   - ☐ Um novo tipo a ser cadastrado
   - ☐ Um financiador específico no sistema

3. Existe necessidade de rastrear cada chamada individualmente ou apenas o total do período?
   - ☐ Cada chamada como registro individual
   - ☐ Apenas total consolidado por período

**Premissa padrão (se não responder):** Contagem de chamadas (quantidade de registros). Se o campo `valor` estiver preenchido, será exibido no detalhe mas não afetará o cálculo da meta.

**Resposta do Cliente:**

> 

---

### A.7 — O projeto Danida exige consolidação institucional (roll-up) dos indicadores do financiador para o IEB?

**Contexto técnico:** O sistema suporta roll-up via campo `equivalente_ieb` em `IndicadorFinanciador`. Quando um indicador de financiador tem um equivalente IEB, os valores lançados para o financiador são automaticamente contabilizados no indicador IEB, sem duplicação de registro.

Exemplo: "Indígenas treinados em mitigação" (Danida) com `equivalente_ieb` → "Indígenas capacitados em mudanças climáticas" (IEB). Ao registrar 50 pessoas no indicador Danida, esses 50 entram automaticamente no consolidado IEB.

**Referência:** `v2.0.md:156-157`, `v2-onda-d2-correcoes-dominio.md:101-118`, `v1.3.md:10-39`

**Perguntas:**

1. O IEB precisa de consolidação automática dos dados Danida para relatórios institucionais?
   - ☐ Sim, implementar roll-up em todos os indicadores que tiverem equivalente IEB
   - ☐ Sim, mas apenas para alguns indicadores (especificar quais abaixo)
   - ☐ Não, a Danida usa apenas seus próprios indicadores sem consolidação IEB

2. Se sim, o IEB já possui indicadores institucionais equivalentes aos da Danida?
   - ☐ Sim (anexar lista de equivalentes)
   - ☐ Não, será necessário criá-los
   - ☐ Não sei, precisa ser verificado

**Premissa padrão (se não responder):** Não implementar roll-up. Se for necessário depois, entrará como tarefa adicional.

**Resposta do Cliente:**

> 

---

## B. Decisões Técnicas Críticas

*Estes pontos não bloqueiam o início do desenvolvimento, mas impactam diretamente a qualidade e a integridade dos dados entregues. Recomenda-se resposta antes da Onda D2.*

---

### B.1 — O sistema deve exigir autenticação para criar registros de atividade?

**Contexto técnico:** Atualmente, qualquer visitante do sistema (incluindo usuários não autenticados) pode acessar o formulário de registro de atividade e criar dados. Apenas a tela de indicadores exige login.

Para o projeto Danida, isso significa que dados podem ser inseridos por pessoas não autorizadas, contaminando os relatórios. A correção é adicionar `@login_required` em aproximadamente 15 views (formulário, criação de satélites, monitoramento), o que representa cerca de 20 linhas de código e risco baixo.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:54-58`

**Perguntas:**

1. O formulário de registro de atividade deve exigir autenticação?
   - ☐ Sim, todos os usuários devem estar logados para lançar dados
   - ☐ Sim, mas apenas para produção (ambiente de teste pode ficar aberto)
   - ☐ Não, manter acesso aberto como está

2. Se exigir autenticação, qual o critério de autorização?
   - ☐ Qualquer usuário logado pode registrar atividades
   - ☐ Apenas usuários vinculados a uma Equipe do projeto
   - ☐ Apenas usuários com perfil IEB administrativo

**Premissa padrão (se não responder):** Adicionar `@login_required` em todas as views de escrita. Qualquer usuário logado pode registrar. A política de autorização por equipe será implementada posteriormente.

**Resposta do Cliente:**

> 

---

### B.2 — A tela de detalhe da atividade deve ser corrigida para exibir os indicadores?

**Contexto técnico:** A tela de detalhe da atividade (`atividade_registro_detalhe.html`) referencia variáveis com nomes que a view não passa. Como resultado, a seção de indicadores nunca renderiza — o usuário vê a atividade mas não vê quantas pessoas, organizações, hectares ou planos foram registrados.

Corrigir isso exige renomear as variáveis no template para bater com o que a view realmente fornece (`pessoas`, `organizacoes`, `area`, `areas_protegidas`) ou ajustar a view para passar as variáveis que o template espera. Estimativa: ~30 linhas, risco baixo.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:16-21`

**Perguntas:**

1. A tela de detalhe precisa exibir os indicadores lançados?
   - ☐ Sim, é essencial para conferência e auditoria dos lançamentos
   - ☐ Sim, mas apenas o resumo (totais), sem desagregações
   - ☐ Não, a conferência será feita pelo admin do Django ou relatório externo

2. O template de PDF (usado para exportar o registro) também deve ser corrigido?
   - ☐ Sim, PDF deve mostrar os mesmos dados do detalhe
   - ☐ Não, PDF não será usado no projeto Danida

**Premissa padrão (se não responder):** Corrigir template de detalhe e PDF. Exibir totais e desagregações quando disponíveis.

**Resposta do Cliente:**

> 

---

### B.3 — O cálculo de hectares vinculados a Terras Indígenas exige correção de arquitetura?

**Contexto técnico:** O modelo `Area` atualmente calcula `total_ha` no método `save()`, o que não cobre alterações feitas pelo admin do Django, shell ou futura API. A correção recomendada é substituir essa lógica por sinais `m2m_changed`, que disparam automaticamente em qualquer alteração da relação entre Atividade e TIs.

Essa correção (T-3.1 do plano anterior) é necessária se o indicador de TIs com autonomia (A.4) usar M2M. Sem ela, hectares podem ficar inconsistentes.

**Referência:** `v1.3.md:147-163`, `v2-onda-d2-correcoes-dominio.md:197-214`, `analise-pontos-cegos-terralab-v2-1.0.md:84-87`

**Perguntas:**

1. Os dados de hectares serão inseridos principalmente por qual via?
   - ☐ Formulário de registro de atividade (onde o `save()` funciona)
   - ☐ Admin do Django (onde o `save()` atual NÃO funciona para M2M)
   - ☐ Ambos

2. Se a resposta de A.4 for "M2M com TIs", devemos implementar os sinais `m2m_changed` agora ou postergar?
   - ☐ Implementar agora (parte da Onda D2)
   - ☐ Postergar para o backlog pós-Danida (assumir risco de inconsistência)

**Premissa padrão (se não responder):** Se A.4 usar M2M, implementar sinais `m2m_changed` na Onda D2. Caso contrário, postergar.

**Resposta do Cliente:**

> 

---

### B.4 — O sistema deve suportar indicadores de `planos` como financiador?

**Contexto técnico:** O código atual (`views.py:638`) tem um problema: quando um indicador é do tipo `planos` e pertence a um financiador (`IndicadorFinanciador`), os dados de planos são ignorados no salvamento. Apenas planos vinculados a `Indicador` IEB são persistidos.

Se a Danida usar indicadores de planos como financiador (A.1), essa correção é obrigatória. É uma tarefa de ~20 linhas, risco baixo.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:28-31`, `v2-onda-d2-correcoes-dominio.md:139-157`

**Perguntas:**

1. A Danida usará indicadores de planos como `IndicadorFinanciador`?
   - ☐ Sim (decorre da resposta A.1)
   - ☐ Não (decorre da resposta A.1)
   - ☐ Ainda não definido

**Premissa padrão (se não responder):** Se A.1 indicar planos como financiador, implementar a correção. Caso contrário, não implementar.

**Resposta do Cliente:**

> 

---

### B.5 — Qual a precisão decimal exigida para áreas e metas?

**Contexto técnico:** Os campos de área geográfica (`total_ha`, `area`) atualmente usam `FloatField`, que pode acumular erros de arredondamento em somatórios de dashboards. A recomendação técnica é migrar para `DecimalField(max_digits=12, decimal_places=4)`, que garante precisão exata.

Essa mudança envolve ~8 migrations e alterações em todos os modelos de área e nas properties de `Meta.realizado`. É um trabalho de ~2-3 horas, risco médio (requer cuidado com dados existentes).

**Referência:** `v1.3.md:397-402`, `v2-onda-d2-correcoes-dominio.md:216-234`

**Perguntas:**

1. A precisão atual (número decimal com possíveis erros de arredondamento) é aceitável para o relatório Danida?
   - ☐ Sim, a precisão atual é suficiente
   - ☐ Não, precisão decimal exata é obrigatória
   - ☐ Não sei, preciso de orientação técnica

2. Se for necessária precisão exata, a migração deve ser feita:
   - ☐ Na Onda D2 (antes da entrega Danida)
   - ☐ No backlog pós-Danida (assumindo risco de imprecisão na primeira entrega)

**Premissa padrão (se não responder):** Manter `FloatField` atual. Migrar para `DecimalField` no backlog.

**Resposta do Cliente:**

> 

---

## C. Decisões de Escopo e Design

*Estes pontos definem o que será executado e o que ficará para depois. Impactam principalmente o tamanho da Onda D2.*

---

### C.1 — Como deve funcionar a política de acesso por equipe?

**Contexto técnico:** O plano v2 propõe vincular cada usuário do sistema a uma `Equipe`, que por sua vez pertence a uma `Instituicao` (ex: IEB, CIR, etc.). O acesso aos projetos seria controlado por `EquipeProjeto`.

Hoje o sistema não tem essa camada — qualquer usuário logado vê todos os projetos e pode lançar dados em qualquer um deles.

**Referência:** `v2.0.md:256-372`, `v2-onda-d2-correcoes-dominio.md:24-78`

**Perguntas:**

1. Para o projeto Danida, diferentes organizações (IEB, CIR, outras) precisam de acessos separados?
   - ☐ Sim, cada organização deve ver apenas seus próprios projetos e dados
   - ☐ Não, todos os usuários podem ver todos os projetos Danida
   - ☐ Apenas o IEB acessa o sistema; outras organizações não terão usuários

2. Um mesmo usuário pode atuar por mais de uma organização?
   - ☐ Sim (ex: mesma pessoa trabalha no IEB e na CIR)
   - ☐ Não, cada usuário pertence a uma única organização

3. Qual a urgência dessa política de acesso?
   - ☐ Deve estar pronta para a entrega Danida (Onda D2)
   - ☐ Pode ficar para depois da entrega Danida (backlog)
   - ☐ Apenas a preparação técnica (vínculo User-Equipe), sem filtros de acesso ainda

**Premissa padrão (se não responder):** Implementar apenas o vínculo `User` → `Equipe` (preparação técnica, T-D2.0). Não implementar filtros de acesso por projeto (T-D2.1). Todos os usuários logados continuam vendo todos os projetos.

**Resposta do Cliente:**

> 

---

### C.2 — Os históricos de Leis e Planos devem registrar a equipe responsável?

**Contexto técnico:** Os modelos `LeiHistorico` e `PlanoHistorico` registram alterações de situação com um campo `usuario` que armazena o nome como texto (`CharField`). Não há vínculo com a entidade `Equipe` ou `User`, dificultando auditoria.

A proposta é adicionar um campo `equipe` (FK para `Equipe`) nesses históricos, preservando a identidade organizacional de quem fez a alteração.

**Referência:** `v2.0.md:322-343`, `v2-onda-d2-correcoes-dominio.md:79-98`, `v1.3.md:217-229`

**Perguntas:**

1. É importante saber qual equipe/organização alterou a situação de um plano ou lei?
   - ☐ Sim, para auditoria e rastreabilidade
   - ☐ Não, o histórico atual (nome textual) é suficiente

2. Esta alteração deve ser feita:
   - ☐ Na Onda D2 (antes da entrega Danida)
   - ☐ No backlog pós-Danida

**Premissa padrão (se não responder):** Postergar para o backlog. Manter histórico com `CharField` atual durante o ciclo Danida.

**Resposta do Cliente:**

> 

---

### C.3 — O tipo de indicador "Outro" deve ser removido do sistema?

**Contexto técnico:** O tipo `outro` existia em `INDICADOR_TIPO_CHOICES` como reserva para indicadores que não se encaixam nos demais tipos. Foi removido do código (P1.14 do plano v1.3), mas:
- O modelo `Outro` ainda existe no banco
- O `GUIA_INDICADORES.md` ainda o lista como tipo disponível
- Nenhum dado real foi registrado com este tipo

**Referência:** `v1.3.md:347-354`, `v2.0.md:219`

**Perguntas:**

1. Existe possibilidade de uso futuro do tipo "Outro"?
   - ☐ Sim, manter no código (corrigir apenas a documentação)
   - ☐ Não, remover completamente (modelo + choices + documentação)
   - ☐ Manter como está, resolver depois

2. Se for remover, quando?
   - ☐ Na Onda D2 (aproveitar o ciclo de desenvolvimento)
   - ☐ No backlog pós-Danida

**Premissa padrão (se não responder):** Postergar para o backlog pós-Danida (B2). Não incluir na Onda D2.

**Resposta do Cliente:**

> 

---

### C.4 — A Onda D2 tem 8 tarefas condicionais. Qual o critério para decidir se cada uma será executada?

**Contexto técnico:** Das 10 tarefas da Onda D2, apenas 2 são obrigatórias (T-D2.0 e T-D2.1). As outras 8 dependem de confirmação da Onda D0 ou D1. Algumas dessas decisões já estão cobertas por perguntas anteriores (B.4, B.5), mas outras dependem de validação técnica.

Para evitar ambiguidade, precisamos de um protocolo claro de decisão.

**Referência:** `v2-onda-d2-correcoes-dominio.md:102-232`

**Perguntas:**

| Tarefa | Descrição | Condição para executar | Decisão do cliente |
|--------|-----------|----------------------|-------------------|
| T-D2.3 | `equivalente_ieb` em `IndicadorFinanciador` | Danida usar indicador financiador com equivalente IEB (ver A.7) | ☐ Executar ☐ Pular |
| T-D2.4 | Constraints e correções em `Fundo` | D1 encontrar lacuna em fundos | ☐ Executar se houver lacuna ☐ Executar sempre ☐ Pular |
| T-D2.5 | `Planos` com `IndicadorFinanciador` | Planos como financiador (ver B.4) | ☐ Executar ☐ Pular |
| T-D2.6 | Constraints em `Pessoas` | D1 encontrar lacuna ou D0 exigir desagregações | ☐ Executar se houver lacuna ☐ Executar sempre ☐ Pular |
| T-D2.7 | `Organizacoes` + `org_governo` | D0 confirmar necessidade de subgrupos | ☐ Executar se houver lacuna ☐ Executar sempre ☐ Pular |
| T-D2.8 | Sinais M2M para `Area`/TIs | A.4 confirmar M2M (ver B.3) | ☐ Executar ☐ Pular |
| T-D2.9 | `DecimalField` para áreas/metas | Precisão decimal exigida (ver B.5) | ☐ Executar ☐ Pular |
| T-D2.2 | Históricos de Lei/Plano com `Equipe` | Auditoria por equipe necessária (ver C.2) | ☐ Executar ☐ Pular |

**Premissa padrão (se não responder):** A equipe técnica decidirá com base nos resultados objetivos de D0 e D1, documentando cada decisão.

**Resposta do Cliente:**

> 

---

### C.5 — O sistema precisa de testes automatizados para a entrega Danida?

**Contexto técnico:** O projeto atualmente tem zero testes automatizados. Toda a validação é manual — um operador testa cada tipo de indicador no formulário e confere visualmente.

A Onda D4 prevê homologação 100% manual (T-D4.3 e T-D4.4). Isso funciona para a primeira entrega, mas qualquer alteração futura pode quebrar funcionalidades sem ser detectada.

**Referência:** `v2-onda-d4-homologacao.md:56-91`, `analise-pontos-cegos-terralab-v2-1.0.md:164-165`

**Perguntas:**

1. Testes automatizados são necessários para a entrega Danida?
   - ☐ Sim, incluir testes básicos para os 5 tipos Danida
   - ☐ Não, a homologação manual é suficiente para esta entrega
   - ☐ Incluir apenas testes de cálculo de metas (parte mais crítica)

2. Se forem incluídos, em qual onda?
   - ☐ Onda D3 (junto com ajustes de formulário)
   - ☐ Onda D4 (junto com homologação)
   - ☐ Onda separada entre D3 e D4

**Premissa padrão (se não responder):** Não incluir testes automatizados neste ciclo. Homologação 100% manual. Adicionar ao backlog pós-Danida.

**Resposta do Cliente:**

> 

---

### C.6 — A tarefa de Planos com indicador financiador (T-D2.5) já foi executada no plano anterior?

**Contexto técnico:** Existe uma sobreposição entre a tarefa T-B.1 do plano v1.3 ("Planos com indicador financiador") e a tarefa T-D2.5 do plano v2 (mesmo objetivo). Se T-B.1 já foi concluída, T-D2.5 é redundante.

Verificação pendente: analisar o código atual para confirmar se a correção já está aplicada.

**Referência:** `PLANO_CIRURGICO_TAREFAS.md:81`, `v2-onda-d2-correcoes-dominio.md:139-157`

**Perguntas:**

1. A equipe técnica deve verificar se T-B.1 já foi executada antes de decidir sobre T-D2.5?
   - ☐ Sim, verificar e reportar
   - ☐ Não, executar T-D2.5 de qualquer forma (garantia de que está feito)

**Premissa padrão (se não responder):** Verificar o código. Se T-B.1 já estiver aplicada, pular T-D2.5. Caso contrário, executar se B.4 indicar necessidade.

**Resposta do Cliente:**

> 

---

## D. Decisões de Segurança

*Estes pontos afetam a integridade dos dados e devem ser endereçados antes da entrada em produção, mesmo que não bloqueiem o desenvolvimento.*

---

### D.1 — O sistema deve ter proteção CSRF em todas as operações de criação de dados?

**Contexto técnico:** Das 9 views AJAX que criam ou alteram dados (adicionar parceria, adicionar plano, atualizar situação, etc.), 6 operam sem token CSRF e 3 usam `@csrf_exempt` (desabilitam a proteção explicitamente). Isso significa que um site malicioso pode, em teoria, forjar requisições para criar dados no sistema se a vítima estiver logada.

O Django oferece proteção CSRF nativa; configurá-la corretamente é questão de adicionar o token no template e remover os `@csrf_exempt`.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:42-52`

**Perguntas:**

1. A proteção CSRF deve ser corrigida para a entrega Danida?
   - ☐ Sim, corrigir todas as views na Onda D2
   - ☐ Sim, mas apenas as views que afetam os tipos Danida (pessoas, organizacoes, area, fundos, planos)
   - ☐ Não, postergar para o backlog

2. Qual o ambiente de produção?
   - ☐ Acesso restrito (rede interna / VPN) — risco menor
   - ☐ Internet pública — risco maior
   - ☐ Ambos

**Premissa padrão (se não responder):** Corrigir CSRF nas views dos tipos Danida na Onda D2. Demais views no backlog.

**Resposta do Cliente:**

> 

---

### D.2 — O sistema deve ter validação de que a equipe selecionada pertence ao projeto informado?

**Contexto técnico:** No formulário de registro de atividade, o campo `equipe_projeto` é populado via AJAX com base no projeto selecionado (validação client-side). No servidor, porém, não há verificação de que a equipe realmente pertence àquele projeto. Um usuário malicioso pode manipular o POST para vincular uma equipe de outro projeto.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:116-118`

**Perguntas:**

1. A validação server-side de consistência entre projeto e equipe deve ser implementada?
   - ☐ Sim, na Onda D2
   - ☐ Não, postergar para o backlog
   - ☐ Não, o risco é aceitável para o ambiente atual

**Premissa padrão (se não responder):** Postergar para o backlog. Risco considerado aceitável para ambiente de acesso restrito.

**Resposta do Cliente:**

> 

---

### D.3 — O sistema deve ter validação de que a atividade selecionada pertence ao componente informado?

**Contexto técnico:** Mesmo problema de D.2, mas para a relação Atividade ↔ Componente. O formulário filtra client-side, mas o servidor não valida.

**Referência:** `analise-pontos-cegos-terralab-v2-1.0.md:120-121`

**Perguntas:**

1. A validação server-side de consistência entre componente e atividade deve ser implementada?
   - ☐ Sim, na Onda D2
   - ☐ Não, postergar para o backlog
   - ☐ Não, o risco é aceitável para o ambiente atual

**Premissa padrão (se não responder):** Postergar para o backlog. Mesmo critério de D.2.

**Resposta do Cliente:**

> 

---

## E. Decisões Operacionais

*Estes pontos não são técnicos, mas afetam a gestão do projeto. Recomenda-se resposta durante a Onda D0.*

---

### E.1 — Qual o mapeamento entre as ondas de desenvolvimento e os produtos contratuais?

**Contexto técnico:** O contrato com o IEB está organizado em 8 produtos (P1 a P8), totalizando 446 horas. As ondas de desenvolvimento v2 (D0 a D4) não têm correspondência 1:1 com esses produtos. Para prestação de contas, é necessário saber como as horas de cada onda serão alocadas.

**Referência:** `proposta/Tarefas_Projetos_IEB.md:1-146`, `README.md:133`

**Mapeamento sugerido:**

| Onda v2 | Descrição | Produto contratual sugerido |
|---------|-----------|---------------------------|
| D0 | Congelamento de escopo | P2: Configuração de Formulários |
| D1 | Validação de fluxo | P2: Configuração de Formulários |
| D2 | Correções de domínio | P2: Formulários + P8: Customização e Acesso |
| D3 | Formulário, admin e relatório | P2: Formulários + P8: Customização e Acesso |
| D4 | Homologação | P2: Formulários + P4: Dashboard + P8: Acesso |

**Perguntas:**

1. O mapeamento sugerido acima está correto? Se não, qual o mapeamento desejado?
   - ☐ Mapeamento sugerido está correto
   - ☐ Mapeamento diferente (descrever abaixo)

**Resposta do Cliente:**

> 

---

### E.2 — O membro da equipe "epassarojr" (formulário v2) está disponível para o ciclo Danida?

**Contexto técnico:** O formulário v2 foi desenvolvido com contribuições do colaborador **epassarojr** (Fases B-F do formulário). Se houver necessidade de manutenção nesses componentes durante a Onda D3, é importante saber se esse conhecimento está disponível.

**Referência:** `horas/REGRAS.md:42`, `CLAUDE.md:61`

**Perguntas:**

1. O colaborador epassarojr está disponível para suporte durante o ciclo Danida?
   - ☐ Sim, disponível se necessário
   - ☐ Não disponível; é necessário knowledge transfer prévio
   - ☐ Não disponível e não é necessário (a equipe atual cobre o conhecimento)

2. Se não disponível, existe documentação suficiente do formulário v2 para manutenção?
   - ☐ Sim
   - ☐ Não
   - ☐ Não sei

**Resposta do Cliente:**

> 

---

### E.3 — O ambiente Docker/GeoNode está funcional para desenvolvimento e teste?

**Contexto técnico:** O ambiente Docker foi validado em 2026-04-27. De lá para cá, pode ter ocorrido alguma quebra (dependências, atualizações de sistema, mudanças de configuração). As Ondas D1 e D4 dependem desse ambiente para validação e homologação.

**Referência:** `PLANO_CIRURGICO_TAREFAS.md:10-29`

**Perguntas:**

1. O ambiente Docker local está atualmente funcional?
   - ☐ Sim, testado e funcionando
   - ☐ Não testado recentemente
   - ☐ Não, precisa de manutenção

2. Se não estiver funcional, quem é responsável por restaurá-lo?
   - ☐ Equipe de desenvolvimento
   - ☐ Equipe de infraestrutura do IEB
   - ☐ Outro:

**Resposta do Cliente:**

> 

---

### E.4 — Há previsão de treinamento ou capacitação dos operadores que usarão o sistema?

**Contexto técnico:** O sistema será usado por operadores do IEB e possivelmente de outras organizações para lançar dados do projeto Danida. O plano atual cobre desenvolvimento e homologação, mas não inclui capacitação de usuários.

**Referência:** `proposta/Tarefas_Projetos_IEB.md:36-53` (P3: Oficinas Participativas)

**Perguntas:**

1. Os operadores que lançarão dados no sistema já conhecem a ferramenta?
   - ☐ Sim, já usam o sistema atualmente
   - ☐ Não, precisam de capacitação
   - ☐ Parcialmente (alguns conhecem, outros não)

2. Se precisarem de capacitação, ela está coberta por qual produto contratual?
   - ☐ P3 (Oficinas Participativas)
   - ☐ P8 (Customização e Acesso)
   - ☐ Precisa ser adicionada ao escopo
   - ☐ Não está no escopo; operadores aprenderão com documentação

**Resposta do Cliente:**

> 

---

## F. Resumo para Decisão

| # | Ponto | Seção | Impacto se não responder | Respondido? |
|---|-------|-------|--------------------------|-------------|
| A.1 | IEB vs financiador vs ambos | A | Bloqueia D0 | ☐ |
| A.2 | Desagregações de pessoas | A | Bloqueia D0 | ☐ |
| A.3 | Campos de organizações | A | Bloqueia D0 | ☐ |
| A.4 | Regra de hectares / M2M com TIs | A | Bloqueia D0 e D2 | ☐ |
| A.5 | Regra de contagem de planos | A | Bloqueia D0 | ☐ |
| A.6 | Regra de fundos | A | Bloqueia D0 | ☐ |
| A.7 | Roll-up IEB | A | Bloqueia D2 (T-D2.3) | ☐ |
| B.1 | Autenticação obrigatória | B | Entrega com risco de contaminação de dados | ☐ |
| B.2 | Correção da tela de detalhe | B | Auditoria quebrada | ☐ |
| B.3 | Sinais M2M para hectares | B | Cálculo de hectares pode falhar | ☐ |
| B.4 | Planos como financiador | B | Dados de planos podem ser perdidos | ☐ |
| B.5 | Precisão decimal | B | Imprecisão em relatórios | ☐ |
| C.1 | Política de acesso por equipe | C | Escopo ambíguo na D2 | ☐ |
| C.2 | Históricos com Equipe | C | Escopo ambíguo na D2 | ☐ |
| C.3 | Remoção do tipo "Outro" | C | Escopo ambíguo na D2 | ☐ |
| C.4 | Protocolo de decisão D2 | C | Risco de executar tarefas desnecessárias | ☐ |
| C.5 | Testes automatizados | C | Cobertura zero | ☐ |
| C.6 | Verificar T-B.1 vs T-D2.5 | C | Risco de retrabalho | ☐ |
| D.1 | Proteção CSRF | D | Dados expostos | ☐ |
| D.2 | Validação equipe-projeto | D | Inconsistência de dados | ☐ |
| D.3 | Validação componente-atividade | D | Inconsistência de dados | ☐ |
| E.1 | Mapeamento ondas × produtos | E | Prestação de contas imprecisa | ☐ |
| E.2 | Disponibilidade epassarojr | E | Risco de bloqueio na D3 | ☐ |
| E.3 | Ambiente Docker | E | Bloqueia D1 e D4 | ☐ |
| E.4 | Capacitação de operadores | E | Adoção do sistema | ☐ |

---

## G. Próximos Passos

1. **Cliente preenche** as respostas neste documento.
2. **Equipe técnica analisa** as respostas e atualiza:
   - Matriz D0 com decisões dos pontos A.1 a A.7.
   - Arquivo `v2-onda-d2-correcoes-dominio.md` com decisões dos pontos B.3, B.4, B.5, C.4.
   - Plano principal `v2.0.md` com ajustes de escopo decorrentes.
3. **Onda D0 é concluída** com base nas respostas (itens sem resposta usarão premissa padrão).
4. **Desenvolvimento prossegue** para D1 com o escopo congelado.

---

*Documento gerado em 2026-04-29 a partir da análise completa dos arquivos de planejamento v2, código-fonte (`models.py`, `views.py`), análise de pontos cegos, propostas contratuais e regras operacionais.*
