# Plano Modular de Evolução Arquitetural — IEB no Ambiente GeoNode

## Objective

Documentar, de forma modular e orientada por arquivo, os próximos passos para reduzir pontos cegos arquiteturais do app `ieb`, melhorar a aderência operacional ao ambiente GeoNode e preparar um desacoplamento progressivo quando isso fizer sentido.

## Contexto e Fontes

- Base do projeto GeoNode carregada via `geonode.settings`: `src/terralab_v2/settings.py:40-45`
- Inclusão do app local `ieb` no projeto: `src/terralab_v2/settings.py:72-74`
- Domínio principal do app concentrado em um único arquivo: `src/ieb/models.py:1-1300`
- Modelos centrais de monitoramento e registros: `src/ieb/models.py:145-236`, `src/ieb/models.py:445-590`
- Auditoria textual sem vínculo ao usuário Django/GeoNode: `src/ieb/models.py:810-818`, `src/ieb/models.py:999-1007`
- Base polimórfica do GeoNode em `ResourceBase`: `/tmp/forge_fetch_ASaygE.txt:630-855`
- Recursos principais do GeoNode herdando de `ResourceBase`: `/tmp/forge_fetch_ASaygE.txt:1480-1488`, `/tmp/forge_fetch_ASaygE.txt:1773-1787`, `/tmp/forge_fetch_ASaygE.txt:1891-1905`

## Assumptions

- O objetivo futuro é manter o `ieb` funcional dentro do projeto atual, mas com fronteiras arquiteturais mais claras.
- Nem todo model do `ieb` deve virar `ResourceBase`; a recomendação preferencial é integração pontual por associação, não por herança massiva.
- As tarefas abaixo devem ser tratadas incrementalmente, com pequenas mudanças por arquivo.

## Implementation Plan

- [ ] **Arquivo: `src/ieb/models.py` — separar o arquivo por subdomínio conceitual antes de qualquer refatoração profunda.** Racional: `src/ieb/models.py:1-1300` concentra cadastros territoriais, gestão de projetos, monitoramento, auditoria e anexos no mesmo módulo, o que dificulta manutenção e futura extração.
- [ ] **Arquivo: `src/ieb/models.py` — introduzir uma camada explícita de integração opcional com recursos GeoNode, sem converter o domínio inteiro para `ResourceBase`.** Racional: hoje não há relação estrutural com `ResourceBase`, `Dataset`, `Map` ou `Document`, apesar de o projeto rodar sobre GeoNode; a integração deve ser seletiva e não invasiva.
- [ ] **Arquivo: `src/ieb/models.py` — revisar os históricos `LeiHistorico` e `PlanoHistorico` para substituir `usuario` textual por vínculo real com o usuário Django/GeoNode.** Racional: os campos em `src/ieb/models.py:815` e `src/ieb/models.py:1004` enfraquecem auditoria, rastreabilidade e governança.
- [ ] **Arquivo: `src/ieb/models.py` — revisar constraints com `unique_together` em modelos que aceitam `indicador` nulo e `indicador_financiador` alternativo.** Racional: padrões como os de `Area`, `Pessoas`, `Organizacoes`, `Leis`, `Outro`, `Parcerias`, `Produtos` e `Contratos` podem produzir inconsistência lógica quando o registro pertence a financiador e o campo `indicador` fica `NULL`.
- [ ] **Arquivo: `src/ieb/models.py` — padronizar agregações calculadas (`save`, `total_*`, `valor_total`, `realizado`) para evitar duplicidade de lógica e divergência entre indicadores normais e de financiador.** Racional: há paralelismo forte entre `Indicador`/`IndicadorFinanciador` e `Meta`/`MetaFinanciador` em `src/ieb/models.py:344-567`, o que sugere dívida estrutural.
- [ ] **Arquivo: `src/ieb/models.py` — revisar o papel dos modelos geográficos cadastrais (`TIs`, `UC`, `PA`, `TUC`) e decidir explicitamente se são apenas catálogos internos ou se precisam se vincular a recursos geoespaciais do GeoNode.** Racional: atualmente são entidades cadastrais com área numérica simples em `src/ieb/models.py:44-54` e `src/ieb/models.py:629-662`, sem integração espacial nativa.
- [ ] **Arquivo: `src/ieb/models.py` — revisar os modelos de anexo (`AtividadeRegistroFoto`, `AtividadeRegistroListaPresenca`) para definir quando anexos permanecem operacionais do app e quando devem ser tratados como documentos catalogáveis.** Racional: o uso atual de `ImageField`/`FileField` próprios em `src/ieb/models.py:593-623` contorna a camada de assets/documentos do GeoNode.
- [ ] **Arquivo: `src/ieb/views.py` — consolidar regras de autenticação, autorização e escopo de acesso do módulo `ieb` no nível das views.** Racional: como os modelos do `ieb` não herdam o sistema de governança de `ResourceBase`, as views precisam carregar explicitamente a responsabilidade por segurança.
- [ ] **Arquivo: `src/ieb/views.py` — criar uma fronteira clara entre operações de cadastro, monitoramento, integrações auxiliares e endpoints AJAX.** Racional: isso reduz acoplamento entre fluxo de interface, regra de negócio e persistência, facilitando manutenção modular.
- [ ] **Arquivo: `src/ieb/forms.py` — reforçar validações server-side coerentes com a hierarquia `Projeto → Componente → Atividade → Subatividade → EquipeProjeto`.** Racional: o domínio transacional precisa garantir consistência própria, já que não usa a semântica de recurso do GeoNode.
- [ ] **Arquivo: `src/ieb/forms.py` — centralizar validações específicas de indicadores e financiadores em componentes reutilizáveis.** Racional: isso reduz a dispersão de regras entre formulário, view e model.
- [ ] **Arquivo: `src/ieb/admin.py` — reorganizar a administração por blocos de subdomínio e destacar entidades que exigem governança mais forte.** Racional: o admin pode funcionar como ponto de estabilização operacional enquanto a arquitetura é modularizada.
- [ ] **Arquivo: `src/ieb/urls.py` — separar rotas por área funcional e identificar endpoints sensíveis.** Racional: a clareza do roteamento ajuda a endurecer segurança e facilita desacoplamento futuro.
- [ ] **Arquivo: `src/terralab_v2/settings.py` — explicitar, em configuração, a posição do `ieb` como app transacional hospedado pelo projeto GeoNode.** Racional: hoje o acoplamento aparece implicitamente em `src/terralab_v2/settings.py:40-45` e `src/terralab_v2/settings.py:72-74`; registrar a intenção arquitetural reduz ambiguidade futura.
- [ ] **Arquivo: `src/terralab_v2/settings.py` — prever pontos de configuração para futura extração parcial do `ieb` sem depender de refatoração brusca.** Racional: preparar flags, namespaces e integrações opcionais reduz custo de desacoplamento progressivo.
- [ ] **Arquivo: `src/terralab_v2/urls.py` — manter explícita a separação entre o roteamento herdado do GeoNode e as rotas do app `ieb`.** Racional: isso ajuda a preservar fronteiras entre portal geoespacial e sistema de monitoramento institucional.
- [ ] **Arquivo: `src/ieb/tests.py` — iniciar cobertura mínima por domínio, começando por permissões, agregações e consistência entre indicadores e metas.** Racional: o desacoplamento seguro depende de testes mínimos sobre o comportamento atual.
- [ ] **Arquivo: `src/ieb/templates/atividade_registro_form_v2.html` — mapear dependências de UI que assumem estrutura específica do backend e separar responsabilidades de apresentação e regra.** Racional: a tela principal de registro concentra alto acoplamento funcional.
- [ ] **Arquivo: `src/ieb/static/ieb/js/script_v2.js` — revisar dependências de frontend que reproduzem regras de negócio já existentes no backend.** Racional: o front não deve carregar sozinho decisões estruturais do domínio.
- [ ] **Arquivo: `src/ieb/templates/monitoramento_metas.html` — alinhar a tela de monitoramento com a futura estratégia de consulta otimizada e governança por escopo.** Racional: telas de consolidação costumam sofrer primeiro com inconsistência entre arquitetura e performance.
- [ ] **Arquivo: `src/ieb/templates/monitoramento_registros.html` — preparar a listagem para evoluir com filtros, paginação e políticas de visibilidade mais explícitas.** Racional: listagens amplas tendem a expor rapidamente limites de segurança e escalabilidade.

## Verification Criteria

- [ ] Existe um backlog modular com uma tarefa específica por arquivo prioritário do domínio `ieb`.
- [ ] O plano distingue claramente o que deve permanecer como domínio transacional próprio e o que pode integrar com recursos GeoNode.
- [ ] As tarefas priorizam segurança, governança, modularização e desacoplamento progressivo.
- [ ] O plano evita recomendar migração massiva para `ResourceBase` sem necessidade de negócio.
- [ ] O roadmap resultante pode ser executado em pequenas entregas independentes.

## Potential Risks and Mitigations

1. **Misturar refatoração estrutural com reescrita funcional ampla**  
   Mitigation: tratar cada arquivo como unidade incremental de trabalho e validar comportamento existente antes de ampliar escopo.

2. **Converter indevidamente entidades transacionais em recursos GeoNode**  
   Mitigation: usar integração por associação apenas onde houver necessidade real de catálogo, metadados ou vínculo com datasets/documentos.

3. **Desacoplar sem endurecer segurança primeiro**  
   Mitigation: priorizar autenticação, autorização e auditoria antes de mudanças maiores na topologia do sistema.

4. **Criar tarefas grandes demais para execução futura**  
   Mitigation: manter o backlog granular por arquivo e tratar cada item como pequeno pacote independente.

## Alternative Approaches

1. **Modularização interna sem extração física**: menor custo inicial e melhor aderência ao estado atual, porém mantém dependência do monolito GeoNode.
2. **Integração seletiva com `ResourceBase` via modelos-ponte**: melhora interoperabilidade com catálogo sem deformar o domínio de negócio.
3. **Extração futura para serviço separado**: maior isolamento e autonomia, mas recomendada apenas após estabilização de contratos, segurança e testes.
