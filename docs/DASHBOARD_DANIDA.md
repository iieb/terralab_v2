# Dashboard Danida — Documentação da Visualização

## Objetivo

O **Dashboard Danida** apresenta uma visão executiva do acompanhamento dos projetos vinculados ao escopo Danida no TerraLab. A visualização consolida informações de projetos, atividades, registros e metas para apoiar a leitura do andamento das ações e a identificação de prioridades de acompanhamento.

A página reúne filtros, cartões de resumo, gráficos, listas de prioridade e tabelas de detalhamento. Ela foi pensada como uma tela de leitura rápida para conversas com equipes e parceiros sobre o andamento do escopo Danida.

Referências técnicas principais:

- View principal: `codigo/terralab_v2/src/ieb/views.py:1073-1280`
- Template da visualização: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:310-708`

---

## Escopo monitorado

O dashboard considera projetos identificados como Danida. A seleção dos projetos é feita por uma consulta que procura o termo **"danida"** nos seguintes campos:

- sigla do financiador;
- nome do financiador;
- nome do projeto;
- nome fantasia do projeto.

Referência: `codigo/terralab_v2/src/ieb/views.py:1004-1010`

Os tipos de indicadores monitorados nesta etapa são:

- Pessoas;
- Organizações;
- Área;
- Fundos;
- Planos.

Referência: `codigo/terralab_v2/src/ieb/views.py:1000`

---

## Filtros disponíveis

A visualização permite refinar os dados exibidos por meio dos seguintes filtros:

### Projeto Danida

Restringe a visualização a um projeto específico. Quando nenhum projeto é selecionado, o dashboard considera todos os projetos Danida encontrados.

### Tipo de indicador

Restringe as metas a um tipo específico de indicador dentro do escopo monitorado.

### Atividade

Restringe registros e metas a uma atividade específica.

### Data inicial

Considera apenas registros e metas a partir da data informada.

### Data final

Considera apenas registros e metas até a data informada.

Referência da interface dos filtros: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:321-364`

Referência da aplicação dos filtros nas consultas: `codigo/terralab_v2/src/ieb/views.py:1115-1128`

---

## Recorte atual

A seção **Recorte atual** descreve quais filtros estão ativos na visualização. Ela informa:

- projeto selecionado;
- tipo de indicador selecionado;
- atividade selecionada;
- período filtrado.

Quando nenhum filtro é aplicado, a tela indica que está mostrando todos os projetos Danida, todos os tipos do escopo, todas as atividades e nenhum filtro de período.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:367-379`

---

## Cartões de resumo executivo

A seção de resumo apresenta os principais números do recorte atual.

### Projetos Danida

Quantidade de projetos Danida considerados no recorte atual.

### Registros de atividade

Total de registros de atividade encontrados no recorte atual.

### Metas no escopo

Quantidade de metas encontradas para os tipos de indicadores monitorados.

### Indicadores ativos

Quantidade de indicadores distintos associados às metas encontradas.

### Metas atingidas

Quantidade de metas cujo percentual de cumprimento é maior ou igual a 100%.

### Cumprimento das metas

Percentual de metas atingidas em relação ao total de metas do recorte.

Referência da interface: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:390-414`

Referência dos dados enviados para o template: `codigo/terralab_v2/src/ieb/views.py:1260-1267`

---

## Como o cumprimento das metas é calculado

Para cada meta individual, o dashboard calcula o percentual de cumprimento a partir da relação entre o valor realizado e o valor esperado da meta:

```text
percentual = realizado / meta * 100
```

Quando a meta não possui valor definido, ou quando o valor da meta é zero, o percentual considerado é `0`.

Referência: `codigo/terralab_v2/src/ieb/views.py:1172-1186`

---

## Status das metas

Cada meta recebe automaticamente um status de acompanhamento com base no seu percentual de cumprimento.

A classificação é definida pela função `_classificar_percentual_meta`.

Referência: `codigo/terralab_v2/src/ieb/views.py:1013-1018`

### Atingida

A meta é classificada como **Atingida** quando o percentual de cumprimento é maior ou igual a 100%.

```text
percentual >= 100%
```

### Em atenção

A meta é classificada como **Em atenção** quando o percentual de cumprimento está entre 70% e 99,9%.

```text
70% <= percentual < 100%
```

### Crítica

A meta é classificada como **Crítica** quando o percentual de cumprimento é menor que 70%.

```text
percentual < 70%
```

---

## O que significa a label "Crítica"

A label **"Crítica"** indica que uma meta está com cumprimento inferior a **70%** no recorte atual do dashboard.

Essa classificação não significa, por si só, que a meta esteja vencida, inválida ou incorreta. Ela indica que, considerando os filtros aplicados e os dados disponíveis, o avanço registrado está abaixo do limite mínimo definido para acompanhamento regular.

Em termos práticos, uma meta crítica deve ser interpretada como uma meta que precisa de atenção prioritária da equipe responsável.

Exemplo:

```text
Meta: 100
Realizado: 45
Percentual: 45%
Status: Crítica
```

Nesse exemplo, como o cumprimento é inferior a 70%, o dashboard exibe a meta como **Crítica**.

Observação importante: o prazo da meta é exibido no dashboard, mas ele não altera diretamente o status. A classificação **Crítica**, **Em atenção** ou **Atingida** é baseada apenas no percentual de cumprimento.

---

## Prioridades de acompanhamento

A seção **Prioridades de acompanhamento** destaca metas que exigem maior atenção no recorte atual.

Referência da interface: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:530-571`

### Metas críticas

A lista **Metas críticas** mostra até cinco metas classificadas como **Crítica**, ou seja, metas com cumprimento inferior a 70%.

Referência da seleção das metas críticas: `codigo/terralab_v2/src/ieb/views.py:1230`

Referência da exibição: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:532-549`

Cada item da lista mostra:

- nome do indicador;
- projeto;
- atividade;
- valor realizado;
- valor da meta;
- percentual de cumprimento;
- prazo;
- link para abrir as metas do projeto.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:536-543`

### Metas em atenção

A lista **Metas em atenção** mostra até cinco metas com cumprimento entre 70% e 99,9%.

Essas metas ainda não foram atingidas, mas estão acima do limite crítico.

Referência da seleção das metas em atenção: `codigo/terralab_v2/src/ieb/views.py:1231`

Referência da exibição: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:552-569`

---

## Ordem de prioridade das metas

As metas são ordenadas para destacar primeiro aquelas que exigem maior atenção.

A prioridade segue esta lógica:

1. metas críticas aparecem primeiro;
2. metas em atenção aparecem depois;
3. metas atingidas aparecem por último.

Referência da função de prioridade: `codigo/terralab_v2/src/ieb/views.py:1021-1026`

Além da prioridade por status, a ordenação também considera:

- percentual de cumprimento;
- data da meta;
- projeto;
- atividade;
- indicador.

Referência: `codigo/terralab_v2/src/ieb/views.py:1159-1170`

---

## Gráficos da visualização

### Temas com mais metas

Mostra como as metas estão distribuídas entre os tipos de indicadores acompanhados.

A leitura recomendada é: cada fatia da pizza representa a participação de um tema no conjunto total de metas.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:420-439`

### Projetos com mais registros

Mostra a participação de cada projeto no total de registros lançados.

A leitura recomendada é: cada fatia da pizza representa a participação de um projeto no total de registros.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:442-461`

### Como está o andamento por tema

Mostra o percentual de avanço das metas por tipo de indicador.

A leitura recomendada é: quanto maior a barra, maior o avanço acumulado das metas naquele tema.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:465-484`

### Onde houve mais registros

Mostra quais projetos possuem maior quantidade de registros de atividade.

A leitura recomendada é: quanto maior a barra, maior o número de registros lançados para o projeto.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:487-505`

### Quando houve mais movimento

Mostra os meses com maior número de registros de atividade.

A leitura recomendada é: quanto mais alta a coluna, maior o volume de registros naquele mês.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:508-526`

---

## Tabelas da visualização

### Consolidado de metas por tipo

A tabela **Consolidado de metas por tipo** agrupa as metas por tipo de indicador e apresenta:

- tipo;
- quantidade de metas;
- soma das metas;
- soma do realizado;
- percentual de cumprimento consolidado.

Referência da interface: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:573-601`

Referência do cálculo: `codigo/terralab_v2/src/ieb/views.py:1140-1157`

### Detalhamento das metas

A tabela **Detalhamento das metas** apresenta cada meta individualmente, com as seguintes informações:

- projeto;
- atividade;
- indicador;
- tipo;
- valor da meta;
- valor realizado;
- percentual de cumprimento;
- status;
- prazo;
- link para a tela de metas do projeto.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:603-645`

O status exibido nessa tabela é calculado automaticamente conforme as regras:

```text
Atingida: percentual >= 100%
Em atenção: percentual >= 70% e < 100%
Crítica: percentual < 70%
```

### Registros por projeto

A tabela **Registros por projeto** apresenta o total de registros de atividade agrupados por projeto.

Referência da interface: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:647-669`

Referência da consulta: `codigo/terralab_v2/src/ieb/views.py:1189-1202`

### Últimos registros

A seção **Últimos registros** exibe os registros de atividade mais recentes no recorte atual.

Ela mostra:

- data;
- projeto;
- atividade;
- responsável;
- links de navegação.

Referência: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:671-703`

Os registros são ordenados por data de início decrescente e, em seguida, por identificador.

Referência: `codigo/terralab_v2/src/ieb/views.py:1278`

---

## Observações importantes

- O status de uma meta depende dos filtros aplicados. Uma meta pode aparecer como crítica em um recorte específico e deixar de aparecer em outro recorte caso os filtros alterem o conjunto analisado.
- A classificação é baseada no percentual de cumprimento, não no prazo.
- O prazo é exibido para apoiar a análise, mas não altera diretamente o status da meta.
- Metas com valor zero ou sem valor definido recebem percentual `0` no dashboard e podem aparecer como críticas.
- A lista de metas críticas mostra no máximo cinco itens.
- A lista de metas em atenção mostra no máximo cinco itens.

Referências:

- Cálculo do percentual e status: `codigo/terralab_v2/src/ieb/views.py:1172-1186`
- Seleção de metas críticas e em atenção: `codigo/terralab_v2/src/ieb/views.py:1230-1231`
- Exibição do prazo nas prioridades: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:540`
- Exibição do prazo na tabela detalhada: `codigo/terralab_v2/src/ieb/templates/dash_danida.html:636`

---

## Leitura recomendada para usuários

Para usar o Dashboard Danida como ferramenta de acompanhamento executivo, recomenda-se a seguinte leitura:

1. Verificar o **recorte atual** para confirmar quais filtros estão aplicados.
2. Observar os **cartões de resumo** para entender o volume geral de projetos, registros, metas e indicadores.
3. Consultar os gráficos de **leitura rápida dos dados** para identificar distribuição de metas, registros e movimento por período.
4. Verificar a seção **Prioridades de acompanhamento**, especialmente as **Metas críticas**.
5. Usar a tabela **Detalhamento das metas** para entender quais metas estão críticas, em atenção ou atingidas.
6. Abrir a tela de metas do projeto quando for necessário investigar ou atualizar informações mais detalhadas.

A label **Crítica** deve ser entendida como um alerta de acompanhamento:

> Uma meta crítica é uma meta com menos de 70% de cumprimento no recorte atual e deve ser priorizada para análise, validação dos registros e acompanhamento pela equipe responsável.
