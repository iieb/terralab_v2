# Bonus -- Correcao de Lacuna: Planos com IndicadorFinanciador

> **Pre-requisito:** Onda 2 concluida.
> **Paralelismo:** Independente. Pode rodar em paralelo com Onda 4.
> **Complexidade:** Baixa.
> **Origem:** Nao previsto no Plano Cirurgico v1.3 original. Identificado na analise do codigo.
> **Revisado:** 2026-04-27 — correcao A7 aplicada.

---

## T-B.1: Habilitar `Planos` para `IndicadorFinanciador` no formulario v2

### Problema
No processamento POST em `_atividade_registro_process` (`views.py:638`), a condicao para tipo `planos` exclui financiadores:

```python
elif tipo == 'planos' and not is_fin:
```

Isso significa que indicadores de financiador com tipo `planos` sao ignorados no formulario. O model `Planos` ja tem o campo `indicador_financiador` (adicionado na migration 0031), mas o formulario nao processa planos de financiador.

### Arquivos
- `src/ieb/views.py` -- `_atividade_registro_process` (~linha 638), `load_indicadores`, inicializacao de maps

### Alteracao

A abordagem deve seguir o roteamento ja existente em `_atividade_registro_process`, sem criar estruturas paralelas desnecessarias. Evitar duplicar blocos grandes.

1. **Remover restricao `and not is_fin`**:
```python
# ANTES:
elif tipo == 'planos' and not is_fin:

# DEPOIS:
elif tipo == 'planos':
```

2. **Reutilizar o mapa existente `planos_map`**, adicionando o marcador de origem (`is_fin`) em cada entrada. Nao criar `fin_planos_map` se o fluxo puder ser resolvido no mesmo mapa:
```python
planos_map[key] = {
    'plano_id': plano_id,
    'situacao_nova': situacao_nova,
    'is_fin': is_fin,
}
```

3. **Na secao de criacao de objetos**, rotear conforme `is_fin`:
```python
for key, data in planos_map.items():
    plano = Plano.objects.get(pk=data['plano_id'])
    kwargs = {
        'atividade_registro': registro,
        'plano': plano,
        'situacao_nova': data['situacao_nova'],
    }

    if data['is_fin']:
        kwargs['indicador_financiador'] = IndicadorFinanciador.objects.get(pk=key)
    else:
        kwargs['indicador'] = Indicador.objects.get(pk=key)

    Planos.objects.create(**kwargs)
    atualizar_situacao_plano(plano, data['situacao_nova'], request.user)
```

**Atencao:** confirmar o nome real do campo de situacao em `Planos` antes de editar. No model atual, a classe usa `situacao_nova`; nao usar `situacao` se o campo nao existir.

4. **Em `load_indicadores`**: Garantir que indicadores de financiador com tipo `planos` recebam `available_plans` no JSON de configuracao.

### Migration
Nenhuma (model ja tem o campo `indicador_financiador`).

### Verificacao
```python
# 1. Criar IndicadorFinanciador com tipo='planos'
fin = IndicadorFinanciador.objects.create(nome='Planos Financiador', tipo='planos', ...)

# 2. Vincular ao projeto
ProjetoIndicadorFin.objects.create(projeto=proj, indicador_financiador=fin)

# 3. Acessar formulario v2
# O indicador de financiador tipo 'planos' deve aparecer
# Deve ser possivel selecionar um Plano e uma situacao

# 4. Submeter formulario
# Planos deve ser criado com indicador_financiador preenchido
planos = Planos.objects.filter(indicador_financiador=fin)
assert planos.exists()

# 5. MetaFinanciador.realizado deve retornar o score do plano
meta_fin = MetaFinanciador.objects.get(indicador_financiador=fin, atividade=ativ)
assert meta_fin.realizado > 0
```

### Dependencias
Onda 2 concluida (constraints em `Planos` ja aplicadas).
