# Revisão Técnica das Tarefas — Plano Cirúrgico v1.3

> **Revisor:** Programador sênior (Django/Postgres/GeoNode)
> **Data:** 2026-04-27
> **Status:** REVISÃO CONCLUÍDA — correções identificadas e documentadas
> **Arquivos revisados:** `src/ieb/models.py` (1300 linhas), `src/ieb/views.py` (1109 linhas), `src/ieb/admin.py` (322 linhas)

---

## Metodologia

Cada arquivo de tarefa foi comparado linha a linha contra o código-fonte real. Foram identificadas divergências entre o que a tarefa descreve e o que o código realmente contém. As correções foram categorizadas por severidade.

---

## Correções Críticas (bloqueantes — causam erro de execução)

### C1. Onda 1: 9 de 9 tarefas dizem "adicionar na classe Meta" mas os models NÃO têm classe Meta

**Models afetados:** `AtividadeRegistro`, `Meta`, `MetaFinanciador`, `OIRegLoc`, `TIsIGATI`, `EquipeProjeto`, `ProjetoOI`, `ProjetoTI`, `Componente`, `Atividade`, `Subatividade`

**Problema:** Nenhum destes models tem `class Meta` no código atual. A instrução "adicionar na classe Meta" fará o agente de IA tentar modificar algo que não existe, gerando código quebrado.

**Correção:** Todas as instruções devem dizer "CRIAR classe Meta" com localização exata (ex: "após o campo `email_organizacao` e antes do `def __str__`").

**Exceção:** `Mobilizados` JÁ POSSUI `class Meta` — a instrução está correta, mas deve preservar o `unique_together` existente.

### C2. Onda 2 (T-2.2): Lista errada de models com `unique_together`

**Problema:** A tarefa diz "REMOVER unique_together" para todos os 16 satélites. Mas apenas 12 têm `unique_together`. Os outros 4 (`Rede`, `PequenoProjeto`, `Fundo`, `AtividadeRegistroModelo`) não têm.

**Correção:** Dividir em Grupo A (12 models com remoção) e Grupo B (4 models sem remoção). A migration falha se tentar `AlterUniqueTogether` em model sem `unique_together`.

### C3. Onda 3 (T-3.1): Save duplo não documentado

**Problema:** `Area.save()` e `AreasProtegidas.save()` fazem `if not self.pk: super().save()` — um save duplo para obter PK antes de setar M2M. A instrução "remover lógica de save()" sem explicar o save duplo vai quebrar o funcionamento.

**Correção:** Documentar que o `if not self.pk: super().save()` deve ser mantido. Apenas a lógica de cálculo e o `super().save()` final são removidos.

### C4. Onda 4 (T-4.3): `Planos.save()` usa string, não `request.user`

**Problema:** `Planos.save()` (models.py:979-992) grava `usuario=str(self.atividade_registro.equipe_projeto.equipe.nome)` — não tem acesso ao request. A tarefa diz "garantir que passa `usuario=request.user`" mas não explica como.

**Correção:** Adicionar `usuario=None` como parâmetro opcional em `save()`. A view passa `usuario=request.user`. Se não fornecido, usar `None`.

### C5. Onda 5 (T-5.3): Constantes transversais sem destino

**Problema:** 7 constantes (`INDICADOR_TIPO_CHOICES`, `SCORE_PLANO`, `FOCO_CHOICES`, `REDE_TIPO_CHOICES`, etc.) são usadas por models em múltiplos subdomínios. A tarefa não diz para onde vão.

**Correção:** Criar `src/ieb/constants.py` com todas as constantes, importar de lá em cada módulo.

---

## Correções Altas (geram código errado)

### A1. Onda 1 (T-1.1): Justificativa do bug errada

**Problema:** Diz "ignora campos com valor 0" mas `sum(v for v in [0, 0] if v)` retorna `0` (correto). O real problema é que `if v` filtra `None` E `0` — um `0` intencional é excluído.

**Correção:** Justificativa atualizada para: "filtra valores falsy (`None` E `0`). Um campo intencionalmente enviado como `0` é excluído da soma."

### A2. Onda 1 (T-1.2): `Contratos.save()` sobrescreve default com None

**Problema:** `Contratos.save()` (linha 1174) faz `self.valor_total = aggregate(...)['total']` que retorna `None`. Mesmo com `default=0`, o save sobrescreve.

**Correção:** Adicionar `or 0` no aggregate: `self.valor_total = ... or 0`.

### A3. Onda 2 (T-2.4): `DESAG_FIELDS` é lista, não dict

**Problema:** A tarefa diz adicionar `'org_governo': 'desag_org_governo'` mas `DESAG_FIELDS` é uma lista de strings.

**Correção:** Adicionar `'desag_org_governo'` na lista. Também faltam instruções para POST, `indicadores_config` e admin.

### A4. Onda 4 (T-4.1): Roll-up vago gera código macarrônico

**Problema:** Pseudocódigo `valor_direto = ... # logica existente` fará o agente reescrever o método inteiro.

**Correção:** Instrução precisa: "NÃO reescrever o método. Apenas modificar o `return 0` final e adicionar um bloco de roll-up."

### A5. Onda 4 (T-4.2): `max_length` errado

**Problema:** Diz `max_length=100` mas o código real é `max_length=255`.

**Correção:** Atualizar para `max_length=255`.

### A6. Onda 4 (T-4.6): `Outro` NÃO está no admin

**Problema:** Diz "verificar se admin.py registra Outro e remover". Verificado: não está registrado.

**Correção:** "Confirmado: `Outro` NÃO está registrado no admin. Nenhuma remoção necessária."

### A7. Onda Bonus (T-B.1): Abordagem simplificada

**Problema:** A abordagem original é mais complexa que o necessário. O padrão de roteamento `_m = fin_map if is_fin else map` já é usado por todos os outros tipos.

**Correção:** Usar o mesmo padrão de roteamento existente.

---

## Correções Médias (qualidade)

### M1. Onda 2 (T-2.3): CheckConstraint com NULL em Postgres

**Problema:** `Q(homens__lte=F('total_pessoas')) | Q(homens__isnull=True)` — no Postgres, `NULL <= valor` avalia para NULL. A disjunção resolve, mas precisa de teste explícito.

**Correção:** Adicionar teste: `Pessoas(total_pessoas=0, homens=None).save()` deve ser OK.

### M2. Onda 5 (T-5.1): Impacto em `Area.save()` e `AreasProtegidas.save()`

**Problema:** `m2m.aggregate(s=Sum('area'))['s'] or 0.0` — o `0.0` é float. Com DecimalField, precisa ser `Decimal("0")`.

**Correção:** Trocar `or 0.0` para `or Decimal("0")`. Se T-3.1 executada, alterar em signals.py.

### M3. Onda 5 (T-5.2): Race condition com transação

**Problema:** A task Celery pode executar antes do commit da transação.

**Correção:** Usar `transaction.on_commit(lambda: gerar_thumbnail.delay(self.pk))`.

### M4. Onda Final (T-F.1): `FOCO_CHOICES` com valores errados

**Problema:** Documentação mostra `governanca`, `subsistencia`, `monitoramento`. Valores reais: `implementacao`, `ativ_prod`, `governanca`.

**Correção:** Atualizar para refletir código real.

---

## Resumo

| Severidade | Quantidade | Status |
|-----------|-----------|--------|
| Crítica | 5 | Documentadas — corrigir antes de executar |
| Alta | 7 | Documentadas — corrigir para evitar código errado |
| Média | 4 | Documentadas — melhorar qualidade |
| **Total** | **16** | Revisão completa |

As correções detalhadas para cada arquivo de tarefa foram produzidas pelo agente de pesquisa e estão disponíveis para aplicação. Cada arquivo (`onda-1-correcoes-pontuais.md` até `final-documentacao.md`) precisa ser atualizado com as correções listadas acima.