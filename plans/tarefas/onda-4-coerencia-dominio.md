# Onda 4 -- Coerencia de Dominio

> **Pre-requisito:** Onda 2 concluida (para T-4.4 e T-4.7). Ondas 0-1 recomendadas.
> **Paralelismo:** T-4.1, T-4.2, T-4.3, T-4.5, T-4.6 sao independentes. T-4.4 e T-4.7 dependem da Onda 2.
> **Complexidade:** Baixa (T-4.2, T-4.3, T-4.6) a ALTA (T-4.5).
> **Revisado:** 2026-04-27 — correcoes C4, A4, A5, A6 aplicadas.

---

## T-4.1: P0.1 -- `equivalente_ieb` FK em `IndicadorFinanciador`

### Referencia no plano
P0.1 do Plano Cirurgico v1.3

### Problema
Quando um financiador exige indicador similar ao IEB, e necessario registrar duas vezes ou a contagem fica separada. Nao ha roll-up automatico.

### Arquivos
- `src/ieb/models.py` -- classe `IndicadorFinanciador` (~linha 391-443)
- `src/ieb/views.py` -- `MetaFinanciador.realizado` e possivelmente `load_indicadores`
- `src/ieb/admin.py` -- `IndicadorFinanciadorAdmin` fieldsets

### Alteracao

1. **Model `IndicadorFinanciador`**: Adicionar campo:
```python
equivalente_ieb = models.ForeignKey(
    'Indicador', on_delete=models.SET_NULL, null=True, blank=True,
    verbose_name='Indicador IEB equivalente',
    help_text='Quando preenchido, os resultados deste indicador de financiador '
              'sao contabilizados tambem no indicador IEB equivalente.',
)
```

2. **`Meta.realizado`** (models.py ~linha 456-500): o roll-up deve acontecer no indicador IEB, nao duplicando registros. **NAO reescrever o metodo `realizado` inteiro.** A alteracao deve ser cirurgica:
   - preservar a logica atual de `SUM_MAP`, `COUNT_MAP` e `planos`;
   - transformar os retornos diretos em atribuicoes a `valor_direto` quando necessario;
   - adicionar um bloco antes do retorno final que consulta `IndicadorFinanciador.objects.filter(equivalente_ieb=self.indicador)`;
   - reutilizar `SUM_MAP`/`COUNT_MAP` para somar resultados de financiadores equivalentes.

```python
# Padrao esperado (adaptar sem reescrever o metodo inteiro):
valor_direto = 0

if tipo in SUM_MAP:
    Model, field = SUM_MAP[tipo]
    result = Model.objects.filter(
        atividade_registro__in=registros,
        indicador=self.indicador,
    ).aggregate(total=Sum(field))
    valor_direto = result['total'] or 0
elif tipo in COUNT_MAP:
    valor_direto = COUNT_MAP[tipo].objects.filter(
        atividade_registro__in=registros,
        indicador=self.indicador,
    ).count()
elif tipo == 'planos':
    # manter a logica atual de SCORE_PLANO e atribuir em valor_direto
    ...

valor_financiadores = 0
for fin in IndicadorFinanciador.objects.filter(equivalente_ieb=self.indicador):
    fin_tipo = fin.tipo
    if fin_tipo in SUM_MAP:
        Model, field = SUM_MAP[fin_tipo]
        result = Model.objects.filter(
            atividade_registro__in=registros,
            indicador_financiador=fin,
        ).aggregate(total=Sum(field))
        valor_financiadores += result['total'] or 0
    elif fin_tipo in COUNT_MAP:
        valor_financiadores += COUNT_MAP[fin_tipo].objects.filter(
            atividade_registro__in=registros,
            indicador_financiador=fin,
        ).count()

return valor_direto + valor_financiadores
```

3. **Admin**: Adicionar `equivalente_ieb` nos fieldsets de `IndicadorFinanciadorAdmin`.

### Migration
```python
operations = [
    migrations.AddField(
        'indicadorfinanciador', 'equivalente_ieb',
        field=models.ForeignKey('Indicador', SET_NULL, null=True, blank=True, ...),
    ),
]
```

### Verificacao
```python
# Criar indicador IEB e financiador equivalente
ind = Indicador.objects.create(nome='Pessoas', tipo='pessoas')
fin = IndicadorFinanciador.objects.create(nome='Beneficiaries', tipo='pessoas', equivalente_ieb=ind)

# Registrar resultado via financiador
# No dashboard de metas IEB, os valores do financiador devem aparecer consolidados
```

### Dependencias
Nenhuma (independente).

---

## T-4.2: P1.2 -- `LeiHistorico.usuario` -> FK para `User`

### Referencia no plano
P1.2 do Plano Cirurgico v1.3

### Problema
`LeiHistorico.usuario` e um `CharField(max_length=255)` (texto livre), nao uma FK para `auth.User`.

### Arquivos
- `src/ieb/models.py` -- classe `LeiHistorico` (~linha 810-818)
- `src/ieb/views.py` -- `atualizar_situacao_lei` (~linha 319-324)

### Alteracao

1. **Model `LeiHistorico`**:
```python
# ANTES:
usuario = models.CharField(max_length=255, verbose_name='Usuario')

# DEPOIS:
usuario = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
    null=True, blank=True, verbose_name='Usuario',
)
```

2. **Views `atualizar_situacao_lei`**: O codigo atual usa `usuario=request.user.username` (string). Apos mudar para FK, trocar para `usuario=request.user` (objeto User):
```python
# ANTES:
LeiHistorico.objects.create(..., usuario=request.user.username)

# DEPOIS:
LeiHistorico.objects.create(..., usuario=request.user)
```

### Migration
```python
operations = [
    # Data migration: converter nomes para IDs se possivel
    # Depois:
    migrations.AlterField(
        'leihistorico', 'usuario',
        field=models.ForeignKey(settings.AUTH_USER_MODEL, SET_NULL, null=True, blank=True),
    ),
]
```

### Atencao
Se existem registros com `usuario` como string (nome do usuario), criar data migration para tentar resolver para FK. Se nao for possivel, setar como `null`.

### Verificacao
```python
# Alterar situacao de lei via view
# Verificar que LeiHistorico.usuario e uma FK para User
hist = LeiHistorico.objects.latest('id')
hist.usuario  # <User: ...> (nao string)
```

### Dependencias
Nenhuma (independente).

---

## T-4.3: P1.3 + P1.4 -- `PlanoHistorico.usuario` -> FK + historico condicional

### Referencia no plano
P1.3 + P1.4 do Plano Cirurgico v1.3

### Problema
1. `PlanoHistorico.usuario` e `CharField(max_length=255)` (igual a LeiHistorico)
2. O `Planos.save()` atual ja possui logica condicional (`if plano and not self.pk`) e cria historico somente na criacao e somente quando a situacao muda. O foco desta tarefa e converter `usuario` para FK sem reescrever a logica inteira.

### Arquivos
- `src/ieb/models.py` -- classe `PlanoHistorico` (~linha 961-1007) e `Planos`
- `src/ieb/views.py` -- `atualizar_situacao_plano` (~linha 195-218)

### Alteracao

1. **Model `PlanoHistorico`**: Trocar `usuario` para FK (mesmo padrao de T-4.2):
```python
# ANTES:
usuario = models.CharField(max_length=255, verbose_name='Usuario')

# DEPOIS:
usuario = models.ForeignKey(
    settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
    null=True, blank=True, verbose_name='Usuario',
)
```

2. **Model `Planos.save()`**: o metodo atual (models.py ~linha 979-992) nao tem acesso ao `request` e usa `usuario=str(self.atividade_registro.equipe_projeto.equipe.nome)`. Apos mudar `PlanoHistorico.usuario` para FK, essa string nao e valida. Solucao: adicionar `usuario=None` como parametro opcional ao `save()` e usar esse objeto quando fornecido pela view; se nao houver usuario, gravar `None`.

```python
def save(self, *args, usuario=None, **kwargs):
    plano = self.plano
    if plano and not self.pk:  # manter a logica condicional existente
        self.situacao_anterior = plano.situacao
        if plano.situacao != self.situacao_nova:
            PlanoHistorico.objects.create(
                plano=plano,
                situacao_anterior=plano.situacao,
                situacao_nova=self.situacao_nova,
                usuario=usuario,  # FK: objeto User ou None
            )
            plano.situacao = self.situacao_nova
            plano.save(update_fields=['situacao'])
    super().save(*args, **kwargs)
```

3. **Views `atualizar_situacao_plano`**: o codigo atual usa `usuario=request.user.username` (string). Apos mudar para FK, trocar para `usuario=request.user` (objeto User).

### Migration
```python
operations = [
    # Data migration para converter strings
    migrations.AlterField('planohistorico', 'usuario', field=...),
]
```

### Verificacao
```python
# Salvar Planos sem mudar situacao -> sem entrada nova no historico
p = Planos.objects.first()
p.save()
PlanoHistorico.objects.filter(plano=p.plano).count()  # Mesmo count de antes

# Mudar situacao -> entrada criada com FK para User
p.situacao_nova = 'adotado'
p.save(usuario=request.user)
hist = PlanoHistorico.objects.filter(plano=p.plano).latest('id')
hist.usuario  # <User: ...> (nao string)
```

### Dependencias
Nenhuma (independente).

---

## T-4.4: P1.12 -- Constraints em `PequenoProjeto` e `Fundo`

### Referencia no plano
P1.12 do Plano Cirurgico v1.3

### Problema
`PequenoProjeto` e `Fundo` permitem `quantidade=0` e `valor_total=None`.

### Arquivo
- `src/ieb/models.py` -- `PequenoProjeto` (~linha 880-895) e `Fundo` (~linha 906-916)

### Alteracao

1. **Ambos models**: Adicionar constraint:
```python
constraints = [
    # ... constraints de T-2.2 ...
    models.CheckConstraint(
        check=models.Q(quantidade__gte=1),
        name='%(class)s_quantidade_min_1',
    ),
]
```

2. **Ambos models**: Tornar `valor_total` obrigatorio:
```python
# ANTES:
valor_total = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

# DEPOIS:
valor_total = DecimalField(max_digits=15, decimal_places=2, default=0)
```

### Migration
```python
operations = [
    # Data migration: setar valor_total=0 onde e None
    migrations.RunSQL(
        "UPDATE ieb_pequenoprojeto SET valor_total = 0 WHERE valor_total IS NULL",
        "UPDATE ieb_pequenoprojeto SET valor_total = 0 WHERE valor_total IS NULL",
    ),
    migrations.RunSQL(
        "UPDATE ieb_fundo SET valor_total = 0 WHERE valor_total IS NULL",
        "UPDATE ieb_fundo SET valor_total = 0 WHERE valor_total IS NULL",
    ),
    migrations.AlterField('pequenoprojeto', 'valor_total', ...),
    migrations.AlterField('fundo', 'valor_total', ...),
    migrations.AddConstraint('pequenoprojeto', ...),
    migrations.AddConstraint('fundo', ...),
]
```

### Verificacao
```python
PequenoProjeto(quantidade=0, ...).save()  # IntegrityError
PequenoProjeto(quantidade=1, valor_total=0, ...).save()  # OK
```

### Dependencias
Onda 2 concluida (constraints de T-2.2 ja aplicadas).

---

## T-4.5: P1.13 -- Redesenho de `Rede` (entidade cadastral + tabela de ligacao)

### Referencia no plano
P1.13 do Plano Cirurgico v1.3

### Complexidade
**ALTA** -- usar planejamento com agente `muse` antes de executar com `forge`.

### Problema
`Rede` atual e um model satelite simples com `nome`, `tipo`, `quantidade` vinculado a `AtividadeRegistro`. A mesma rede pode ser referenciada por multiplas atividades, mas hoje cada referencia cria um novo registro.

### Arquivos
- `src/ieb/models.py` -- classe `Rede` (~linha 860-878)
- `src/ieb/views.py` -- `load_indicadores`, `_atividade_registro_process`, detail view, email
- `src/ieb/admin.py` -- registro de `Rede`
- `src/terralab_v2/static/ieb/js/script_v2.js` -- renderizacao do tipo `redes`

### Alteracao proposta

1. **Transformar `Rede` em entidade cadastral** (sem FK para AtividadeRegistro):
```python
class Rede(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    tipo = models.CharField(max_length=50, choices=REDE_TIPO_CHOICES, blank=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']
```

2. **Criar tabela de ligacao** (model satelite):
```python
class AtividadeRegistroRede(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, CASCADE)
    rede = models.ForeignKey(Rede, on_delete=models.PROTECT)
    indicador = models.ForeignKey(Indicador, SET_NULL, null=True, blank=True)
    indicador_financiador = models.ForeignKey(IndicadorFinanciador, SET_NULL, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=1)
    pessoas = models.PositiveIntegerField(null=True, blank=True)
    instituicoes = models.PositiveIntegerField(null=True, blank=True)
    organizacoes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            # Mesmas constraints de T-2.2
            CheckConstraint(...),
            UniqueConstraint(...),
            UniqueConstraint(...),
        ]
```

3. **Atualizar `SUM_MAP`**:
```python
# ANTES:
'redes': (Rede, 'quantidade')

# DEPOIS:
'redes': (AtividadeRegistroRede, 'quantidade')
```

4. **Atualizar views**:
   - `load_indicadores`: retornar lista de redes cadastradas para o seletor
   - `_atividade_registro_process`: parsear `indicadores_{id}_rede_id` (FK para Rede existente) + campo de quantidade
   - Detail view: atualizar query de redes

5. **Atualizar admin**: `RedeAdmin` com `AtividadeRegistroRedeInline`

6. **Atualizar JS**: seletor de rede (autocomplete ou dropdown) + campo quantidade

### Migration
```python
operations = [
    # 1. Criar AtividadeRegistroRede
    migrations.CreateModel('AtividadeRegistroRede', fields=[...]),

    # 2. Data migration: mover dados de Rede para AtividadeRegistroRede
    # Para cada Rede existente:
    #   - Criar ou encontrar Rede cadastral (por nome)
    #   - Criar AtividadeRegistroRede com FK para a rede

    # 3. Remover campos satelite de Rede antiga
    migrations.RemoveField('rede', 'atividade_registro'),
    migrations.RemoveField('rede', 'indicador'),
    migrations.RemoveField('rede', 'indicador_financiador'),
    migrations.RemoveField('rede', 'quantidade'),
]
```

### Data migration detalhada

Apos criar `AtividadeRegistroRede` e antes de remover os campos satelite de `Rede`, executar uma data migration que preserve os dados existentes:

1. Para cada registro `Rede` atual, normalizar `nome` (`strip().lower()`) para deduplicacao.
2. Criar ou reutilizar uma `Rede` cadastral mestre para cada nome.
3. Criar um `AtividadeRegistroRede` para cada registro antigo, copiando:
   - `atividade_registro`
   - `indicador`
   - `indicador_financiador`
   - `quantidade`
   - FK `rede` apontando para a rede cadastral mestre.

```python
def migrate_rede_data(apps, schema_editor):
    Rede = apps.get_model('ieb', 'Rede')
    AtividadeRegistroRede = apps.get_model('ieb', 'AtividadeRegistroRede')

    redes_by_nome = {}
    for rede in Rede.objects.all().order_by('id'):
        nome_key = (rede.nome or '').strip().lower() or f'rede-{rede.pk}'
        if nome_key not in redes_by_nome:
            redes_by_nome[nome_key] = rede

    for rede in Rede.objects.all().order_by('id'):
        nome_key = (rede.nome or '').strip().lower() or f'rede-{rede.pk}'
        rede_mestre = redes_by_nome[nome_key]
        AtividadeRegistroRede.objects.create(
            atividade_registro=rede.atividade_registro,
            rede=rede_mestre,
            indicador=rede.indicador,
            indicador_financiador=rede.indicador_financiador,
            quantidade=rede.quantidade,
        )
```

**Atencao:** deduplicacao por nome e heuristica. Se existirem redes semanticamente iguais com nomes diferentes, a limpeza deve ser manual antes/depois da migration.

### Estrategia de execucao
1. Agente `muse` cria plano detalhado com steps exatos
2. Agente `forge` executa uma etapa por vez:
   - Etapa 1: Criar model `AtividadeRegistroRede`
   - Etapa 2: Data migration
   - Etapa 3: Atualizar views
   - Etapa 4: Atualizar admin
   - Etapa 5: Atualizar JS
   - Etapa 6: Atualizar SUM_MAP
   - Etapa 7: Limpar model `Rede` antigo

### Verificacao
```python
# Criar rede cadastral
rede = Rede.objects.create(nome='Rede Xingu', tipo='regional')

# Registrar em atividade
arr = AtividadeRegistroRede.objects.create(
    atividade_registro=ar, rede=rede, indicador=ind, quantidade=1
)

# Mesma rede em outra atividade
arr2 = AtividadeRegistroRede.objects.create(
    atividade_registro=ar2, rede=rede, indicador=ind, quantidade=1
)

# SUM_MAP funciona
meta.realizado  # Soma quantidade de AtividadeRegistroRede
```

### Dependencias
Onda 2 concluida (para constraints em `AtividadeRegistroRede`).

---

## T-4.6: P1.14 -- Remover `Outro`

### Referencia no plano
P1.14 do Plano Cirurgico v1.3

### Problema
Model `Outro` e codigo morto sem uso real.

### Arquivos
- `src/ieb/models.py` -- classe `Outro` (~linha 919-930), `INDICADOR_TIPO_CHOICES` (~linha 332), `SUM_MAP` (~linha 477, 538)
- `src/ieb/views.py` -- import `Outro` (~linha 16), detail view (~linha 148), processamento (~linha 632-636, 727-730), `indicadores_config` (~linha 990-993)
- `src/ieb/admin.py` -- Confirmado: `Outro` NAO esta registrado no admin.py. Nenhuma remocao necessaria no admin.

### Referencias a remover (verificadas no codigo)

**models.py:**
- `('outro', 'Outro')` em `INDICADOR_TIPO_CHOICES`
- `default='outro'` em campos tipo (trocar para `default='pessoas'`)
- `'outro': (Outro, 'valor')` no `SUM_MAP` (2x: Meta e MetaFinanciador)
- Classe `Outro` inteira

**views.py:**
- `Outro` no import
- `'outro': Outro.objects.filter(...)` no detail view
- `outro_map = {}` na inicializacao
- Bloco `elif tipo == 'outro':` no processamento
- Cricao de `Outro.objects.create(...)` no POST
- `"outro": [...]` no `indicadores_config`

### Alteracao
1. Remover todas as referencias listadas acima
2. **Confirmado: `Outro` NAO esta registrado no admin.py. Nenhuma remocao necessaria no admin.**
3. Trocar `default='outro'` para `default='pessoas'` nos campos tipo

### Migration
```python
operations = [
    migrations.DeleteModel('Outro'),
]
```

### Verificacao
```python
# INDICADOR_TIPO_CHOICES nao contem 'outro'
assert 'outro' not in dict(Indicador.TIPO_CHOICES)

# SUM_MAP nao contem 'outro'
assert 'outro' not in SUM_MAP

# Formulario v2 nao renderiza campos de Outro
# (tipo 'outro' nao existe mais)
```

### Dependencias
Nenhuma (independente).

---

## T-4.7: P1.15 -- `indicador_financiador` em `AtividadeRegistroModelo`

### Referencia no plano
P1.15 do Plano Cirurgico v1.3

### Problema
`AtividadeRegistroModelo` so tem FK para `Indicador`, nao para `IndicadorFinanciador`.

### Arquivo
- `src/ieb/models.py` -- classe `AtividadeRegistroModelo` (~linha 1190-1209)

### Alteracao
```python
class AtividadeRegistroModelo(models.Model):
    # campos existentes...
    indicador = models.ForeignKey(Indicador, SET_NULL, null=True, blank=True, related_name='atividaderegistromodelo_set')
    # ADICIONAR:
    indicador_financiador = models.ForeignKey(
        IndicadorFinanciador, SET_NULL, null=True, blank=True,
        related_name='atividaderegistromodelo_fin_set',
    )

    class Meta:
        constraints = [
            # Mesmo padrao de T-2.2
            models.CheckConstraint(
                check=~models.Q(indicador__isnull=False, indicador_financiador__isnull=False),
                name='arm_single_fk',
            ),
            models.UniqueConstraint(
                fields=['atividade_registro', 'indicador'],
                condition=models.Q(indicador__isnull=False),
                name='arm_unique_indicador',
            ),
            models.UniqueConstraint(
                fields=['atividade_registro', 'indicador_financiador'],
                condition=models.Q(indicador_financiador__isnull=False),
                name='arm_unique_ind_fin',
            ),
        ]
```

### Migration
```python
operations = [
    migrations.AddField('atividaderegistromodelo', 'indicador_financiador', field=...),
    migrations.AddConstraint('atividaderegistromodelo', ...),
    migrations.AddConstraint('atividaderegistromodelo', ...),
    migrations.AddConstraint('atividaderegistromodelo', ...),
]
```

### Verificacao
```python
# Ambos FKs preenchidos -> IntegrityError
AtividadeRegistroModelo(atividade_registro=ar, indicador=ind, indicador_financiador=fin).save()  # ERRO

# Apenas um -> OK
AtividadeRegistroModelo(atividade_registro=ar, indicador_financiador=fin).save()  # OK
```

### Dependencias
Onda 2 concluida (padrao de constraints ja estabelecido).
