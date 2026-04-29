# Análise de Pontos Cegos — TerraLab v2

## Objetivo

Mapear todos os pontos cegos, inconsistências, riscos e lacunas no código e na documentação do projeto TerraLab v2, priorizados por impacto.

---

## 1. PROBLEMAS CRÍTICOS (Bug / Funcionalidade quebrada)

### 1.1 Arquivo JS referenciado no template v2 está em diretório errado
- **Template** `atividade_registro_form_v2.html:8` referencia `{% static 'ieb/css/form_v2.css' %}` e `:267` referencia `{% static 'ieb/js/script_v2.js' %}`
- Os arquivos **existem** em `src/terralab_v2/static/ieb/` (diretório do projeto), **NÃO** em `src/ieb/static/` (diretório da app)
- O `settings.py:80-83` configura `STATICFILES_DIRS` incluindo ambos os diretórios, então **funciona em dev** mas é uma inconsistência de organização que pode causar confusão em deploys que usam `collectstatic` com configurações diferentes

### 1.2 Template de detalhe usa variáveis que não são passadas pela view
- `atividade_registro_detalhe.html` referencia variáveis como `treinados`, `capacitados`, `aplicacao`, `area_geral`, `area_direto`, `area_restrito` (linhas 151, 159, 172, 189, 231, 242, 251)
- A view `atividade_registro_detalhe_view` (`views.py:133-156`) passa `pessoas`, `organizacoes`, `area`, `areas_protegidas` — **nomes completamente diferentes**
- **Impacto**: A seção de indicadores do template de detalhe **nunca renderiza** nenhum indicador. Essas variáveis são `None` e os blocos `{% if %}` falham silenciosamente
- O mesmo problema existe no template `atividade_registro_pdf.html` (linhas 279, 284, 295, 306, etc.)

### 1.3 `unique_together` conflitante em modelos de indicadores com `indicador` nullable
- Modelos como `Pessoas`, `Organizacoes`, `Area`, `AreasProtegidas`, `Evento`, `Outro`, `Leis`, `Parcerias`, `Produtos`, `Contratos`, `Mobilizados` usam `unique_together = ('atividade_registro', 'indicador')`
- Porém, `indicador` é `on_delete=SET_NULL, null=True, blank=True`
- Quando `indicador_financiador` é usado, `indicador` fica `NULL`, e **múltiplos registros do mesmo tipo para o mesmo `atividade_registro` com `indicador=NULL` violarão a constraint**
- O PostgreSQL trata `NULL != NULL` em unique constraints, mas o Django ORM pode gerar problemas dependendo do banco

### 1.4 Plano não suporta indicadores de financiador
- `views.py:638` — `elif tipo == 'planos' and not is_fin:` — planos de financiadores são **ignorados** no processamento do POST
- Não existe `fin_planos_map` ou processamento equivalente para `Planos` com `indicador_financiador`
- **Impacto**: Se um `IndicadorFinanciador` do tipo `planos` for criado, o formulário exibe os campos mas os dados são descartados no salvamento

### 1.5 Modelo não suporta indicadores de financiador
- `views.py` — Não existe `fin_modelos_map` nem processamento de modelos para financiadores
- O tipo `modelo` não está nem no `INDICADOR_TIPO_CHOICES`, mas `AtividadeRegistroModelo` existe no admin
- **Inconsistência**: O modelo `AtividadeRegistroModelo` usa `indicador` FK mas não tem `indicador_financiador` FK

---

## 2. PROBLEMAS DE SEGURANÇA

### 2.1 Views AJAX sem proteção CSRF
- `views.py:162` `adicionar_parceria` — sem `@csrf_exempt` mas também sem `{% csrf_token %}` no POST JSON
- `views.py:178` `adicionar_plano` — mesmo padrão
- `views.py:195` `atualizar_situacao_plano` — mesmo padrão
- `views.py:221` `adicionar_produto` — mesmo padrão
- `views.py:236` `adicionar_contrato` — mesmo padrão
- `views.py:261` `atualizar_estado_contrato` — mesmo padrão
- `views.py:280` `adicionar_lei` — usa `@csrf_exempt` explicitamente
- `views.py:303` `atualizar_situacao_lei` — usa `@csrf_exempt` explicitamente
- `views.py:331` `adicionar_modelo` — usa `@csrf_exempt` explicitamente
- **Impacto**: 6 views sem CSRF token, 3 com `@csrf_exempt` — todas aceitam POST sem verificação adequada

### 2.2 Views sem `@login_required`
- Apenas `load_indicadores` (`views.py:80`) tem `@login_required`
- Todas as outras views, incluindo `atividade_registro_view`, `atividade_registro_view_v2`, `monitoramento_metas_view`, `monitoramento_registros_view`, e todas as views de criação (adicionar_parceria, adicionar_plano, etc.) estão **abertas para usuários não autenticados**
- **Impacto**: Qualquer visitante anônimo pode criar registros de atividade, adicionar parcerias, leis, contratos, etc.

### 2.3 Validação de input insuficiente nas views AJAX
- Views como `adicionar_parceria`, `adicionar_plano`, `adicionar_produto`, `adicionar_contrato`, `adicionar_lei`, `adicionar_modelo` recebem JSON do POST e criam objetos diretamente sem validar permissões ou sanear o input
- `atualizar_situacao_plano`, `atualizar_estado_contrato`, `atualizar_situacao_lei` permitem alterações de estado sem verificar se o usuário tem permissão

---

## 3. PROBLEMAS DE PERFORMANCE

### 3.1 N+1 queries na view de metas
- `monitoramento_metas_view` (`views.py:1049-1107`) itera sobre cada `Meta` e `MetaFinanciador` chamando `.realizado` e `.percentual` que são **properties** com queries individuais
- Cada chamada a `realizado` faz 1-2 queries ao banco
- Para 100 metas, são ~200+ queries
- **Sugestão**: O próprio código tem um comentário em `models.py:458`: *"Uso pontual (detalhe de uma Meta). Para listagens, usar anotação na queryset."* — mas a view de monitoramento **não usa anotação**

### 3.2 N+1 queries na view de registros
- `monitoramento_registros_view` faz `qs.distinct()` após `select_related` mas sem `prefetch_related` para `equipe_projeto__equipe`, causando queries extras no template

### 3.3 `realizado` recalculado a cada acesso
- As properties `realizado` e `percentual` nos modelos `Meta` e `MetaFinanciador` não têm cache
- Se o template de detalhe acessar `realizado` mais de uma vez, a query é repetida

---

## 4. INCONSISTÊNCIAS ENTRE MODELO E CÓDIGO

### 4.1 `AreasProtegidas.unique_together` com `indicador` nullable
- `models.py:715` — `unique_together = ('atividade_registro', 'indicador')`
- Mesmo problema que 1.3: quando `indicador_financiador` é usado, `indicador` é NULL

### 4.2 `Contratos.save()` — `valor_total` pode ser `None`
- `models.py:1174` — `self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']`
- Se nenhum contrato tiver valor, o resultado é `None` (não 0), e o campo `valor_total` é `DecimalField(null=True, blank=True)` — funciona, mas é inconsistente com outros modelos que usam `default=0`

### 4.3 `desag_pct` em `Indicador` e `IndicadorFinanciador` não é usado
- O campo `desag_pct` existe nos dois modelos mas **não é referenciado** em nenhuma view, template ou JS
- Os campos específicos `desag_pct_indigenas`, `desag_pct_extrativistas`, `desag_pct_quilombolas` são usados no lugar

### 4.4 Nomenclatura inconsistente: `Meta` vs `MetaFinanciador` vs nome do model `Meta`
- O model `Meta` (models.py:445) conflita com o nome da classe interna `Meta` (Django `class Meta:`)
- Isso funciona em Python porque estão em escopos diferentes, mas é confuso para legibilidade

### 4.5 `AtividadeRegistro` sem `class Meta` para ordering
- `AtividadeRegistro` não define `ordering`, então a navegação anterior/próximo (`views.py:346-366`) usa `id__lt`/`id__gt` que pode não ser cronologicamente correto se registros forem inseridos fora de ordem

---

## 5. LACUNAS FUNCIONAIS

### 5.1 Sem edição de registros
- Não existe view ou URL para **editar** um `AtividadeRegistro` já salvo
- Não existe view para **excluir** registros
- **Impacto**: Erros em registros só podem ser corrigidos via admin do Django

### 5.2 Sem paginação
- `monitoramento_registros_view` e `monitoramento_metas_view` não usam paginação
- Com muitos registros, a página pode ficar lenta ou travar

### 5.3 Sem validação de `equipe_projeto` pertence ao projeto
- No formulário, o campo `equipe_projeto` é populado via AJAX baseado no projeto selecionado, mas no server-side (`forms.py`) não há validação de que a equipe selecionada realmente pertence ao projeto informado
- Um usuário malicioso pode manipular o POST para vincular uma equipe de outro projeto

### 5.4 Sem validação de que `atividade` pertence ao `componente`
- Mesmo problema: a cascata é client-side, mas o server-side não valida a consistência

### 5.5 E-mail de notificação sem tratamento robusto
- `views.py:867-870` — falha no envio de e-mail é capturada mas apenas logada com `print()`
- Se o e-mail falhar, o registro é salvo mas o usuário não é notificado da falha

### 5.6 Sem exportação de dados
- Não existe CSV/Excel export para os registros ou metas
- O PDF gerado usa o template antigo com variáveis incompatíveis (ver 1.2)

### 5.7 `LeiHistorico.usuario` e `PlanoHistorico.usuario` são `CharField`
- `models.py:815,1004` — ambos usam `CharField` em vez de `ForeignKey` para `User`
- Isso impede integridade referencial e torna difícil rastrear quem fez a alteração

---

## 6. PROBLEMAS DE DOCUMENTAÇÃO

### 6.1 `CLAUDE.md` com contagem de linhas desatualizada
- `CLAUDE.md:56` diz `~750 linhas` para `models.py`, mas o arquivo atual tem **1300 linhas**
- `CLAUDE.md:57` diz `~1400 linhas` para `views.py`, mas o arquivo atual tem **1109 linhas**

### 6.2 `README.md` genérico do GeoNode
- O README é o template padrão do GeoNode, sem nenhuma documentação específica do TerraLab
- Não documenta as funcionalidades do sistema, as URLs disponíveis, nem os modelos de dados
- Referencia `Django==3.2.16` em um trecho (`README.md:76`) enquanto o sistema usa Django 4.2

### 6.3 `GUIA_INDICADORES.md` — fluxo completo mas sem menção a modelos
- O guia documenta bem o fluxo operacional mas não menciona os modelos `Modelo` e `AtividadeRegistroModelo` que existem no código e admin

### 6.4 Sem documentação de API
- As views AJAX não estão documentadas (parâmetros, retorno, autenticação necessária)

---

## 7. DÍVIDA TÉCNICA

### 7.1 Código duplicado massivo
- `Indicador` e `IndicadorFinanciador` em `models.py` têm **campos idênticos** de desagregação (~30 campos booleanos duplicados)
- `Meta.realizado` e `MetaFinanciador.realizado` são **idênticos** exceto pelo FK (`indicador` vs `indicador_financiador`)
- A view `_atividade_registro_process` em `views.py` tem blocos quase idênticos para indicadores base e financiadores (~100 linhas duplicadas)

### 7.2 Sem testes
- `tests.py` está vazio (apenas o import de `TestCase`)
- Zero cobertura de testes para toda a lógica de negócio

### 7.3 `gis_models` importado mas não usado
- `models.py:5` — `from django.contrib.gis.db import models as gis_models` é importado mas nenhum modelo usa campos geográficos

### 7.4 `dev_config.yml` desatualizado
- `dev_config.yml:6-7` — Referências a `py2exe`, `pyproj`, `lxml` para Python 2.7, que são irrelevantes para Python 3.10

### 7.5 Comentários duplicados
- `models.py:3,9` — `# Create your models here.` aparece duas vezes

---

## RESUMO DE PRIORIZAÇÃO

| Prioridade | Categoria | Qtd | Itens mais urgentes |
|---|---|---|---|
| **P0 — Crítico** | Bug funcional | 5 | Templates de detalhe/PDF com variáveis erradas; Planos de financiador ignorados |
| **P1 — Alto** | Segurança | 3 | Views sem login_required; CSRF inconsistente; Validação de input |
| **P2 — Médio** | Performance | 3 | N+1 queries em metas; Sem paginação; Properties sem cache |
| **P3 — Baixo** | Consistência | 5 | unique_together com NULL; nomenclatura; campos não usados |
| **P4 — Melhoria** | Funcionalidade | 7 | Sem edição/exclusão; sem exportação; sem testes; código duplicado |
