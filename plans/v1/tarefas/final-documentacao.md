# Final -- Documentacao de Contratos Transversais

> **Pre-requisito:** Todas as tarefas de implementacao concluidas.
> **Complexidade:** Baixa.
> **Revisado:** 2026-04-27 — correcao M4 aplicada.

---

## T-F.1: P2.8 -- Documentar `INDICADOR_TIPO_CHOICES` e `SCORE_PLANO` como contratos transversais

### Referencia no plano
P2.8 do Plano Cirurgico v1.3

### Problema
`INDICADOR_TIPO_CHOICES`, `SCORE_PLANO`, `SUM_MAP` e `FOCO_CHOICES` sao contratos transversais que impactam models, views, JS e admin. Qualquer alteracao nesses contratos tem efeito cascata, mas nao estao documentados no codigo.

### Arquivo
- `src/ieb/models.py` -- topo do arquivo (~linha 317-341)

### Alteracao
Adicionar docstring detalhada antes de cada contrato:

```python
# =============================================================================
# CONTRATOS TRANSVERSAIS
#
# Os contratos abaixo impactam MULTIPLOS ARQUIVOS. Alterar qualquer item
# requer atualizacao em todos os pontos listados.
#
# Arquivos impactados:
#   - models.py:   SUM_MAP (Meta.realizado, MetaFinanciador.realizado)
#   - views.py:    _atividade_registro_process, load_indicadores, indicadores_config, detail view
#   - admin.py:    IndicadorAdmin fieldsets, inlines
#   - script_v2.js: renderIndicador (renderizacao por tipo)
#   - signals.py:  m2m_changed receivers (se tipo usa M2M com recalculo)
# =============================================================================

INDICADOR_TIPO_CHOICES = [
    ('pessoas',           'Pessoas'),
    ('organizacoes',      'Organizacoes'),
    ('area',              'Area'),
    ('areas_protegidas',  'Areas Protegidas'),
    ('eventos',           'Eventos'),
    ('planos',            'Planos'),
    ('parcerias',         'Parcerias'),
    ('mobilizados',       'Recursos Mobilizados'),
    ('produtos',          'Produtos'),
    ('contratos',         'Contratos'),
    ('redes',             'Redes'),
    ('pequenos_projetos', 'Pequenos Projetos'),
    ('fundos',            'Fundos'),
    ('leis_politicas',    'Leis e Politicas'),
]
# NOTA: 'outro' foi removido (T-4.6). Se necessario re-adicionar:
# 1. Adicionar aqui
# 2. Criar model satelite
# 3. Adicionar ao SUM_MAP
# 4. Adicionar ao indicadores_config em views.py
# 5. Adicionar renderizacao em script_v2.js
# 6. Adicionar no admin


SCORE_PLANO = {
    'em desenvolvimento': 1,
    'proposto':           2,
    'adotado':            3,
    'em implementacao':   4,
    'implementado':       5,
}
# NOTA: Meta.base=1, Meta.meta=5. Alterar SCORE_PLANO requer ajuste
# em todas as Meta existentes e no dashboard.


FOCO_CHOICES = [
    ('governanca',     'Governanca'),
    ('implementacao',  'Implementacao'),
    ('ativ_prod',      'Atividades Produtivas'),
]
# NOTA: Usado por Pessoas e Organizacoes quando Indicador.tem_foco=True.
```

### Migration
Nenhuma (somente documentacao no codigo).

### Verificacao
- Abrir `models.py` e confirmar que os docstrings estao visiveis antes de cada contrato
- Verificar que a lista de arquivos impactados esta correta e completa

### Dependencias
Todas as tarefas de implementacao concluidas (para que a documentacao reflita o estado final).
