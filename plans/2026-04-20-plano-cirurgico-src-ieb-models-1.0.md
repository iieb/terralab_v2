# Plano Cirúrgico — Evolução de `src/ieb/models.py`

## Objective

Converter a análise estrutural de `src/ieb/models.py` em um backlog cirúrgico, com tarefas pequenas, focadas e executáveis de forma incremental, priorizando integridade do banco, coerência do domínio, redução de ambiguidade e melhoria da manutenção.

## Contexto e Fontes

- Arquivo principal analisado: `src/ieb/models.py:1-1300`
- Núcleo hierárquico do domínio: `src/ieb/models.py:128-312`
- Estrutura de indicadores e metas: `src/ieb/models.py:344-567`
- Registro operacional central: `src/ieb/models.py:570-623`
- Modelos satélite com dupla referência de indicador: `src/ieb/models.py:666-1178`
- Modelos de histórico: `src/ieb/models.py:810-818`, `src/ieb/models.py:999-1007`
- Modelos complementares finais: `src/ieb/models.py:1180-1300`

## Assumptions

- O plano deve privilegiar pequenas tarefas compatíveis com futuras entregas incrementais.
- A recomendação preferencial é fortalecer o modelo atual antes de qualquer refatoração ampla.
- A eventual unificação de `Indicador` e `IndicadorFinanciador` deve ser preparada com cuidado, não assumida como mudança imediata.
- Toda mudança estrutural futura deve preservar a semântica central de `AtividadeRegistro` como fato operacional.

## Implementation Plan

- [ ] **Trecho: `src/ieb/models.py:12-41` — adicionar regras de unicidade para vínculos entre OIs regionais e locais.** Racional: `OIRegLoc` não protege contra duplicação lógica do mesmo relacionamento.
- [ ] **Trecho: `src/ieb/models.py:44-77` — revisar tipos e validações dos dados territoriais e cadastrais básicos (`TIs`, `Aldeia`, `Indigena`).** Racional: CPF, RG e área estão modelados de forma permissiva e sem validações de integridade mais fortes.
- [ ] **Trecho: `src/ieb/models.py:82-95` — adicionar unicidade ao relacionamento entre `IGATI` e `TIs`.** Racional: `TIsIGATI` também permite duplicidade silenciosa do mesmo vínculo.
- [ ] **Trecho: `src/ieb/models.py:101-124` — revisar unicidade e padronização de identificadores institucionais em `Financiador`, `Instituicao` e `Equipe`.** Racional: `Financiador.sigla` já é único, mas `Instituicao.sigla`, CPF e outros identificadores ainda não têm proteção equivalente.
- [ ] **Trecho: `src/ieb/models.py:128-166` — fortalecer chaves de negócio de `Programa` e `Projeto`.** Racional: a estrutura principal do domínio merece proteção explícita para siglas, nomes operacionais e vínculos hierárquicos.
- [ ] **Trecho: `src/ieb/models.py:169-186` — criar unicidade contextual para códigos de `Componente` e `Atividade`.** Racional: códigos sem escopo protegido por projeto/componente podem colidir e gerar inconsistência operacional.
- [ ] **Trecho: `src/ieb/models.py:189-210` — adicionar constraints de unicidade em `EquipeProjeto`, `ProjetoOI` e `ProjetoTI`.** Racional: hoje esses relacionamentos aceitam repetição do mesmo par lógico.
- [ ] **Trecho: `src/ieb/models.py:213-236` — revisar naming, constraints e coerência dos vínculos `ProjetoIndicador` e `ProjetoIndicadorFin`.** Racional: esse trecho já introduz a separação estrutural entre indicador comum e indicador de financiador, que precisa de maior clareza conceitual.
- [ ] **Trecho: `src/ieb/models.py:241-312` — preservar as tabelas de ligação temáticas, mas revisar se todas possuem unicidade e semântica de negócio explícita.** Racional: esses vínculos são importantes para o domínio e devem ser tratados como relações fortes, não apenas auxiliares.
- [ ] **Trecho: `src/ieb/models.py:317-342` — consolidar o papel das choices globais de indicador e score de plano como contrato do domínio.** Racional: esse bloco define semântica transversal e precisa ser estável, legível e centralizado.
- [ ] **Trecho: `src/ieb/models.py:344-442` — analisar a viabilidade de unificação entre `Indicador` e `IndicadorFinanciador`.** Racional: a duplicação estrutural nesse trecho é o maior sinal de dívida de modelagem do arquivo.
- [ ] **Trecho: `src/ieb/models.py:344-442` — caso a unificação não seja imediata, definir constraints explícitas para convivência segura entre os dois modelos.** Racional: o modelo atual exige regras claras de fronteira entre indicador institucional e indicador específico de financiador.
- [ ] **Trecho: `src/ieb/models.py:445-567` — revisar a duplicação entre `Meta` e `MetaFinanciador` e preparar uma estratégia de consolidação lógica.** Racional: a repetição de estrutura e cálculo indica oportunidade clara de redução de complexidade.
- [ ] **Trecho: `src/ieb/models.py:445-567` — adicionar validações e constraints temporais em metas e períodos de apuração.** Racional: o banco deve proteger coerência entre `data_inicio`, `data` e valores base/meta.
- [ ] **Trecho: `src/ieb/models.py:570-590` — adicionar integridade temporal e coerência hierárquica em `AtividadeRegistro`.** Racional: `AtividadeRegistro` é o centro do domínio e precisa garantir datas válidas e relações coerentes entre projeto, componente, atividade e equipe.
- [ ] **Trecho: `src/ieb/models.py:593-623` — revisar o tratamento de anexos para evitar lógica pesada ou frágil diretamente nos models.** Racional: geração de thumbnail e upload acoplados ao `save()` podem dificultar manutenção e previsibilidade operacional.
- [ ] **Trecho: `src/ieb/models.py:629-662` — explicitar o papel dos catálogos geográficos (`UC`, `PA`, `TUC`) e revisar precisão do campo de área.** Racional: são entidades cadastrais centrais para somatórios e precisam de tipos e regras consistentes.
- [ ] **Trecho: `src/ieb/models.py:666-695` — corrigir a estratégia de unicidade e integridade do model `Area`.** Racional: a combinação atual de `unique_together` com `indicador` nulo e `indicador_financiador` opcional é estruturalmente frágil.
- [ ] **Trecho: `src/ieb/models.py:666-695` — revisar o cálculo persistido de `total_ha` para não depender apenas de `save()` com M2M.** Racional: somatórios baseados em relações M2M podem ficar desatualizados quando o vínculo muda após a gravação inicial.
- [ ] **Trecho: `src/ieb/models.py:699-734` — revisar `AreasProtegidas` com foco em unicidade, consistência dos totais e atualização de agregados.** Racional: esse model repete a mesma fragilidade estrutural de `Area`, com múltiplos campos derivados.
- [ ] **Trecho: `src/ieb/models.py:743-761` — corrigir a integridade lógica de `Pessoas`, especialmente no vínculo com tipos de indicador e nos limites das desagregações.** Racional: o banco deveria proteger melhor a coerência entre total de pessoas e campos derivados.
- [ ] **Trecho: `src/ieb/models.py:764-818` — revisar `Lei`, `Leis` e `LeiHistorico` para fortalecer catálogo, agregação e auditoria.** Racional: além de totais derivados frágeis, o histórico usa usuário textual sem integridade referencial.
- [ ] **Trecho: `src/ieb/models.py:821-835` — revisar `Organizacoes` para adicionar consistência entre total e desagregações.** Racional: a estrutura atual permite divergência entre o total declarado e os subtotais informados.
- [ ] **Trecho: `src/ieb/models.py:838-857` — revisar `Evento` para garantir que o cálculo de `total` seja confiável e semanticamente estável.** Racional: totais derivados não devem depender de estados implícitos ou campos parcialmente preenchidos.
- [ ] **Trecho: `src/ieb/models.py:868-877` — avaliar se `Rede` deve aceitar múltiplos registros por atividade/indicador ou se precisa de restrição adicional por nome/tipo.** Racional: hoje o modelo é muito aberto e pode gerar duplicidade de informação.
- [ ] **Trecho: `src/ieb/models.py:881-915` — revisar `PequenoProjeto` e `Fundo` com foco em precisão monetária e coerência entre quantidade, tipo e valor total.** Racional: esses modelos misturam quantitativos e valores sem constraints semânticas mais fortes.
- [ ] **Trecho: `src/ieb/models.py:919-930` — revisar `Outro` para definir melhor o contrato mínimo de dados e evitar registros vagos demais.** Racional: a flexibilidade do modelo pode comprometer a qualidade analítica do banco.
- [ ] **Trecho: `src/ieb/models.py:934-1007` — revisar a arquitetura de `Plano`, `Planos` e `PlanoHistorico` para separar claramente catálogo, evento de mudança e auditoria.** Racional: hoje o `save()` mistura atualização de estado com gravação histórica e usuário textual.
- [ ] **Trecho: `src/ieb/models.py:1010-1056` — revisar `Parceria` e `Parcerias` para proteger integridade do catálogo e recalcular totais de forma confiável.** Racional: a estrutura atual persiste agregados dependentes de M2M sem blindagem suficiente.
- [ ] **Trecho: `src/ieb/models.py:1060-1088` — revisar `Mobilizados` para fortalecer tipos financeiros e constraints de valor.** Racional: sendo dado financeiro, esse model merece maior precisão e proteção contra valores inválidos.
- [ ] **Trecho: `src/ieb/models.py:1091-1140` — revisar `Produto` e `Produtos` com foco em consistência do catálogo e dos totais agregados.** Racional: o mesmo padrão de agregação frágil por M2M reaparece aqui.
- [ ] **Trecho: `src/ieb/models.py:1143-1178` — revisar `Contrato` e `Contratos` para garantir coerência entre estado, valor e total agregado.** Racional: `valor_total` pode ficar inconsistente e há mistura de catálogo com somatório persistido.
- [ ] **Trecho: `src/ieb/models.py:1180-1209` — alinhar `Modelo` e `AtividadeRegistroModelo` com a estratégia geral de indicadores, incluindo o caso de financiador.** Racional: esse trecho hoje está desalinhado em relação ao padrão adotado nas demais tabelas satélite.
- [ ] **Trecho: `src/ieb/models.py:1212-1300` — separar logicamente os modelos finais de formação e política pública indígena do núcleo transacional de monitoramento.** Racional: esse bloco final amplia o escopo do arquivo e dificulta entender os subdomínios do banco.
- [ ] **Arquivo: `src/ieb/models.py` — substituir `unique_together` legados por `UniqueConstraint` nomeadas e, quando necessário, condicionais.** Racional: isso melhora clareza, expressividade e aderência aos cenários com campos opcionais.
- [ ] **Arquivo: `src/ieb/models.py` — introduzir `CheckConstraint` para regras temporais, exclusividade entre indicadores e não negatividade de valores.** Racional: parte relevante da integridade hoje depende apenas da aplicação.
- [ ] **Arquivo: `src/ieb/models.py` — revisar uso de `FloatField` versus `DecimalField` em áreas, metas e valores agregados.** Racional: somatórios institucionais e dados financeiros pedem maior previsibilidade numérica.
- [ ] **Arquivo: `src/ieb/models.py` — revisar uso excessivo de `related_name='+'` onde isso dificulta manutenção e introspecção.** Racional: a supressão completa de reversos reduz legibilidade do domínio.
- [ ] **Arquivo: `src/ieb/models.py` — preparar futura modularização do arquivo por subdomínio sem alterar imediatamente o comportamento do banco.** Racional: reduzir o monolito facilita manutenção futura e esclarece fronteiras de negócio.

## Verification Criteria

- [ ] Existe uma lista granular de tarefas pequenas cobrindo os principais blocos de `src/ieb/models.py`.
- [ ] O plano distingue problemas de integridade, duplicação, precisão numérica, auditoria e manutenção.
- [ ] As tarefas permitem atacar o modelo atual incrementalmente, sem exigir uma reescrita total de uma vez.
- [ ] A estratégia preserva `AtividadeRegistro` como núcleo operacional enquanto fortalece o restante do esquema.
- [ ] O backlog está pronto para ser executado em pequenas entregas futuras por trecho do arquivo.

## Potential Risks and Mitigations

1. **Transformar o backlog cirúrgico em uma refatoração grande demais**  
   Mitigation: tratar cada linha como intervenção incremental, validando impacto local antes de avançar para o próximo bloco.

2. **Quebrar compatibilidade com dados existentes ao reforçar constraints**  
   Mitigation: prever saneamento e diagnóstico dos dados antes de impor constraints mais rígidas.

3. **Persistir agregados sem resolver o problema estrutural de atualização**  
   Mitigation: revisar primeiro a estratégia de atualização de M2M antes de confiar em totais armazenados.

4. **Reduzir duplicação sem clareza sobre o papel de indicadores de financiador**  
   Mitigation: decidir conceitualmente a fronteira entre indicador institucional e indicador específico antes de consolidar models.

## Alternative Approaches

1. **Endurecer o modelo atual sem unificar indicadores**: menor risco imediato, mas mantém duplicação estrutural relevante.
2. **Unificar progressivamente `Indicador`/`IndicadorFinanciador` e `Meta`/`MetaFinanciador`**: reduz dívida de modelagem, mas exige migração conceitual e cuidado com dados existentes.
3. **Separar primeiro o arquivo por subdomínio e só depois ajustar o banco**: melhora leitura e governança da manutenção, porém não resolve imediatamente a integridade relacional.
