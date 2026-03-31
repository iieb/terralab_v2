# Guia de Indicadores e Projetos — TerraLab v2

## Para quem é este guia?

Para qualquer pessoa que precise cadastrar um novo projeto, vincular indicadores ou registrar resultados de atividades no sistema. Não é necessário conhecimento técnico.

---

## Como o sistema está organizado

O sistema segue uma hierarquia simples:

```
Programa
 └── Projeto
      └── Componente
           └── Atividade
                └── Registro de Atividade  ← onde os resultados são lançados
```

- **Programa** — estratégia ou linha de atuação geral (ex: "Proteção Territorial")
- **Projeto** — iniciativa específica com financiadores e metas (ex: "Projeto Xingu 2024–2027")
- **Componente** — divisão interna do projeto, geralmente por tema ou executor
- **Atividade** — ação concreta executada dentro de um componente (ex: "Oficina de Mapeamento")
- **Registro de Atividade** — o formulário preenchido após uma atividade acontecer, com datas, participantes e resultados

Um projeto pode ter subprojetos, permitindo agrupar iniciativas menores sob um guarda-chuva maior.

---

## O que é um Indicador?

Um **indicador** mede o resultado ou impacto de um projeto. Ele responde à pergunta: *"O que estamos contando ou monitorando?"*

O sistema tem dois tipos de indicadores:

| Tipo | Para quem é? | Exemplo |
|---|---|---|
| **Indicador institucional** | Metas internas do IEB | "Nº de indígenas formados em gestão territorial" |
| **Indicador do financiador** | Exigência de quem financia | "Number of beneficiaries (USAID)" |

Os dois tipos funcionam da mesma forma — a diferença é que o indicador do financiador fica associado a um financiador específico e pode ter código e nomenclatura próprios daquele parceiro.

---

## Tipos de indicador

Cada indicador tem um **tipo**, que define o que ele mede e quais campos aparecerão no formulário de registro. Os tipos disponíveis são:

| Tipo | O que mede | Exemplo de nome do indicador |
|---|---|---|
| **Pessoas** | Quantidade de pessoas beneficiadas | "Indígenas capacitados em vigilância territorial" |
| **Organizações** | Quantidade de organizações fortalecidas | "Organizações indígenas apoiadas" |
| **Área** | Hectares de território sob influência | "Área com manejo sustentável (ha)" |
| **Áreas Protegidas** | Número de unidades (TIs, UCs, PAs, TUCs) | "Terras Indígenas com plano de gestão" |
| **Eventos** | Formações, seminários, encontros, reuniões | "Eventos de formação realizados" |
| **Planos** | Avanço de um plano (PGTA, Plano de Manejo…) | "PGTA aprovado e em implementação" |
| **Parcerias** | Quantidade de parcerias firmadas | "Parcerias institucionais estabelecidas" |
| **Recursos Mobilizados** | Valor financeiro captado ou mobilizado | "Recursos mobilizados de contrapartida (R$)" |
| **Produtos** | Publicações, relatórios, cartilhas | "Publicações produzidas e distribuídas" |
| **Contratos** | Contratos formalizados | "Contratos com prestadores locais" |
| **Redes** | Redes articuladas (local, regional, nacional) | "Redes de vigilância territorial articuladas" |
| **Pequenos Projetos** | Projetos de pequena escala apoiados | "Pequenos projetos comunitários financiados" |
| **Fundos** | Fundos constituídos ou aportados | "Fundos ambientais estruturados" |
| **Leis e Políticas** | Normas em tramitação ou implementadas | "Políticas públicas influenciadas" |
| **Outro** | Qualquer resultado que não se encaixe acima | (uso livre) |

> **Regra importante:** o *tipo* define a *estrutura* do que é medido. O *nome* do indicador define o *conteúdo*. Um mesmo tipo pode aparecer em vários indicadores diferentes de um projeto.

---

## Desagregações: o que são?

Quando você cadastra um indicador, pode habilitar **desagregações** — campos opcionais que aparecem no formulário de registro para detalhar o resultado.

Por exemplo, para um indicador do tipo **Pessoas**, você pode habilitar:
- Registrar quantos são homens / mulheres / jovens
- Registrar percentual de indígenas, extrativistas ou quilombolas
- Registrar se há servidores públicos entre os participantes
- Registrar o foco da ação (governança, subsistência, monitoramento)

Para **Área**, você pode habilitar:
- Área restrita (HA digitado manualmente)
- Área de influência direta (seleção de Terras Indígenas, UCs, PAs ou TUCs)
- Área de influência indireta (idem)

As desagregações **não são obrigatórias** — se não forem habilitadas, o formulário mostra apenas o campo principal (ex: total de pessoas).

---

## Como cadastrar um novo projeto

### Passo 1 — Cadastrar o projeto

Acesse o **Admin → IEB → Projetos** e crie um novo projeto com:
- **Nome fantasia** — nome curto e operacional (aparece nos relatórios)
- **Nome** — nome completo e oficial
- **Programas** — selecione os programas aos quais o projeto pertence
- **Financiadores** — selecione os financiadores do projeto

Se for um subprojeto, preencha o campo **Projeto pai**.

### Passo 2 — Criar Componentes

Dentro do projeto, crie os componentes (abas de execução, temas, ou parceiros executores).

### Passo 3 — Criar Atividades

Dentro de cada componente, crie as atividades que serão executadas.

### Passo 4 — Vincular Indicadores ao Projeto

Os indicadores precisam ser **vinculados ao projeto** antes de serem usados.

**Para indicadores institucionais:**
Admin → IEB → Projetos → (seu projeto) → seção *Indicadores do projeto* → adicione os indicadores desejados.

**Para indicadores de financiador:**
Admin → IEB → Projetos → (seu projeto) → seção *Indicadores do Financiador* → adicione os indicadores do financiador.

> Cada indicador só aparece no formulário de registro se estiver vinculado ao projeto.

### Passo 5 — Definir Metas por Atividade

Para cada atividade, defina a meta de cada indicador:

Admin → IEB → Metas → criar nova meta com:
- **Atividade** — a atividade a que a meta se refere
- **Indicador** — qual indicador está sendo monitorado
- **Base** — valor de partida (linha de base)
- **Meta** — valor a ser alcançado
- **Prazo** — data limite
- **Início do período** *(opcional)* — se preenchido, o sistema só conta registros dentro deste intervalo de datas

---

## Como cadastrar um novo indicador

Acesse **Admin → IEB → Indicadores** e crie um novo indicador:

1. **Nome** — nome descritivo do que está sendo medido
2. **Código** — código interno (ex: "IND-01")
3. **Tipo** — escolha o tipo que melhor descreve o resultado (ver tabela acima)
4. **Reporte** — com que frequência o resultado deve ser reportado
5. **Desagregações** *(opcional)* — habilite apenas os campos que forem necessários para este indicador

Depois de criado, vincule o indicador aos projetos onde ele será usado (Passo 4 acima).

---

## Como registrar um resultado (Registro de Atividade)

Após executar uma atividade, acesse o formulário de registro em:

`/ieb/atividade_registro/v2/`

O formulário pede:

1. **Projeto / Componente / Atividade** — seleção encadeada
2. **Datas e localização** — quando e onde aconteceu
3. **Descrição, desafios, propostas** — narrativa da atividade
4. **Resultados por indicador** — para cada indicador vinculado à atividade, o formulário exibe campos específicos conforme o tipo e as desagregações habilitadas

O sistema calcula automaticamente o total de cada indicador e atualiza o percentual de cumprimento das metas.

---

## Como o sistema calcula o "realizado" de uma meta

O campo **Realizado** de uma meta é calculado automaticamente:

1. O sistema busca todos os Registros de Atividade da atividade
2. Para cada registro, soma o campo principal do tipo de indicador (ex: `total_pessoas` para tipo Pessoas, `total_ha` para tipo Área)
3. Divide pelo valor da meta para calcular o percentual

**Caso especial — Planos:** o sistema não soma, mas pontua o estado atual do plano em uma escala de 1 a 5:

| Situação | Pontuação |
|---|---|
| Em desenvolvimento | 1 |
| Proposto | 2 |
| Adotado | 3 |
| Em implementação | 4 |
| Implementado | 5 |

**Filtro por período:** se a meta tiver um *Início do período* preenchido, o sistema só considera registros com data dentro do intervalo definido.

---

## Diferença entre Área e Áreas Protegidas

É comum confundir esses dois tipos:

| Tipo | O que mede | Como mede |
|---|---|---|
| **Área** | Extensão territorial em hectares | Ha digitados manualmente (modo restrito) *ou* seleção de TIs/UCs/PAs/TUCs com soma automática dos hectares |
| **Áreas Protegidas** | Quantidade de unidades de conservação, TIs, PAs ou TUCs | Conta o número de unidades selecionadas (não mede hectares) |

Use **Área** quando a meta for em hectares.
Use **Áreas Protegidas** quando a meta for em número de territórios ou unidades.

---

## Indicadores de Financiador

Alguns financiadores (USAID, GEF, etc.) exigem reportar resultados com nomenclaturas e métricas próprias. Para isso existe o **Indicador do Financiador**.

Ele funciona exatamente igual ao indicador institucional, mas:
- Está associado a um financiador específico
- Pode ter nome, código e descrição no idioma/formato exigido pelo parceiro
- Aparece separado no dashboard de metas (coluna "Financiador")
- A meta é registrada em **MetaFinanciador**, não em Meta

Para criar um indicador de financiador:
Admin → IEB → Financiadores → (seu financiador) → seção *Indicadores* → adicione os indicadores.

Depois vincule ao projeto via *Indicadores do Financiador* no cadastro do projeto.

---

## Resumo visual do fluxo completo

```
[1] Criar Financiador(es)         [1] Criar Indicadores institucionais
         │                                    │
[2] Criar IndicadorFinanciador                │
         │                                    │
         └──────────── [3] Criar Projeto ─────┘
                              │
                    (vincular indicadores + definir metas)
                              │
                    [4] Criar Componentes
                              │
                    [5] Criar Atividades
                              │
                    [6] Definir Meta por Atividade + Indicador
                              │
                    [7] Executar atividade
                              │
                    [8] Lançar Registro de Atividade (v2)
                              │
                    [9] Dashboard atualiza Realizado / %
```

---

## Perguntas frequentes

**Posso usar o mesmo indicador em vários projetos?**
Sim. O indicador é cadastrado uma vez e vinculado a quantos projetos forem necessários.

**E se dois indicadores do mesmo projeto tiverem o mesmo tipo?**
Sem problema. O tipo define apenas a estrutura do formulário. O nome diferencia os indicadores.

**O que acontece se registrar uma atividade sem vincular um indicador?**
O registro é salvo normalmente, mas não será contabilizado em nenhuma meta.

**Posso registrar resultados de indicadores de financiador e institucionais no mesmo formulário?**
Sim. O formulário v2 exibe todos os indicadores ativos para aquela atividade — institucionais e de financiadores — em seções separadas.

**Um projeto pode estar em mais de um programa?**
Sim. A associação é muitos-para-muitos.
