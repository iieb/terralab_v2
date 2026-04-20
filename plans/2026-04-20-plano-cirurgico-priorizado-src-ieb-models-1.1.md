# Plano Cirúrgico Priorizado — Evolução de `src/ieb/models.py`

## Objective

Reorganizar o backlog cirúrgico de `src/ieb/models.py` por prioridade arquitetural e risco de banco, explicitando o contexto e as premissas de cada mudança para facilitar revisão técnica e debate entre outros desenvolvedores antes de qualquer implementação.

## Contexto e Fontes

- Arquivo principal analisado: `src/ieb/models.py:1-1300`
- Núcleo hierárquico do domínio: `src/ieb/models.py:128-312`
- Estrutura de indicadores e metas: `src/ieb/models.py:344-567`
- Registro operacional central: `src/ieb/models.py:570-623`
- Modelos satélite com dupla referência de indicador: `src/ieb/models.py:666-1178`
- Modelos de histórico: `src/ieb/models.py:810-818`, `src/ieb/models.py:999-1007`
- Modelos complementares finais: `src/ieb/models.py:1180-1300`

## Assumptions

- O sistema deve continuar tratando `AtividadeRegistro` como o centro do fato operacional do domínio, e não há intenção imediata de romper esse desenho.
- A principal hipótese desta análise é que os maiores riscos atuais não estão na hierarquia `Projeto → Componente → Atividade`, mas na integridade relacional e semântica das tabelas satélite ligadas a indicadores.
- Sempre que houver conflito entre “reduzir duplicação” e “preservar segurança da migração”, a prioridade recomendada é primeiro endurecer o modelo atual e só depois avaliar consolidação de models.
- Algumas mudanças sugeridas dependem de validar dados já existentes antes de impor novas constraints; portanto, várias tarefas assumem uma etapa prévia de diagnóstico e saneamento.
- A eventual unificação de `Indicador` com `IndicadorFinanciador`, e de `Meta` com `MetaFinanciador`, é uma hipótese de melhoria estrutural, não uma decisão já tomada.

## Critério de Priorização

### P0 — Integridade e risco direto de inconsistência
Mudanças nesta faixa atacam situações em que o banco pode aceitar estados inválidos, produzir relatórios incorretos ou permitir ambiguidade estrutural relevante.

### P1 — Coerência do domínio e governança do dado
Mudanças nesta faixa fortalecem regras de negócio, chaves de negócio, auditoria e consistência analítica, mas sem o mesmo potencial imediato de corrupção estrutural dos itens P0.

### P2 — Qualidade arquitetural e redução de dívida técnica
Mudanças nesta faixa melhoram clareza, modularização, precisão e evolutividade, mas podem ser feitas depois que o modelo estiver mais seguro.

## Implementation Plan

### P0 — Integridade estrutural do banco

- [ ] **Trecho: `src/ieb/models.py:344-442` — mapear formalmente o contrato entre `Indicador` e `IndicadorFinanciador` antes de qualquer alteração estrutural.** Racional: a suposição atual do código é que existem dois universos paralelos de indicador, mas isso não está formalizado no banco nem no domínio. Outros devs precisam opinar se essa separação é realmente conceitual ou apenas histórica, porque essa resposta muda todo o plano posterior.
- [ ] **Trecho: `src/ieb/models.py:666-1178` — definir a regra de exclusividade entre `indicador` e `indicador_financiador` em todos os models satélite.** Racional: o desenho atual assume que um registro pertence a um indicador institucional ou a um indicador de financiador, mas o banco não protege essa hipótese. A mudança assume que o preenchimento deve ser exclusivo, e essa premissa precisa ser validada pelo time antes de virar constraint.
- [ ] **Trecho: `src/ieb/models.py:666-1178` — substituir `unique_together` dependente de `indicador` por `UniqueConstraint` condicionais para os dois cenários de vínculo.** Racional: hoje a unicidade foi desenhada como se só existisse `indicador`, mas vários models também usam `indicador_financiador`. A mudança assume que a unicidade correta depende do tipo de vínculo, e não apenas do campo legado `indicador`.
- [ ] **Trecho: `src/ieb/models.py:666-695` — revisar `Area` para que unicidade e somatório não dependam de um estado ambíguo de indicador.** Racional: esse model já materializa a fragilidade central do arquivo: dupla FK opcional e total persistido. A mudança assume que `Area` deve representar um único contexto analítico por registro, e não aceitar ambiguidade.
- [ ] **Trecho: `src/ieb/models.py:699-734` — revisar `AreasProtegidas` com a mesma estratégia de exclusividade e unicidade condicional.** Racional: o model replica o padrão problemático de `Area` e adiciona mais agregados persistidos. A mudança assume que o mesmo contrato lógico deve valer para os dois modelos.
- [ ] **Trecho: `src/ieb/models.py:743-761` — corrigir a integridade lógica de `Pessoas` no vínculo com indicador e nas desagregações.** Racional: a estrutura atual aceita estados onde o registro pode estar mal vinculado ou ter subtotais incoerentes com o total. A mudança assume que desagregações devem respeitar algum contrato mínimo em relação ao total informado.
- [ ] **Trecho: `src/ieb/models.py:821-835` — revisar `Organizacoes` para impedir incoerência entre o total informado e seus subtotais.** Racional: o model assume implicitamente que os subtotais descrevem o total, mas isso não é garantido. Outros devs devem validar se os subtotais são exaustivos ou apenas informativos, porque essa resposta muda a regra de constraint.
- [ ] **Trecho: `src/ieb/models.py:838-857` — estabilizar a regra de cálculo de `Evento.total` e validar se campos nulos equivalem a zero ou a “não informado”.** Racional: o cálculo atual soma apenas valores truthy. A mudança assume que a semântica de vazio precisa ser definida com clareza para evitar totais analiticamente errados.
- [ ] **Trecho: `src/ieb/models.py:764-805` — revisar `Leis` para que os agregados persistidos não dependam exclusivamente de `save()` com M2M.** Racional: a mudança assume que totais derivados precisam refletir o estado real da relação M2M, e não apenas o momento de criação/edição do registro principal.
- [ ] **Trecho: `src/ieb/models.py:1010-1053` — revisar `Parcerias` com o mesmo princípio de atualização confiável dos totais M2M.** Racional: a premissa é que o valor persistido deve ser confiável mesmo quando a relação M2M muda fora do fluxo originalmente pensado pela view.
- [ ] **Trecho: `src/ieb/models.py:1091-1137` — revisar `Produtos` para quebrar a dependência frágil entre M2M e agregados persistidos.** Racional: o padrão se repete e sugere dívida sistêmica, não caso isolado.
- [ ] **Trecho: `src/ieb/models.py:1143-1175` — revisar `Contratos` para garantir consistência de `valor_total` e evitar `NULL` sem semântica clara.** Racional: a mudança assume que “sem contratos com valor” não deve ficar indistinto de “valor não calculado”. Isso precisa de consenso funcional.
- [ ] **Trecho: `src/ieb/models.py:570-590` — adicionar integridade temporal mínima em `AtividadeRegistro` (`data_final >= data_inicio`).** Racional: essa é uma suposição básica de domínio e, se verdadeira, deve ser protegida pelo banco para evitar registros operacionalmente inválidos.
- [ ] **Trecho: `src/ieb/models.py:445-567` — adicionar integridade temporal mínima em `Meta` e `MetaFinanciador` (`data >= data_inicio`, quando aplicável).** Racional: a mudança assume que metas sempre representam uma janela temporal coerente; se houver exceções de negócio, elas devem ser explicitadas antes da constraint.
- [ ] **Arquivo: `src/ieb/models.py` — introduzir `CheckConstraint` para exclusividade entre indicadores, datas coerentes e não negatividade de campos quantitativos essenciais.** Racional: a maior parte da integridade hoje está implícita na aplicação. A mudança assume que o banco deve proteger o núcleo semântico mínimo do domínio.

### P1 — Coerência de domínio, auditoria e chaves de negócio

- [ ] **Trecho: `src/ieb/models.py:445-567` — revisar a duplicação entre `Meta` e `MetaFinanciador` e documentar claramente por que ela existe antes de qualquer consolidação.** Racional: a mudança assume que reduzir duplicação pode ser desejável, mas só faz sentido se os dois modelos realmente expressarem o mesmo conceito com diferença apenas de escopo.
- [ ] **Trecho: `src/ieb/models.py:810-818` — substituir a auditoria textual de `LeiHistorico.usuario` por uma relação real com o usuário do sistema.** Racional: a suposição é que auditoria deve apontar para identidade real e não para texto livre; isso melhora rastreabilidade, mas exige alinhamento sobre o modelo de autenticação esperado.
- [ ] **Trecho: `src/ieb/models.py:999-1007` — aplicar a mesma correção de auditoria em `PlanoHistorico.usuario`.** Racional: a mudança assume que histórico de plano e de lei devem seguir o mesmo padrão de governança.
- [ ] **Trecho: `src/ieb/models.py:934-992` — separar conceitualmente em `Planos` o que é catálogo, o que é evento de mudança e o que é atualização do estado corrente.** Racional: o `save()` atual mistura responsabilidades. A mudança assume que o time quer um modelo mais explícito de transição de estado e histórico.
- [ ] **Trecho: `src/ieb/models.py:12-41` — adicionar unicidade lógica a `OIRegLoc`.** Racional: a suposição é que o mesmo par regional-local não deveria ser cadastrado repetidamente.
- [ ] **Trecho: `src/ieb/models.py:82-95` — adicionar unicidade lógica a `TIsIGATI`.** Racional: a mudança assume que um mesmo vínculo IGATI-TI não deveria existir mais de uma vez sem metadado adicional.
- [ ] **Trecho: `src/ieb/models.py:189-210` — adicionar unicidade lógica a `EquipeProjeto`, `ProjetoOI` e `ProjetoTI`.** Racional: a estrutura atual assume implicitamente que esses pares são únicos; a mudança apenas explicita isso no banco.
- [ ] **Trecho: `src/ieb/models.py:169-186` — definir unicidade contextual para `Componente.codigo` e `Atividade.codigo`.** Racional: a mudança assume que códigos são identificadores operacionais dentro do seu escopo hierárquico, não apenas rótulos livres.
- [ ] **Trecho: `src/ieb/models.py:253-260` — definir unicidade contextual para `Subatividade.codigo`.** Racional: mesma premissa dos códigos hierárquicos acima.
- [ ] **Trecho: `src/ieb/models.py:101-124` — revisar identificadores institucionais (`sigla`, CPF, CNPJ) para decidir quais são apenas informativos e quais são chaves de negócio.** Racional: antes de impor unicidade, o time precisa concordar se esses campos são realmente identificadores canônicos ou apenas campos de cadastro.
- [ ] **Trecho: `src/ieb/models.py:1060-1088` — revisar `Mobilizados` para reforçar o contrato de valor financeiro e tipos válidos.** Racional: a mudança assume que valores monetários devem obedecer a regras mais rígidas do que campos quantitativos comuns.
- [ ] **Trecho: `src/ieb/models.py:881-915` — revisar `PequenoProjeto` e `Fundo` quanto à coerência entre quantidade, classificação e valor total.** Racional: a premissa é que o banco deveria impedir estados absurdos, como quantidade zero com valor alto sem contexto claro, caso isso seja de fato inválido para o negócio.
- [ ] **Trecho: `src/ieb/models.py:868-877` — decidir se `Rede` representa ocorrências independentes ou um catálogo consolidado por atividade/indicador.** Racional: a mudança depende de consenso funcional, porque a necessidade de unicidade aqui é semântica, não apenas técnica.
- [ ] **Trecho: `src/ieb/models.py:919-930` — redefinir o contrato mínimo de `Outro` para evitar que ele vire depósito genérico de dado analiticamente inútil.** Racional: a mudança assume que flexibilidade demais está prejudicando qualidade do dado.
- [ ] **Trecho: `src/ieb/models.py:1180-1209` — alinhar `AtividadeRegistroModelo` com a mesma estratégia de indicadores adotada no restante do arquivo.** Racional: o model hoje parece exceção à regra geral, e o time precisa decidir se isso é proposital ou lacuna de modelagem.

### P2 — Qualidade arquitetural, precisão e manutenção

- [ ] **Trecho: `src/ieb/models.py:44-77` — revisar uso de `CharField` e validações em dados sensíveis de `Indigena` e entidades correlatas.** Racional: a mudança assume que CPF/RG merecem tratamento mais explícito, mas isso pode depender de política de privacidade e uso real desses campos.
- [ ] **Trecho: `src/ieb/models.py:629-662` — revisar precisão e semântica do campo `area` em `UC`, `PA`, `TUC` e `TIs`.** Racional: a premissa é que área é dado consolidável e pode exigir mais precisão do que `FloatField` oferece em relatórios institucionais.
- [ ] **Arquivo: `src/ieb/models.py` — revisar uso de `FloatField` versus `DecimalField` em áreas, metas e agregados relevantes.** Racional: a mudança assume que previsibilidade numérica importa para consolidação, mas o time precisa ponderar custo de migração versus benefício prático.
- [ ] **Arquivo: `src/ieb/models.py` — revisar uso extensivo de `related_name='+'` onde isso prejudica manutenção e leitura.** Racional: a suposição é que esconder todos os reversos simplificou o início do projeto, mas hoje talvez esteja atrapalhando evolução e debugging.
- [ ] **Trecho: `src/ieb/models.py:593-623` — desacoplar gradualmente processamento de anexos e thumbnails da lógica direta de model.** Racional: a mudança assume que operações de arquivo têm custo operacional e deveriam ficar mais previsíveis e testáveis.
- [ ] **Trecho: `src/ieb/models.py:1212-1300` — separar conceitualmente os models finais de formação e política pública indígena do núcleo transacional de monitoramento.** Racional: a premissa é que o arquivo ficou monolítico demais e já contém mais de um subdomínio distinto.
- [ ] **Arquivo: `src/ieb/models.py` — preparar modularização futura do arquivo por subdomínio sem mudar o banco de imediato.** Racional: a mudança assume que clareza estrutural do código facilitará revisão do esquema, mesmo antes de alterar tabelas.
- [ ] **Trecho: `src/ieb/models.py:317-342` — documentar internamente o papel das choices globais de indicador e score de plano como contrato transversal do domínio.** Racional: a premissa é que esses enums já funcionam como linguagem ubíqua do sistema e precisam ficar estáveis e explícitos para futuras refatorações.
- [ ] **Trecho: `src/ieb/models.py:128-166` — revisar `Programa` e `Projeto` para explicitar se nomes e siglas possuem função de identificação operacional ou apenas descritiva.** Racional: isso ajuda a decidir depois quais campos merecem indexação, unicidade ou validação mais forte.
- [ ] **Trecho: `src/ieb/models.py:241-312` — revisar as tabelas de ligação temáticas para padronizar semântica, nomes e expectativas de unicidade.** Racional: a mudança assume que há valor em tornar o desenho mais previsível para novos desenvolvedores, mesmo sem impacto imediato no banco.

## Verification Criteria

- [ ] O backlog foi reorganizado em P0, P1 e P2 com justificativa de prioridade explícita.
- [ ] Cada tarefa relevante explicita a suposição funcional ou estrutural que está motivando a mudança.
- [ ] O plano permite que outros desenvolvedores debatam premissas antes de qualquer implementação de constraint ou refatoração.
- [ ] Os itens P0 atacam primeiro integridade do banco e confiabilidade analítica.
- [ ] Os itens P1 fortalecem governança, chaves de negócio e coerência de domínio.
- [ ] Os itens P2 ficam reservados para melhoria arquitetural e evolução de longo prazo.

## Potential Risks and Mitigations

1. **Assumir regras de negócio erradas ao transformar hipóteses em constraints**  
   Mitigation: validar cada hipótese destacada no racional com stakeholders e desenvolvedores antes de materializar migrations.

2. **Priorizar redução de duplicação antes de resolver integridade**  
   Mitigation: manter a ordem P0 → P1 → P2, começando por segurança estrutural do esquema atual.

3. **Endurecer o banco com dados legados inconsistentes**  
   Mitigation: prever diagnóstico e saneamento antes de impor novas constraints condicionais ou checks.

4. **Gerar discussão ampla demais sem convergência prática**  
   Mitigation: usar este plano como instrumento de revisão técnica item a item, e não como proposta monolítica de refatoração total.

## Alternative Approaches

1. **Endurecer primeiro e manter a duplicação estrutural**: mais conservador, reduz risco imediato, mas preserva dívida conceitual.
2. **Consolidar cedo `Indicador`/`IndicadorFinanciador` e `Meta`/`MetaFinanciador`**: reduz complexidade futura, mas aumenta risco de migração antes de validar premissas.
3. **Separar primeiro o arquivo por subdomínio e postergar mudanças de banco**: melhora legibilidade e debate técnico, porém adia correções de integridade que hoje são mais urgentes.
