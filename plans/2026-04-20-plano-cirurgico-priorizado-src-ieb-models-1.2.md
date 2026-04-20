# Plano Cirúrgico Priorizado — `src/ieb/models.py` (Versão consolidada para revisão técnica)

## Objective

Consolidar, em um único plano de referência, a análise estrutural de `src/ieb/models.py` com foco em discussão técnica entre desenvolvedores, reduzindo redundância na pasta `plans` e organizando as decisões por prioridade, hipótese assumida, risco atual e impacto esperado.

## Nota de Organização

Este documento deve ser tratado como a **referência principal consolidada** para a revisão de `src/ieb/models.py`, substituindo operacionalmente os planos anteriores sobre o mesmo tema:

- `plans/2026-04-20-plano-cirurgico-src-ieb-models-1.0.md`
- `plans/2026-04-20-plano-cirurgico-priorizado-src-ieb-models-1.1.md`

Premissa de organização: evitar abrir novos planos paralelos sobre o mesmo assunto quando a intenção for apenas refinar prioridade, contexto ou formato de discussão. A preferência futura deve ser por **evoluir a mesma linha de plano por versão**, em vez de multiplicar arquivos semelhantes.

## Contexto e Fontes

- Arquivo principal analisado: `src/ieb/models.py:1-1300`
- Núcleo hierárquico do domínio: `src/ieb/models.py:128-312`
- Estrutura de indicadores e metas: `src/ieb/models.py:344-567`
- Registro operacional central: `src/ieb/models.py:570-623`
- Modelos satélite com dupla referência de indicador: `src/ieb/models.py:666-1178`
- Modelos de histórico: `src/ieb/models.py:810-818`, `src/ieb/models.py:999-1007`
- Modelos complementares finais: `src/ieb/models.py:1180-1300`

## Assumptions

- `AtividadeRegistro` deve continuar sendo o centro do fato operacional do domínio.
- O maior risco atual do esquema não está na hierarquia base de projetos, mas na integridade e semântica dos modelos ligados a indicadores.
- Antes de consolidar models duplicados, é mais seguro endurecer a integridade do desenho atual.
- Novas constraints devem ser precedidas por diagnóstico de dados existentes.
- A eventual unificação de `Indicador`/`IndicadorFinanciador` e `Meta`/`MetaFinanciador` continua sendo hipótese de melhoria, não decisão fechada.

## Como usar este plano em revisão técnica

Cada item abaixo foi organizado para facilitar opinião de outros desenvolvedores. O objetivo não é assumir consenso automático, e sim explicitar:

- qual trecho está sendo questionado
- qual hipótese está sendo assumida
- qual risco existe hoje
- qual seria o ganho se a mudança for aceita
- se há dependência de saneamento prévio

## Implementation Plan

### P0 — Integridade estrutural e confiabilidade analítica

- [ ] **Item P0.1 — Formalizar o contrato entre `Indicador` e `IndicadorFinanciador`**  
  **Arquivo/Trecho:** `src/ieb/models.py:344-442`  
  **Assunção:** hoje existem dois universos de indicador porque há diferença conceitual real entre indicador institucional e indicador específico de financiador.  
  **Risco atual:** a separação existe no código, mas não está suficientemente formalizada como contrato de domínio; isso contamina metas, tabelas satélite e regras de unicidade.  
  **Impacto da mudança:** cria base conceitual para decidir se o caminho correto é manter dualidade com constraints fortes ou unificar modelos no futuro.  
  **Dependência de saneamento:** não. É uma tarefa de alinhamento conceitual e modelagem.

- [ ] **Item P0.2 — Definir exclusividade entre `indicador` e `indicador_financiador` nos modelos satélite**  
  **Arquivo/Trecho:** `src/ieb/models.py:666-1178`  
  **Assunção:** cada registro satélite deve pertencer a exatamente um contexto analítico: institucional ou financiador.  
  **Risco atual:** o banco pode aceitar estados ambíguos, com os dois campos preenchidos ou sem nenhum preenchido, dependendo do fluxo.  
  **Impacto da mudança:** elimina ambiguidade estrutural nas tabelas mais críticas do domínio.  
  **Dependência de saneamento:** sim, antes de impor constraint é preciso verificar dados já existentes.

- [ ] **Item P0.3 — Substituir `unique_together` atuais por `UniqueConstraint` condicionais**  
  **Arquivo/Trecho:** `src/ieb/models.py:666-1178`  
  **Assunção:** a unicidade correta muda conforme o tipo de vínculo do registro.  
  **Risco atual:** a maioria dos models protege apenas `(atividade_registro, indicador)`, mesmo quando a linha pode depender de `indicador_financiador`; isso fragiliza a integridade relacional.  
  **Impacto da mudança:** faz a unicidade refletir o desenho real do domínio.  
  **Dependência de saneamento:** sim, especialmente para duplicidades já gravadas.

- [ ] **Item P0.4 — Revisar `Area` como caso-base de fragilidade estrutural**  
  **Arquivo/Trecho:** `src/ieb/models.py:666-695`  
  **Assunção:** `Area` deve representar um único recorte analítico por registro, sem ambiguidade de indicador.  
  **Risco atual:** mistura dupla referência opcional e total persistido calculado a partir de M2M, combinação propensa a inconsistência.  
  **Impacto da mudança:** esse model pode virar referência para corrigir o mesmo padrão no restante das tabelas satélite.  
  **Dependência de saneamento:** provável, se houver duplicidades ou linhas mal vinculadas.

- [ ] **Item P0.5 — Revisar `AreasProtegidas` com a mesma estratégia de integridade de `Area`**  
  **Arquivo/Trecho:** `src/ieb/models.py:699-734`  
  **Assunção:** o mesmo contrato lógico de exclusividade e unicidade deve valer aqui.  
  **Risco atual:** o model replica a fragilidade de `Area` e ainda adiciona vários agregados persistidos.  
  **Impacto da mudança:** reduz divergência entre modelos quase paralelos.  
  **Dependência de saneamento:** sim, se os totais persistidos já estiverem inconsistentes.

- [ ] **Item P0.6 — Revisar `Pessoas` para coerência entre vínculo analítico e desagregações**  
  **Arquivo/Trecho:** `src/ieb/models.py:743-761`  
  **Assunção:** os subtotais devem respeitar algum contrato mínimo em relação ao total de pessoas.  
  **Risco atual:** o banco aceita combinações incoerentes entre total e desagregações, além da ambiguidade entre indicador comum e financiador.  
  **Impacto da mudança:** aumenta confiabilidade analítica dos dados mais sensíveis do monitoramento.  
  **Dependência de saneamento:** sim, se já existirem registros incoerentes.

- [ ] **Item P0.7 — Revisar `Organizacoes` para definir se subtotais são exaustivos ou apenas informativos**  
  **Arquivo/Trecho:** `src/ieb/models.py:821-835`  
  **Assunção:** a equipe precisa decidir se `org_sociedade_civil`, `org_indigenas` e `org_extrativistas` precisam ou não fechar com `total_organizacoes`.  
  **Risco atual:** hoje não existe contrato claro, então qualquer validação futura pode estar errada se a premissa funcional for equivocada.  
  **Impacto da mudança:** permite decidir conscientemente entre constraint forte ou flexibilidade controlada.  
  **Dependência de saneamento:** depende da regra que for escolhida.

- [ ] **Item P0.8 — Estabilizar a semântica de `Evento.total`**  
  **Arquivo/Trecho:** `src/ieb/models.py:838-857`  
  **Assunção:** é necessário decidir se campo vazio significa zero ou “não informado”.  
  **Risco atual:** o cálculo atual soma valores truthy, o que embute uma semântica implícita e potencialmente incorreta.  
  **Impacto da mudança:** melhora confiabilidade do total e padroniza interpretação dos campos do model.  
  **Dependência de saneamento:** possível, se houver diferença entre nulo e zero nos dados legados.

- [ ] **Item P0.9 — Redesenhar a estratégia de agregados persistidos dependentes de M2M**  
  **Arquivo/Trecho:** `src/ieb/models.py:764-805`, `src/ieb/models.py:1010-1053`, `src/ieb/models.py:1091-1137`, `src/ieb/models.py:1143-1175`  
  **Assunção:** totais persistidos devem refletir mudanças em relações M2M mesmo fora do fluxo original de criação.  
  **Risco atual:** `Leis`, `Parcerias`, `Produtos` e `Contratos` podem armazenar totais desatualizados porque `save()` do model principal não cobre todas as mudanças da relação.  
  **Impacto da mudança:** elimina fonte recorrente de divergência entre dado base e dado consolidado.  
  **Dependência de saneamento:** sim, para recalcular estados atuais se necessário.

- [ ] **Item P0.10 — Corrigir semântica de `Contratos.valor_total`**  
  **Arquivo/Trecho:** `src/ieb/models.py:1143-1175`  
  **Assunção:** o sistema deve diferenciar claramente “sem valor informado” de “total calculado zero”.  
  **Risco atual:** `NULL` pode significar tanto ausência de cálculo quanto ausência de valor contratual, o que prejudica análise financeira.  
  **Impacto da mudança:** melhora interpretação do dado consolidado e reduz ambiguidade contábil.  
  **Dependência de saneamento:** sim, se for preciso remapear valores existentes.

- [ ] **Item P0.11 — Impor integridade temporal mínima em `AtividadeRegistro`**  
  **Arquivo/Trecho:** `src/ieb/models.py:570-590`  
  **Assunção:** `data_final` não pode ser anterior a `data_inicio`.  
  **Risco atual:** o banco pode aceitar registros operacionalmente inválidos.  
  **Impacto da mudança:** impede erro básico de domínio direto na camada de persistência.  
  **Dependência de saneamento:** sim, se houver registros com datas invertidas.

- [ ] **Item P0.12 — Impor integridade temporal mínima em `Meta` e `MetaFinanciador`**  
  **Arquivo/Trecho:** `src/ieb/models.py:445-567`  
  **Assunção:** a janela de apuração precisa ser coerente quando `data_inicio` existe.  
  **Risco atual:** metas podem ser gravadas com período inválido, distorcendo apuração.  
  **Impacto da mudança:** fortalece consistência das métricas monitoradas.  
  **Dependência de saneamento:** sim, conforme estado atual da base.

- [ ] **Item P0.13 — Introduzir `CheckConstraint` transversais para o núcleo semântico do arquivo**  
  **Arquivo/Trecho:** `src/ieb/models.py`  
  **Assunção:** regras mínimas de integridade não devem depender apenas das views/forms.  
  **Risco atual:** a aplicação carrega sozinha a responsabilidade por proteger coerência de dados.  
  **Impacto da mudança:** eleva robustez do banco independentemente do ponto de entrada dos dados.  
  **Dependência de saneamento:** sim, em quase todos os casos.

### P1 — Coerência de domínio, auditoria e chaves de negócio

- [ ] **Item P1.1 — Documentar por que `Meta` e `MetaFinanciador` existem separados**  
  **Arquivo/Trecho:** `src/ieb/models.py:445-567`  
  **Assunção:** só faz sentido manter duplicação se houver diferença conceitual real, e não apenas herança histórica de implementação.  
  **Risco atual:** o time pode discutir unificação sem clareza sobre o motivo original da duplicação.  
  **Impacto da mudança:** melhora qualidade da decisão futura sobre consolidação ou manutenção da separação.  
  **Dependência de saneamento:** não.

- [ ] **Item P1.2 — Corrigir auditoria de `LeiHistorico` para usuário real do sistema**  
  **Arquivo/Trecho:** `src/ieb/models.py:810-818`  
  **Assunção:** histórico deve apontar para identidade persistente e não para texto livre.  
  **Risco atual:** auditoria fraca, sem integridade referencial e com baixa rastreabilidade.  
  **Impacto da mudança:** melhora governança e capacidade de auditoria.  
  **Dependência de saneamento:** provável mapeamento parcial de históricos existentes.

- [ ] **Item P1.3 — Corrigir auditoria de `PlanoHistorico` para usuário real do sistema**  
  **Arquivo/Trecho:** `src/ieb/models.py:999-1007`  
  **Assunção:** o mesmo padrão de governança deve valer para todos os históricos relevantes.  
  **Risco atual:** divergência de padrão e baixa confiabilidade de rastreio.  
  **Impacto da mudança:** padroniza auditoria do módulo.  
  **Dependência de saneamento:** sim, semelhante ao item anterior.

- [ ] **Item P1.4 — Separar em `Planos` o que é catálogo, transição de estado e histórico**  
  **Arquivo/Trecho:** `src/ieb/models.py:934-992`  
  **Assunção:** atualizar estado corrente e registrar histórico não deveriam ficar misturados na mesma rotina de persistência.  
  **Risco atual:** responsabilidades sobrepostas dificultam previsibilidade e evolução do model.  
  **Impacto da mudança:** melhora clareza do domínio e reduz efeitos colaterais implícitos.  
  **Dependência de saneamento:** não necessariamente, mas depende da estratégia escolhida.

- [ ] **Item P1.5 — Adicionar unicidade lógica em `OIRegLoc`**  
  **Arquivo/Trecho:** `src/ieb/models.py:12-41`  
  **Assunção:** o mesmo vínculo regional-local não deveria existir repetido sem metadado adicional.  
  **Risco atual:** duplicação silenciosa de relacionamento.  
  **Impacto da mudança:** melhora integridade relacional dos cadastros base.  
  **Dependência de saneamento:** sim, se houver pares duplicados.

- [ ] **Item P1.6 — Adicionar unicidade lógica em `TIsIGATI`**  
  **Arquivo/Trecho:** `src/ieb/models.py:82-95`  
  **Assunção:** mesma lógica de vínculo único entre entidades.  
  **Risco atual:** repetição silenciosa do mesmo par.  
  **Impacto da mudança:** fortalece coerência dos catálogos temáticos.  
  **Dependência de saneamento:** sim.

- [ ] **Item P1.7 — Adicionar unicidade em `EquipeProjeto`, `ProjetoOI` e `ProjetoTI`**  
  **Arquivo/Trecho:** `src/ieb/models.py:189-210`  
  **Assunção:** esses relacionamentos representam pares únicos e não eventos repetíveis.  
  **Risco atual:** duplicação de vínculo compromete consultas, filtros e relatórios.  
  **Impacto da mudança:** melhora previsibilidade dos relacionamentos centrais do domínio.  
  **Dependência de saneamento:** sim.

- [ ] **Item P1.8 — Definir unicidade contextual de `Componente.codigo` e `Atividade.codigo`**  
  **Arquivo/Trecho:** `src/ieb/models.py:169-186`  
  **Assunção:** esses códigos funcionam como identificadores operacionais dentro do seu escopo, e não apenas como texto livre.  
  **Risco atual:** colisões de código podem gerar ambiguidade operacional.  
  **Impacto da mudança:** fortalece legibilidade do domínio e futuras integrações.  
  **Dependência de saneamento:** sim, se já houver colisões.

- [ ] **Item P1.9 — Definir unicidade contextual de `Subatividade.codigo`**  
  **Arquivo/Trecho:** `src/ieb/models.py:253-260`  
  **Assunção:** a mesma lógica de código hierárquico deve continuar descendo na estrutura.  
  **Risco atual:** ausência de padrão uniforme nos códigos do domínio.  
  **Impacto da mudança:** torna a hierarquia mais previsível.  
  **Dependência de saneamento:** sim.

- [ ] **Item P1.10 — Decidir quais identificadores institucionais são realmente chaves de negócio**  
  **Arquivo/Trecho:** `src/ieb/models.py:101-124`, `src/ieb/models.py:12-77`  
  **Assunção:** nem todo CPF/CNPJ/sigla precisa ser único no banco; isso depende do papel real do campo.  
  **Risco atual:** impor unicidade errada pode travar o uso legítimo do sistema, mas não impor nada também reduz confiabilidade do cadastro.  
  **Impacto da mudança:** cria base correta para futuras validações e índices.  
  **Dependência de saneamento:** depende da decisão funcional.

- [ ] **Item P1.11 — Revisar `Mobilizados` como dado financeiro com regras mais rígidas**  
  **Arquivo/Trecho:** `src/ieb/models.py:1060-1088`  
  **Assunção:** dado financeiro deve ter contrato mais forte de validade do que campos quantitativos genéricos.  
  **Risco atual:** baixa proteção semântica para valores financeiros.  
  **Impacto da mudança:** melhora qualidade contábil e analítica dos registros.  
  **Dependência de saneamento:** possível.

- [ ] **Item P1.12 — Revisar coerência semântica de `PequenoProjeto` e `Fundo`**  
  **Arquivo/Trecho:** `src/ieb/models.py:881-915`  
  **Assunção:** quantidade, classificação e valor total deveriam obedecer a um contrato minimamente coerente.  
  **Risco atual:** o banco aceita combinações estranhas sem alertar o sistema.  
  **Impacto da mudança:** melhora a confiabilidade desses objetos em relatórios e consolidação.  
  **Dependência de saneamento:** sim, se houver dados atípicos já gravados.

- [ ] **Item P1.13 — Decidir se `Rede` é ocorrência livre ou consolidado lógico por atividade/indicador**  
  **Arquivo/Trecho:** `src/ieb/models.py:868-877`  
  **Assunção:** a necessidade ou não de unicidade depende da semântica funcional do model.  
  **Risco atual:** sem essa definição, qualquer constraint pode ficar errada.  
  **Impacto da mudança:** evita correção técnica baseada em interpretação equivocada do negócio.  
  **Dependência de saneamento:** depende da decisão final.

- [ ] **Item P1.14 — Redefinir contrato mínimo de `Outro`**  
  **Arquivo/Trecho:** `src/ieb/models.py:919-930`  
  **Assunção:** o model está flexível demais e pode estar capturando informação de baixa utilidade analítica.  
  **Risco atual:** virar “caixa de resto” do domínio.  
  **Impacto da mudança:** melhora qualidade e interpretabilidade dos dados excepcionais.  
  **Dependência de saneamento:** possível, se a base já estiver muito heterogênea.

- [ ] **Item P1.15 — Alinhar `AtividadeRegistroModelo` à estratégia geral de indicadores**  
  **Arquivo/Trecho:** `src/ieb/models.py:1180-1209`  
  **Assunção:** o model hoje parece exceção não documentada ao padrão das demais tabelas satélite.  
  **Risco atual:** inconsistência de desenho interno do próprio arquivo.  
  **Impacto da mudança:** melhora simetria e previsibilidade do domínio.  
  **Dependência de saneamento:** depende da solução escolhida.

### P2 — Qualidade arquitetural, precisão e manutenção

- [ ] **Item P2.1 — Revisar tratamento de dados sensíveis como CPF e RG**  
  **Arquivo/Trecho:** `src/ieb/models.py:44-77`  
  **Assunção:** esses campos podem exigir validação, normalização ou política específica de retenção.  
  **Risco atual:** baixa padronização e possível acúmulo de ruído cadastral.  
  **Impacto da mudança:** melhora qualidade do cadastro e prepara futuras decisões de governança.  
  **Dependência de saneamento:** sim, se houver formatos variados.

- [ ] **Item P2.2 — Revisar precisão do campo `area` em `TIs`, `UC`, `PA` e `TUC`**  
  **Arquivo/Trecho:** `src/ieb/models.py:44-54`, `src/ieb/models.py:629-662`  
  **Assunção:** áreas são valores consolidáveis e podem exigir maior previsibilidade numérica.  
  **Risco atual:** `FloatField` pode gerar comportamento pouco previsível em somatórios institucionais.  
  **Impacto da mudança:** melhora precisão analítica de métricas territoriais.  
  **Dependência de saneamento:** migração de tipo e validação de escala/precisão.

- [ ] **Item P2.3 — Revisar `FloatField` versus `DecimalField` em metas, áreas e agregados**  
  **Arquivo/Trecho:** `src/ieb/models.py`  
  **Assunção:** previsibilidade numérica é mais valiosa que simplicidade de tipo em parte do domínio.  
  **Risco atual:** arredondamentos ou somatórios inconsistentes em relatórios.  
  **Impacto da mudança:** melhora robustez matemática do esquema.  
  **Dependência de saneamento:** sim, e com avaliação de impacto em migrations.

- [ ] **Item P2.4 — Revisar uso extensivo de `related_name='+'`**  
  **Arquivo/Trecho:** `src/ieb/models.py`  
  **Assunção:** esconder reversos simplificou o desenho inicial, mas hoje pode dificultar manutenção.  
  **Risco atual:** baixa legibilidade para desenvolvimento, admin e debugging.  
  **Impacto da mudança:** melhora introspecção e clareza do domínio.  
  **Dependência de saneamento:** não, mas exige cuidado para evitar colisões de nomes reversos.

- [ ] **Item P2.5 — Desacoplar processamento de anexos da lógica direta dos models**  
  **Arquivo/Trecho:** `src/ieb/models.py:593-623`  
  **Assunção:** manipulação de arquivos e thumbnails não deveria depender apenas de `save()` síncrono do model.  
  **Risco atual:** comportamento pesado, menos previsível e mais difícil de testar.  
  **Impacto da mudança:** melhora manutenção e robustez operacional.  
  **Dependência de saneamento:** não necessariamente.

- [ ] **Item P2.6 — Separar logicamente o bloco de formação e política pública indígena do núcleo transacional**  
  **Arquivo/Trecho:** `src/ieb/models.py:1212-1300`  
  **Assunção:** o arquivo hoje abriga mais de um subdomínio distinto.  
  **Risco atual:** aumento do custo cognitivo e dificuldade de revisão.  
  **Impacto da mudança:** melhora legibilidade e prepara futura modularização.  
  **Dependência de saneamento:** não.

- [ ] **Item P2.7 — Preparar modularização futura do arquivo por subdomínio**  
  **Arquivo/Trecho:** `src/ieb/models.py:1-1300`  
  **Assunção:** melhorar organização do código facilitará discutir o banco com menos ruído estrutural.  
  **Risco atual:** monolito de models dificulta enxergar padrões e exceções.  
  **Impacto da mudança:** melhora manutenção e revisão evolutiva.  
  **Dependência de saneamento:** não.

- [ ] **Item P2.8 — Explicitar o papel das choices globais de indicador e score de plano como contrato transversal**  
  **Arquivo/Trecho:** `src/ieb/models.py:317-342`  
  **Assunção:** essas enums já funcionam como linguagem ubíqua do sistema.  
  **Risco atual:** mudanças futuras podem quebrar semântica sem perceber o alcance transversal desse bloco.  
  **Impacto da mudança:** melhora previsibilidade de futuras refatorações.  
  **Dependência de saneamento:** não.

- [ ] **Item P2.9 — Revisar papel operacional de nomes e siglas em `Programa` e `Projeto`**  
  **Arquivo/Trecho:** `src/ieb/models.py:128-166`  
  **Assunção:** decidir se são identificadores operacionais ou apenas descrição ajuda a calibrar validações futuras.  
  **Risco atual:** incerteza sobre quais campos merecem tratamento de chave de negócio.  
  **Impacto da mudança:** apoia decisões mais consistentes sobre índices, unicidade e integrações.  
  **Dependência de saneamento:** depende da decisão funcional.

- [ ] **Item P2.10 — Padronizar semântica das tabelas de ligação temáticas**  
  **Arquivo/Trecho:** `src/ieb/models.py:241-312`  
  **Assunção:** nomes, padrões de unicidade e expectativas de uso ainda podem ficar mais previsíveis para novos desenvolvedores.  
  **Risco atual:** aprendizado e manutenção mais lentos por falta de uniformidade.  
  **Impacto da mudança:** melhora consistência interna do desenho.  
  **Dependência de saneamento:** não necessariamente.

## Verification Criteria

- [ ] Existe apenas um plano consolidado como referência principal para revisão de `src/ieb/models.py`.
- [ ] O backlog está organizado por P0, P1 e P2 sem multiplicar documentos paralelos sobre o mesmo assunto.
- [ ] Cada item explicita hipótese assumida, risco atual, impacto esperado e eventual necessidade de saneamento.
- [ ] O documento pode ser usado diretamente em reunião técnica para debate item a item.
- [ ] As prioridades deixam claro o que é integridade do banco, o que é coerência de domínio e o que é melhoria arquitetural.

## Potential Risks and Mitigations

1. **Acumular versões parecidas demais na pasta `plans`**  
   Mitigation: usar este documento como referência consolidada e evoluir a mesma linha de plano por versão futura, evitando novos arquivos concorrentes sobre o mesmo tópico.

2. **Confundir hipótese com decisão já aprovada**  
   Mitigation: manter explícitas as assunções em cada item e validar em revisão técnica antes de qualquer migration.

3. **Querer resolver P1/P2 antes de estabilizar P0**  
   Mitigation: preservar a ordem proposta e tratar integridade estrutural como pré-condição para refatorações mais elegantes.

4. **Impor constraints sem conhecer o estado dos dados legados**  
   Mitigation: tratar saneamento e diagnóstico como etapa obrigatória antes de endurecer o esquema.

## Alternative Approaches

1. **Manter múltiplos planos temáticos menores**: facilita foco local, mas aumenta redundância e dispersa o contexto.
2. **Usar um único plano consolidado versionado**: melhora organização da pasta e preserva histórico sem espalhar arquivos semelhantes.
3. **Quebrar a consolidação apenas quando surgir um novo tema realmente distinto**: reduz redundância e mantém a pasta `plans` mais legível.
