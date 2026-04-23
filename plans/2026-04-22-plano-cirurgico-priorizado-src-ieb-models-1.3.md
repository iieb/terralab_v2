# Plano Cirúrgico — `src/ieb/models.py` (Versão 1.3 — Revisão técnica com domínio IEB)

## Sobre este documento

Revisão ponto a ponto da versão 1.2, conduzida com quem conhece o domínio funcional do IEB.
Registra decisões de aceitar, rejeitar ou adaptar cada item antes da implementação.

---

## P0 — Integridade estrutural

### P0.1 — Formalizar o contrato entre `Indicador` e `IndicadorFinanciador`

**Status:** ACEITO COM EXPANSÃO DE ESCOPO

**Contrato definido:**
- `Indicador` → indicador institucional do IEB, usado para agregar estatísticas entre projetos, programas e ao longo do tempo
- `IndicadorFinanciador` → indicador específico de um financiador; pode ter formato distinto (ex: escala de score 1–5) e pode ou não ter equivalente institucional

**Decisão tomada:**
Adicionar campo `equivalente_ieb = ForeignKey(Indicador, null=True, blank=True)` em `IndicadorFinanciador`, permitindo roll-up automático para o indicador institucional quando há equivalência.

**Três casos cobertos:**

| Caso | Como fica no modelo |
|---|---|
| Indicador IEB puro | `Indicador`, sem vínculo de financiador |
| Indicador de financiador sem equivalente IEB | `IndicadorFinanciador`, `equivalente_ieb=null` |
| Indicador de financiador com equivalente IEB | `IndicadorFinanciador`, `equivalente_ieb=<Indicador>` |

**Regra de roll-up:**
Quando um registro de campo aponta para `IndicadorFinanciador` com `equivalente_ieb` preenchido, os valores são contabilizados automaticamente no indicador IEB correspondente — sem duplicar o registro de campo.

**Exemplo:**
"Indígenas castanheiros com formação em boas práticas" (financiador) com `equivalente_ieb` → "Indígenas capacitados em bioeconomia" (IEB). Ao registrar 20 pessoas no indicador do financiador, esses 20 entram na consolidação institucional sem novo registro.

**Consequência para P0.2:**
Um registro satélite (Pessoas, Area, etc.) aponta sempre para exatamente um indicador — institucional ou de financiador. O roll-up institucional é resolvido pela equivalência, não por duplo preenchimento. Isso torna P0.2 consequência natural deste contrato.

---

### P0.2 — Definir exclusividade entre `indicador` e `indicador_financiador` nos modelos satélite

**Status:** ACEITO COM AJUSTE DE ESCOPO

**Decisão tomada:**
A constraint correta é "no máximo um — nunca os dois simultaneamente". Registros sem nenhum indicador são válidos (atividade realizada sem contribuir para um indicador específico).

**Casos válidos por registro satélite:**

| `indicador` | `indicador_financiador` | Válido? |
|---|---|---|
| `null` | `null` | Sim — atividade sem indicador |
| preenchido | `null` | Sim — indicador IEB |
| `null` | preenchido | Sim — indicador de financiador |
| preenchido | preenchido | **Não** — ambíguo, bloqueado |

**Consequência:** uma atividade pode gerar múltiplos registros satélite do mesmo tipo (ex: dois `Pessoas`), desde que cada um aponte para um indicador diferente. Ex: "indígenas treinados" e "indígenas aplicando conhecimento" são dois indicadores distintos, dois registros `Pessoas` válidos para a mesma atividade.

---

### P0.3 — Substituir `unique_together` por `UniqueConstraint` condicionais

**Status:** ACEITO

**Decisão tomada:**
O `unique_together = ('atividade_registro', 'indicador')` atual não cobre `indicador_financiador`. Substituir em todos os satélites pelo padrão:

```python
constraints = [
    models.UniqueConstraint(
        fields=['atividade_registro', 'indicador'],
        condition=models.Q(indicador__isnull=False),
        name='<model>_unique_por_indicador'
    ),
    models.UniqueConstraint(
        fields=['atividade_registro', 'indicador_financiador'],
        condition=models.Q(indicador_financiador__isnull=False),
        name='<model>_unique_por_indicador_financiador'
    ),
    models.CheckConstraint(
        check=~models.Q(indicador__isnull=False, indicador_financiador__isnull=False),
        name='<model>_nao_ambos_indicadores'
    ),
]
```

**O que bloqueia:** o mesmo indicador registrado duas vezes para a mesma atividade.
**O que permite:** indicadores diferentes do mesmo tipo na mesma atividade (ex: dois `Pessoas` com indicadores distintos).

---

### P0.4 — Revisar `Area` como caso-base de fragilidade estrutural

**Status:** ACEITO — implementação derivada de P0.2/P0.3 e P0.9

Não exige decisão de domínio separada. Aplicar o padrão de constraints definido em P0.2/P0.3 e a estratégia de M2M definida em P0.9. `Area` serve de modelo de referência para os demais satélites.

---

### P0.5 — Revisar `AreasProtegidas` com a mesma estratégia de `Area`

**Status:** ACEITO — implementação derivada de P0.4

Mesmo padrão de `Area`. Resolver junto com P0.4.

---

### P0.6 — Revisar `Pessoas` para coerência entre vínculo analítico e desagregações

**Status:** ACEITO

**Contrato definido:**
- `homens` + `mulheres` são mutuamente exclusivos e exaustivos — quando ambos preenchidos, devem somar `total_pessoas`. Validação exata da soma no `clean()` do model ou formulário (não expressável diretamente em `CheckConstraint` no Django ORM).
- `jovens`, `pct_indigenas`, `pct_extrativistas`, `pct_quilombolas`, `servidor_publico` são subconjuntos independentes e sobrepostos — cada um ≤ `total_pessoas`, sem obrigação de somar entre si.

**Constraints a adicionar:** cada subgrupo ≤ `total_pessoas` via `CheckConstraint`. Validação de soma de `homens + mulheres == total_pessoas` no `clean()`.

---

### P0.7 — Revisar `Organizacoes` — subtotais exaustivos ou informativos?

**Status:** ACEITO COM ADIÇÃO DE CAMPO

**Contrato definido:**
Todas as categorias são subconjuntos independentes e sobrepostos — uma organização pode pertencer a mais de uma categoria. Nenhuma obrigação de somar ao total; cada categoria ≤ `total_organizacoes`.

**Adição de campo:** incluir `org_governo = models.PositiveIntegerField(null=True, blank=True)` junto às demais desagregações.

**Constraints a adicionar:** cada subgrupo ≤ `total_organizacoes` via `CheckConstraint`.

---

### P0.8 — Estabilizar a semântica de `Evento.total`

**Status:** ACEITO — correção técnica simples

Na prática do IEB a distinção entre `None` e `0` não tem relevância funcional — o que importa são valores acima de zero. A correção padroniza o comportamento do cálculo e evita bugs futuros.

**Mudança:** substituir `if v` por `or 0` no `save()`:
```python
self.total = sum((v or 0) for v in [self.formacoes, self.seminarios, self.encontros, self.reunioes])
```

---

### P0.9 — Redesenhar agregados persistidos dependentes de M2M

**Status:** ACEITO — alta prioridade

Os totais serão usados em dashboards. Manter sempre sincronizados é requisito, não opcional.

**Mudança:** substituir lógica de `save()` por sinais `m2m_changed` em `Leis`, `Parcerias`, `Produtos` e `Contratos`. O sinal dispara em qualquer mudança da relação M2M (add, remove, set, clear) — inclusive pelo admin, formulário, shell e futura API.

```python
@receiver(m2m_changed, sender=Leis.leis.through)
def atualizar_totais_leis(sender, instance, **kwargs):
    instance.total_leis = instance.leis.count()
    # demais totais...
    instance.save(update_fields=[...])
```

**Vale também para `Area` e `AreasProtegidas`** (P0.4/P0.5) — mesma estratégia, substituir `save()` por `m2m_changed`.

---

### P0.10 — Corrigir semântica de `Contratos.valor_total`

**Status:** ACEITO — correção técnica simples

**Mudança:** adicionar `default=0` no campo `valor_total` de `Contratos`, eliminando ambiguidade entre "não calculado" e "zero". Dashboards financeiros não precisam tratar `NULL` como caso especial.

---

### P0.11 — Impor integridade temporal em `AtividadeRegistro`

**Status:** ACEITO

**Mudança:** `CheckConstraint` garantindo `data_final >= data_inicio`. Erro de digitação, nunca faz sentido funcionalmente.

---

### P0.12 — Impor integridade temporal em `Meta` e `MetaFinanciador`

**Status:** ACEITO

**Mudança:** `CheckConstraint` garantindo `data >= data_inicio` quando `data_inicio` está preenchido. Mesmo princípio de P0.11.

---

### P0.13 — Introduzir `CheckConstraint` transversais

**Status:** ABSORVIDO — não exige implementação própria

Coberto pelos itens P0.2, P0.3, P0.6, P0.7, P0.8, P0.11 e P0.12. O princípio de mover validações para o banco já está operacionalizado nesses itens.

---

## P1 — Coerência de domínio

### P1.1 — Documentar por que `Meta` e `MetaFinanciador` existem separados

**Status:** ACEITO — separação mantida, razão formalizada

**Contrato definido:**
Ambos os models são de escopo de projeto. A distinção é qual tipo de indicador referenciam:

- `Meta` → projeto + indicador institucional IEB (`Indicador`)
- `MetaFinanciador` → projeto + indicador de financiador (`IndicadorFinanciador`)

Um projeto pode ter os dois tipos simultaneamente para indicadores distintos. A agregação institucional entre projetos é feita por queries, aproveitando o `equivalente_ieb` definido em P0.1 para unir dados de ambos os caminhos quando há equivalência.

**Não há necessidade de unificar os models.** A separação é consequência direta e justificada da dualidade `Indicador`/`IndicadorFinanciador`.

---

### P1.2 — Corrigir auditoria de `LeiHistorico`

**Status:** ACEITO

**Mudança:** substituir `usuario = CharField` por `usuario = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)`. Sistema usa `auth.User` padrão do Django, compartilhado com GeoNode e demais aplicações.

---

### P1.3 — Corrigir auditoria de `PlanoHistorico`

**Status:** ACEITO — mesmo padrão de P1.2

---

### P1.4 — Separar em `Planos` o que é catálogo, transição de estado e histórico

**Status:** ACEITO

**Contexto:** o histórico de evolução de status de planos tem uso ativo — serve para acompanhamento de processos. Comportamento implícito no `save()` pode gerar entradas espúrias (ex: salvar para corrigir texto sem mudar status).

**Mudança:** histórico só é gravado quando `situacao` efetivamente muda. Transição de estado vira operação explícita — método dedicado ou sinal `pre_save` comparando valor anterior com novo.

---

### P1.5 — Adicionar unicidade lógica em `OIRegLoc`

**Status:** ACEITO

**Mudança:** `unique_together = ('oi_regional', 'oi_local')`. Vínculo de pertencimento, não evento repetível.

---

### P1.6 — Adicionar unicidade lógica em `TIsIGATI`

**Status:** ACEITO — mesmo padrão de P1.5

**Mudança:** `unique_together = ('ti', 'igati')`.

---

### P1.7 — Adicionar unicidade em `EquipeProjeto`, `ProjetoOI` e `ProjetoTI`

**Status:** ACEITO

Relações muitos-para-muitos sem necessidade de registrar o mesmo par mais de uma vez. Não há papéis/funções diferenciados por enquanto.

**Mudanças:**
- `EquipeProjeto`: `unique_together = ('pessoa', 'projeto')`
- `ProjetoOI`: `unique_together = ('projeto', 'oi')`
- `ProjetoTI`: `unique_together = ('projeto', 'ti')`

---

### P1.8 — Definir unicidade contextual de `Componente.codigo` e `Atividade.codigo`

**Status:** ACEITO

Códigos são únicos dentro do escopo pai, não globalmente.

**Mudanças:**
- `Componente`: `unique_together = ('projeto', 'codigo')`
- `Atividade`: `unique_together = ('componente', 'codigo')`

---

### P1.9 — Definir unicidade contextual de `Subatividade.codigo`

**Status:** ACEITO — mesmo padrão de P1.8

**Mudança:** `unique_together = ('atividade', 'codigo')`

---

### P1.10 — Decidir quais identificadores institucionais são chaves de negócio

**Status:** ADIADO

Cadastros operacionais por enquanto — duplicidade eventual é tolerável. Unicidade de CPF, CNPJ e siglas pode ser exigida futuramente quando o controle cadastral for prioridade. Não impor constraints agora para não bloquear fluxos onde o dado não está disponível no momento do cadastro.

---

### P1.11 — Revisar `Mobilizados` como dado financeiro com regras mais rígidas

**Status:** ACEITO

**Mudança:** `CheckConstraint` garantindo `valor_mobilizado > 0`. Se existe o registro, houve mobilização com valor positivo — zero não é válido.

---

### P1.13 — Decidir se `Rede` é ocorrência livre ou consolidado lógico por atividade/indicador

**Status:** REDESENHO — `Rede` vira cadastro + tabela de ligação

A mesma rede pode ser fortalecida por ações de diferentes projetos. O model atual (satélite de `AtividadeRegistro`) não permite reuso — cada atividade cria sua própria entrada sem identidade persistente.

**Novo desenho imediato:**
- `Rede` vira entidade cadastral: `nome`, `tipo`
- Nova tabela de ligação `AtividadeRegistroRede` conecta atividades a redes, com vínculo de indicador e desagregações de participação
- Nem toda atividade estará relacionada a uma rede — o vínculo é opcional
- O formulário de registro já condiciona a exibição dos campos de indicadores pela relação com a atividade; a regra "só aparece quando há meta de rede" é validação de UI, não constraint de banco

```python
class Rede(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=REDE_TIPO_CHOICES)

class AtividadeRegistroRede(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    rede                  = models.ForeignKey(Rede, on_delete=models.CASCADE)
    indicador             = models.ForeignKey(Indicador, null=True, blank=True, ...)
    indicador_financiador = models.ForeignKey(IndicadorFinanciador, null=True, blank=True, ...)
    quantidade            = models.PositiveIntegerField(default=1)
    pessoas               = models.PositiveIntegerField(null=True, blank=True)
    instituicoes          = models.PositiveIntegerField(null=True, blank=True)
    organizacoes          = models.PositiveIntegerField(null=True, blank=True)
    # constraints de P0.2/P0.3 aplicadas aqui
```

**Análises de indicador que este redesenho deve suportar futuramente:**
- "Redes criadas" — contagem de `Rede` registradas em um período
- "Participação institucional em X redes" — requer M2M de `Rede` com `Instituicao`, `OIsLocal`, `OIsRegional`
- "Redes de bioeconomia fortalecidas" — requer campo de tema/categoria em `Rede`

**Melhorias futuras a planejar:**
- Cadastro completo de composição da rede (quais organizações a integram permanentemente)
- Registro de participantes presentes em cada atividade específica
- Campo de tema/categoria para análises temáticas

---

### P1.14 — Redefinir contrato mínimo de `Outro`

**Status:** REMOVER

Model criado como reserva, sem dados reais e sem caso de uso previsto. Manter código morto aumenta custo cognitivo sem benefício. Remover `Outro` e o item `'outro'` do `INDICADOR_TIPO_CHOICES` se não houver referência ativa em views, forms ou templates.

**Atenção na implementação:** verificar se `'outro'` ainda aparece em `INDICADOR_TIPO_CHOICES` e no `SUM_MAP` do `Meta.realizado` antes de remover.

---

### P1.12 — Revisar coerência semântica de `PequenoProjeto` e `Fundo`

**Status:** ACEITO COM REGISTRO DE MELHORIAS FUTURAS

**Mudanças imediatas:**
- `CheckConstraint` garantindo `quantidade >= 1` — se existe o registro, houve pelo menos um pequeno projeto
- `valor_total` passa a ser obrigatório (`null=False`, sem `blank=True`)

**Melhorias futuras a planejar (fora do escopo desta revisão):**
- Campo de status de execução (em curso / finalizado) para acompanhamento da evolução
- Campo indicando responsável pela execução financeira: organização parceira diretamente ou IEB

---

### P1.15 — Alinhar `AtividadeRegistroModelo` à estratégia geral de indicadores

**Status:** ACEITO — ajuste pontual

`Modelo` é uma metodologia/protocolo/instrumento de gestão. `AtividadeRegistroModelo` registra a adoção de um modelo numa atividade específica com seu status de ciclo de vida (em desenvolvimento → implementação ativa → difundido). O mesmo modelo pode estar em estágios diferentes em projetos distintos — o status pertence à relação, não ao modelo.

O design já segue o padrão correto (entidade cadastral + tabela de ligação). O único ajuste necessário é adicionar `indicador_financiador` para alinhar com P0.2/P0.3.

---

## P2 — Qualidade arquitetural

### P2.1 — Revisar tratamento de dados sensíveis como CPF e RG

**Status:** ADIADO — junto com P1.10

Validação de formato e política de retenção de dados sensíveis são decisões de governança a tomar futuramente.

---

### P2.2 — Revisar precisão do campo `area` em `TIs`, `UC`, `PA` e `TUC`

**Status:** ACEITO — junto com P2.3

---

### P2.3 — Revisar `FloatField` versus `DecimalField` em metas, áreas e agregados

**Status:** ACEITO

**Mudança:** substituir `FloatField` por `DecimalField(max_digits=12, decimal_places=4)` em todos os campos de área geográfica (`TIs.area`, `UC.area`, `PA.area`, `TUC.area`, `Area.total_ha`, `AreasProtegidas.total_ha`). Elimina acúmulo de erro de ponto flutuante em somatórios de dashboards territoriais. Valores financeiros já usam `DecimalField`.

---

### P2.4 — Revisar uso extensivo de `related_name='+'`

**Status:** ACEITO

**Mudança:** substituir `related_name='+'` por nomes explícitos em todos os FKs de `indicador` e `indicador_financiador` nos modelos satélite. Permite queries diretas a partir do indicador (`indicador.pessoas_set.all()`), melhora debugging no admin e prepara a futura API.

---

### P2.5 — Desacoplar processamento de anexos da lógica direta dos models

**Status:** ACEITO

**Mudança:** mover geração de thumbnail de `AtividadeRegistroFoto.save()` para task Celery assíncrona. O upload salva o arquivo imediatamente; o thumbnail é gerado em background. Melhora responsividade e isola falha de processamento de imagem do fluxo principal. O projeto já usa Celery.

---

### P2.6 — Separar logicamente o bloco de formação e política pública indígena do núcleo transacional

**Status:** ACEITO

**Mudança:** isolar `FormacaoIndigena`, `PoliticaPublica` e modelos relacionados (a partir de ~linha 1212) em módulo próprio como parte da modularização de P2.7.

---

### P2.8 — Explicitar o papel das choices globais de indicador e score de plano como contrato transversal

**Status:** ACEITO — documentação no código

`INDICADOR_TIPO_CHOICES` e `SCORE_PLANO` são contratos transversais: qualquer adição ou remoção impacta `SUM_MAP`/`COUNT_MAP` no `realizado` de `Meta` e `MetaFinanciador`, os satélites, e futuros filtros de dashboard. Adicionar comentário explícito no código alertando para esse alcance.

---

### P2.9 — Revisar papel operacional de nomes e siglas em `Programa` e `Projeto`

**Status:** ADIADO — junto com P1.10

Decisão de governança cadastral a tomar futuramente.

---

### P2.10 — Padronizar semântica das tabelas de ligação temáticas

**Status:** ABSORVIDO

Coberto pelas decisões de P1.7, P1.8, P1.9 e P1.13. Não exige implementação própria.

---

### P2.7 — Preparar modularização futura do arquivo por subdomínio

**Status:** ACEITO

**Mudança:** dividir `models.py` em módulos por subdomínio, mantendo `models/__init__.py` com imports para preservar compatibilidade com código existente:

```
ieb/models/
  __init__.py         ← re-exporta tudo para não quebrar imports existentes
  movimento.py        ← OIsRegional, OIsLocal, TIs, Indigena, IGATI, OIRegLoc, TIsIGATI
  projetos.py         ← Programa, Projeto, Componente, Atividade, Subatividade, equipe, vínculos
  indicadores.py      ← Indicador, IndicadorFinanciador, Meta, MetaFinanciador, choices globais
  monitoramento.py    ← AtividadeRegistro, todos os satélites
  catalogos.py        ← UC, PA, TIs, TUC, Lei, Modelo, Rede e demais cadastros de referência
  organizacional.py   ← Parceria, Contrato, Financiador, Instituicao, Planos
  formacao.py         ← FormacaoIndigena, PoliticaPublica e subdomínio de formação
```

Executar após estabilização dos demais itens desta revisão.
