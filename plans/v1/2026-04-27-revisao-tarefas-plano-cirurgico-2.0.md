# Revisão Técnica das Tarefas — Plano Cirúrgico v1.3

> **Revisor:** Programador sênior (Django/Postgres/GeoNode)
> **Data:** 2026-04-27
> **Status:** CORREÇÕES NECESSÁRIAS — aplicar antes de executar

---

## Problemas Críticos (bloqueantes)

### C1. T-1.3, T-1.4, T-1.5–1.9: Models sem classe Meta

**Problema:** As tarefas dizem "adicionar na classe Meta" mas os models `AtividadeRegistro`, `Meta`, `MetaFinanciador`, `OIRegLoc`, `TIsIGATI`, `EquipeProjeto`, `ProjetoOI`, `ProjetoTI`, `Componente`, `Atividade`, `Subatividade` **não têm classe Meta** no código atual. 

**Correção:** Cada tarefa deve dizer explicitamente "CRIAR classe Meta" (não "adicionar na"). Exemplo:

```python
# ANTES (sem Meta):
class OIRegLoc(models.Model):
    oiregional = models.ForeignKey(OIsRegional, on_delete=models.CASCADE)
    oilocal = models.ForeignKey(OIsLocal, on_delete=models.CASCADE)
    ...

# DEPOIS (criar Meta):
class OIRegLoc(models.Model):
    oiregional = models.ForeignKey(OIsRegional, on_delete=models.CASCADE)
    oilocal = models.ForeignKey(OIsLocal, on_delete=models.CASCADE)
    ...
    class Meta:
        unique_together = ('oiregional', 'oilocal')
```

**Risco IA:** Sem esta instrução, o agente pode tentar adicionar a constraint em Meta inexistente e gerar código quebrado.

---

### C2. T-2.2: Lista errada de models com `unique_together`

**Problema:** A tarefa diz "REMOVER: unique_together" para todos os 16 satélites. Mas no código real:
- **TÊM** `unique_together`: Pessoas, Organizacoes, Area, AreasProtegidas, Evento, Leis, Parcerias, Produtos, Contratos, Mobilizados, Outro, Planos
- **NÃO TÊM** `unique_together`: Rede, PequenoProjeto, Fundo, AtividadeRegistroModelo

**Correção:** Separar claramente:
- Models que precisam de `AlterUniqueTogether(model, set())` para remover
- Models que só precisam de `AddConstraint` (sem remoção prévia)

**Risco IA:** Se o agente tentar remover `unique_together` de um model que não tem, a migration falha.

---

### C3. T-3.1: Save duplo nos models M2M

**Problema:** `Area.save()` (linha 682-692) e `AreasProtegidas.save()` (linha 719-731) fazem `if not self.pk: super().save()` — um save duplo para obter o PK antes de setar M2M. O signal `m2m_changed` não é disparado durante este primeiro save. A instrução "remover a lógica de save()" sem explicar o save duplo vai quebrar o funcionamento.

**Correção:** A instrução deve dizer:
1. Manter o `if not self.pk: super().save()` (primeiro save para obter PK)
2. Mover apenas a lógica de cálculo de totais para o signal
3. O segundo `super().save()` no final deve ser removido (o signal já salva com `update_fields`)

---

### C4. T-4.3: `Planos.save()` grava histórico com string, não User

**Problema:** `Planos.save()` (linha 979-992) grava `PlanoHistorico` com `usuario=str(self.atividade_registro.equipe_projeto.equipe.nome)` — não recebe `request.user`. A tarefa diz "garantir que passa `usuario=request.user`" mas o `save()` não tem acesso ao request.

**Correção:** A tarefa deve explicar que:
1. O `Planos.save()` não tem acesso ao request — é chamado pelo formulário
2. A solução é passar o usuário via `Planos.save(usuario=request.user)` — mas `save()` hoje não aceita esse parâmetro
3. Precisa adicionar `usuario=None` como parâmetro opcional em `save()`, e usá-lo se fornecido, senão manter o fallback atual

---

### C5. T-5.3: Constantes transversais sem destino

**Problema:** `INDICADOR_TIPO_CHOICES`, `SCORE_PLANO`, `FOCO_CHOICES`, `REDE_TIPO_CHOICES`, `FUNDO_TIPO_CHOICES`, `PARCERIA_TIPO_CHOICES`, `PRODUTO_TIPO_CHOICES` são constantes definidas no corpo de `models.py` e usadas por models em múltiplos subdomínios. A tarefa não diz para onde vão.

**Correção:** Adicionar instrução:
1. Criar arquivo `src/ieb/constants.py` com todas as constantes transversais
2. Importar de `constants.py` em cada módulo que precisa
3. Re-exportar em `__init__.py` para compatibilidade

---

## Problema Alto (pode gerar código errado)

### A1. T-1.1: Justificativa do bug está errada

**Problema:** Diz "ignora campos com valor `0`" mas `0` é falsy em Python, e `sum(v for v in [0, 0] if v)` retorna `0` (correto). O bug real é que `None` é ignorado: `sum(v for v in [None, 2] if v)` retorna `2` (correto também). Na verdade o código atual funciona para os casos práticos.

**Correção:** A justificativa deve ser: "O `if v` filtra `None` E `0`. Se o usuário enviar `formacoes=0` intencionalmente, o `0` é ignorado na soma, mas isso é raro. A correção com `(v or 0)` é mais defensiva e explícita."

---

### A2. T-1.2: `Contratos.save()` sobrescreve default com None

**Problema:** `Contratos.save()` (linha 1171-1175) faz `self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']` — `aggregate` retorna `None` quando não há contratos com valor. Mesmo com `default=0`, o `save()` sobrescreve com `None`.

**Correção:** A tarefa deve incluir alteração no `save()`:
```python
# ANTES:
self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']
# DEPOIS:
self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total'] or 0
```

---

### A3. T-2.4: `DESAG_FIELDS` é lista, não dict

**Problema:** A tarefa diz adicionar `'org_governo': 'desag_org_governo'` mas `DESAG_FIELDS` (views.py:103-112) é uma **lista** de strings, não um dicionário. A instrução correta é adicionar `'desag_org_governo'` na lista.

**Correção:** 
```python
# ANTES:
DESAG_FIELDS = [
    'desag_homens', 'desag_mulheres', ...
]
# DEPOIS:
DESAG_FIELDS = [
    'desag_homens', 'desag_mulheres', ...,
    'desag_org_governo',  # NOVO
]
```

Também faltam instruções para:
- Adicionar campo no processamento POST (`elif field_name == 'org_governo': d['org_governo'] = _int(value)`)
- Adicionar campo no `indicadores_config['organizacoes']`
- Adicionar campo no admin fieldset de Organizações (tanto em `IndicadorAdmin` quanto em `IndicadorFinanciadorAdmin`)

---

### A4. T-4.1: Roll-up vago gera código macarrônico

**Problema:** A instrução de roll-up diz "adicionar lógica em `Meta.realizado`" com pseudocódigo vago (`valor_direto = ... # logica existente`). Um agente de IA vai tentar reescrever o método inteiro em vez de adicionar um bloco no final.

**Correção:** Dar instrução precisa:
1. NÃO reescrever o método `realizado` inteiro
2. Adicionar APENAS um bloco após o `return 0` final (que vira `return valor_direto`)
3. O bloco consulta `IndicadorFinanciador.objects.filter(equivalente_ieb=self.indicador)` e reutiliza o `SUM_MAP` existente
4. Somar ao valor direto e retornar

---

### A5. T-4.2: `max_length` errado

**Problema:** Diz `CharField(max_length=100)` mas o código real é `CharField(max_length=255)` (linha 815).

**Correção:** Atualizar para `max_length=255`.

---

### A6. T-4.6: `Outro` NÃO está no admin

**Problema:** A tarefa diz "Verificar se `admin.py` registra `Outro` e remover". Verificando o admin.py real, `Outro` **não está registrado** — não aparece em nenhum `admin.site.register()` ou `@admin.register()`.

**Correção:** Atualizar a instrução para dizer "Confirmar que `Outro` não está registrado no admin (verificado: não está). Nenhuma remoção necessária no admin."

---

### A7. T-B.1: `fin_planos_map` já não é necessário

**Problema:** A tarefa diz criar `fin_planos_map = {}` mas a lógica de processamento POST já usa `planos_map` para indicadores IEB. A correção correta é mais simples: remover `and not is_fin` e rotear para o map correto usando `is_fin`:

```python
# ANTES:
elif tipo == 'planos' and not is_fin:
    d = planos_map.setdefault(_id, {})

# DEPOIS:
elif tipo == 'planos':
    _m = fin_planos_map if is_fin else planos_map
    d = _m.setdefault(_id, {})
```

E adicionar a criação de `Planos` com `indicador_financiador` na seção de IndicadorFinanciador (espelhando o bloco de linhas 732-742).

---

## Problemas Médios (qualidade)

### M1. T-2.3: CheckConstraint com NULL em Postgres

**Problema:** `Q(homens__lte=F('total_pessoas')) | Q(homens__isnull=True)` — no Postgres, `NULL <= valor` avalia para `NULL` (não TRUE nem FALSE). A disjunção com `isnull=True` resolve, mas o teste de verificação deve incluir o caso `total_pessoas=0, homens=None` explicitamente.

**Correção:** Adicionar teste:
```python
Pessoas(total_pessoas=0, homens=None).save()  # OK (homens null é permitido)
Pessoas(total_pessoas=0, homens=1).save()     # IntegrityError (1 > 0)
```

---

### M2. T-5.1: Impacto em `Area.save()` e `AreasProtegidas.save()`

**Problema:** `Area.save()` usa `m2m.aggregate(s=models.Sum('area'))['s'] or 0.0` — o `0.0` é float. Com `DecimalField`, precisa ser `Decimal('0')`.

**Correção:** Adicionar instrução para atualizar o `or 0.0` para `or Decimal('0')` nos saves de `Area` e `AreasProtegidas`.

---

### M3. T-5.2: Save duplo em `AtividadeRegistroFoto`

**Problema:** O `save()` atual (linha 598-612) faz:
1. `super().save()` (salva a foto no disco)
2. Abre a imagem do caminho salvo
3. Gera thumbnail
4. `super().save(update_fields=['foto_thumbnail'])` (atualiza o campo)

A extração para Celery precisa preservar este padrão de "salvar primeiro, depois processar". A task precisa receber o PK (já salvo) e fazer o processamento.

**Correção:** Atualizar a instrução para dizer explicitamente:
1. O `save()` principal deve fazer apenas `super().save(*args, **kwargs)` e depois `gerar_thumbnail.delay(self.pk)`
2. A task Celery deve fazer todo o processamento de thumbnail (abrir, redimensionar, salvar)
3. A task deve chamar `foto.save(update_fields=['foto_thumbnail'])` no final

---

### M4. T-F.1: `FOCO_CHOICES` errado na documentação

**Problema:** A tarefa mostra `FOCO_CHOICES` com valores `governanca`, `subsistencia`, `monitoramento` mas o código real (linha 736-740) tem:
```python
FOCO_CHOICES = [
    ('implementacao', 'Implementação melhorada/monitoramento/vigilância'),
    ('ativ_prod',     'Meios de subsistência/cadeia de valor sustentáveis melhorados'),
    ('governanca',   'Fortalecimento institucional/capacitação organizacional/governança'),
]
```

**Correção:** Atualizar a documentação para refletir os valores reais.

---

## Resumo de Ações

| Prioridade | Quantidade | Ação |
|-----------|-----------|------|
| Crítico | 5 | Corrigir antes de qualquer execução |
| Alto | 7 | Corrigir para evitar código errado |
| Médio | 4 | Melhorar qualidade das instruções |
| **Total** | **16** | Correções necessárias |