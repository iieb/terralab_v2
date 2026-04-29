# Replanejamento das Ondas Danida v2

## Contexto

Com base nas respostas do cliente em `plans/v2/2026-04-29-consulta-cliente-pontos-abertos-danida-v2.md`, a decisão central foi:

> **Todos os indicadores Danida serão `Indicador` (de projeto), não `IndicadorFinanciador`.**

Isso cancela as tarefas T-D2.3 (equivalente_ieb) e T-D2.5 (planos com financiador). As demais respostas simplificam Planos, Fundos, e definem nova semântica de FOCO_CHOICES.

**Arquivos principais afetados:**
- `src/ieb/models.py` — FOCO_CHOICES (l.812), Meta.realizado para planos (l.527), Fundo constraints (l.1026), Planos.save() (l.1087)
- `src/ieb/views.py` — autenticação (~l.44,133,471), CSRF (l.278,302,330), _foco_options, Meta.realizado
- `src/ieb/admin.py` — modelos satélite não registrados
- Templates: `atividade_registro_detalhe.html`, `atividade_registro_pdf.html`

---

## ONDA D1 — Correções bloqueantes antes de qualquer teste

### T-D1.1 — Adicionar `@login_required` nas views de escrita
**Arquivo:** `src/ieb/views.py`

Adicionar `@login_required` em:
- `atividade_registro_view` (~l.44)
- `atividade_registro_view_v2` (~l.471)
- `atividade_registro_detalhe_view` (~l.133)
- `adicionar_parceria` (~l.161)
- `adicionar_plano` (~l.177)
- `adicionar_produto` (~l.220)
- `adicionar_contrato` (~l.235)
- `monitoramento_registros_view` (~l.993)
- `monitoramento_metas_view` (~l.1029)

As views AJAX que já têm `@csrf_exempt` (`adicionar_lei` l.278, `atualizar_situacao_lei` l.302, `adicionar_modelo` l.330) recebem também `@login_required` acima do `@csrf_exempt`.

**Aceite:** `/atividade_registro/v2/` sem login → redirect para `/accounts/login/`. Admin acessa tudo.

---

### T-D1.2 — Verificar template `atividade_registro_detalhe.html`
**Arquivo:** `src/ieb/templates/atividade_registro_detalhe.html`

A view (l.133–155) já passa variáveis corretas: `pessoas`, `organizacoes`, `area`, `fundos`, `planos`, etc.
Verificar se o template usa essas variáveis ou nomes legados (ex: `treinados`, `capacitados`, `area_geral`).
Se houver nomes legados, substituir pelos nomes atuais do contexto da view.

**Aceite:** `/atividade/<pk>/` renderiza sem `AttributeError` e exibe os satélites corretamente.

---

## ONDA D2 — Correções de Domínio

### T-D2.1 — Substituir FOCO_CHOICES pelos 4 novos valores Danida
**Arquivo:** `src/ieb/models.py` (l.812–816) e `src/ieb/views.py` (`_foco_options`)

Substituir:
```python
FOCO_CHOICES = [
    ('soc_civil',          'Fortalecimento da sociedade civil'),
    ('gov_territorial',    'Governança Territorial e Ambiental'),
    ('defesa_direitos',    'Defesa de Direitos'),
    ('sociobiodiversidade','Economias da Sociobiodiversidade'),
]
```
Os valores antigos (`implementacao`, `ativ_prod`, `governanca`) têm max_length=20; os novos também cabem.
Gerar migration `AlterField` para `Pessoas.foco` e `Organizacoes.foco`.

Atualizar `_foco_options` em `views.py` para os 4 novos pares value/label.

**Aceite:** Formulário exibe os 4 novos focos. Admin mostra os novos choices.

---

### T-D2.2 — Corrigir Meta.realizado para tipo `planos` (contar atividades, não score)
**Arquivo:** `src/ieb/models.py` (l.527–532)

O bloco atual usa `SCORE_PLANO.get(ultimo.plano.situacao, 0)`. O cliente quer contar quantas atividades foram feitas para o plano.

Substituir o bloco `elif tipo == 'planos':` por:
```python
elif tipo == 'planos':
    valor_direto = Planos.objects.filter(
        atividade_registro__in=registros,
        indicador=self.indicador,
    ).count()
```

**Aceite:** Tela de monitoramento de metas exibe contagem de registros para indicadores de planos.

---

### T-D2.3 — Simplificar Planos satellite: remover histórico automático do save()
**Arquivo:** `src/ieb/models.py` (l.1066–1104) e `src/ieb/views.py` (~l.724–730)

O cliente quer apenas relacionar atividades a um plano e contar. O `Planos.save()` atual cria `PlanoHistorico` e atualiza `Plano.situacao` automaticamente — remover essa lógica.

Simplificar `Planos.save()` para apenas `super().save(*args, **kwargs)`.
Remover o parâmetro `usuario` da assinatura e da chamada em `views.py`.
Tornar `situacao_anterior` e `situacao_nova` campos `blank=True` (migration `AlterField`, não destrutivo).

**Aceite:** Criar um `Planos` via formulário não altera `Plano.situacao` nem gera `PlanoHistorico`.

---

### T-D2.4 — Simplificar Fundo: remover constraint `quantidade_min_1` e tornar campos opcionais
**Arquivo:** `src/ieb/models.py` (l.1026–1032)

O cliente quer apenas relacionar atividades ao fundo (contagem de atividades). A constraint `fundo_quantidade_min_1` bloqueia registros com `quantidade=0`.

Remover a constraint `fundo_quantidade_min_1` do `Meta.constraints`.
Alterar `quantidade` para `default=1, blank=True`.
Gerar migration.

No `views.py`, na seção que salva `Fundo`, garantir que `quantidade=1` seja o padrão se não informado.

**Aceite:** Criar um registro com indicador `fundos` não exige preencher quantidade. `Fundo.objects.filter(indicador=x).count()` retorna contagem correta.

---

### T-D2.5 — Verificar e limpar tipo `outro` de INDICADOR_TIPO_CHOICES
**Arquivo:** `src/ieb/models.py`

Verificar se `'outro'` ainda aparece em `INDICADOR_TIPO_CHOICES`. Se sim, remover a entrada e gerar migration `AlterField` no campo `tipo` de `Indicador` e `IndicadorFinanciador`.
O `'Outro'` em `Plano.TIPO_CHOICES` (l.1046) é intencional — manter.

**Aceite:** `python manage.py shell -c "from ieb.models import INDICADOR_TIPO_CHOICES; print(INDICADOR_TIPO_CHOICES)"` não lista `outro`.

---

### T-D2.6 — Registrar modelos satélite sem cobertura no Admin
**Arquivo:** `src/ieb/admin.py`

Adicionar registros simples para os modelos que não estão no admin:
```python
admin.site.register(Fundo)
admin.site.register(Evento)
admin.site.register(Area)
admin.site.register(AreasProtegidas)
admin.site.register(Organizacoes)
```

**Aceite:** Admin Django exibe `Fundo`, `Evento`, `Area`, `AreasProtegidas`, `Organizacoes` como seções navegáveis.

---

## ONDA D3 — Templates e Apresentação

### T-D3.1 — Template detalhe: formatação formal, sem ícones de AI
**Arquivo:** `src/ieb/templates/atividade_registro_detalhe.html`

Substituir todos os ícones HTML entities (ex: `&#128221;`, `&#128247;`) por labels de texto simples em negrito ou por um símbolo neutro (`•` ou `▸`).
Aplicar estilo de relatório institucional: fundo branco, tabelas com bordas simples, sem gradientes ou cores vivas.

**Aceite:** A página de detalhe não exibe nenhum emoji. Visual é compatível com relatório institucional.

---

### T-D3.2 — Template PDF: mesma formatação formal
**Arquivo:** `src/ieb/templates/atividade_registro_pdf.html`

Mesmas correções de T-D3.1: remover HTML entities de emoji, usar texto para títulos de seção.
Verificar que o template usa as variáveis corretas do contexto passado pelo gerador de PDF.

**Aceite:** PDF gerado não exibe caixas de caractere inválido. Títulos de seção legíveis como texto.

---

## ONDA D4 — Dados e Homologação (sem código)

### T-D4.1 — Cadastrar os 14 indicadores Danida no Admin como `Indicador`
Criar cada indicador com tipo correto, flags `desag_*` marcados conforme A.2:
- Indicadores de `pessoas`: marcar `desag_homens`, `desag_mulheres`, `desag_jovens`, `desag_pct_indigenas`.
- Vincular ao Projeto Danida via `ProjetoIndicador`.

### T-D4.2 — Criar estrutura do Projeto Danida no Admin
Criar: `Financiador` Danida → `Projeto` → `Componente`(s) → `Atividade`(s) → `Meta`(s) → `EquipeProjeto`.

### T-D4.3 — Smoke test ponta a ponta
1. Login como admin → abrir formulário v2.
2. Preencher atividade com indicador `pessoas` (desag homens/mulheres/jovens/indigenas).
3. Verificar detalhe da atividade exibe os dados.
4. Verificar monitoramento de metas atualiza o realizado.
5. Gerar PDF → sem caixas de caractere inválido.

---

## Backlog pós-Danida

| ID | Descrição | Decisão origem |
|----|-----------|----------------|
| B-01 | Reformular model `TIs` com campo geométrico (PostGIS) para cálculo automático de área | A.4 |
| B-02 | Após B-01: garantir que signal `area_m2m_changed` usa área real do PostGIS | B.3 |
| B-03 | Atualizar `docker-compose.yml` conforme repositório oficial GeoNode | E.3 |
| B-04 | Implementar `equivalente_ieb` (roll-up IEB) quando houver discussão institucional sobre macro-indicadores | A.7 |
| B-05 | Adicionar `@login_required` + remover `@csrf_exempt` de `adicionar_lei`/`atualizar_situacao_lei` quando Leis for reativado | B.1/C.2 |

---

## Sequência de implementação recomendada

```
T-D1.1 (login_required)
T-D1.2 (verificar template detalhe)
T-D2.1 (FOCO_CHOICES + migration)
T-D2.2 (Meta.realizado planos)
T-D2.3 (Planos.save simplificado + migration)
T-D2.4 (Fundo constraints + migration)
T-D2.5 (limpar tipo outro)
T-D2.6 (admin)
T-D3.1 + T-D3.2 (templates — podem rodar em paralelo com migrations)
T-D4.1 + T-D4.2 (dados no admin)
T-D4.3 (smoke test)
```

## Tarefas canceladas (pelo cliente)

| Tarefa original | Motivo do cancelamento |
|-----------------|----------------------|
| T-D2.3 (equivalente_ieb) | Sem roll-up IEB por ora (A.7) |
| T-D2.5 (Planos com IndicadorFinanciador) | Todos indicadores são de projeto (A.1) |
| T-D2.7 (Organizacoes + org_governo) | Campos existentes são suficientes (C.4) |
| T-D2.8 (sinais M2M Area/TIs) | TIs precisa reformulação geográfica primeiro (A.4 → B-01) |
| T-D2.2 (históricos com Equipe) | Leis não serão usadas; Planos simplificado (C.2) |
| Testes automatizados (C.5) | Homologação manual suficiente para esta entrega |
