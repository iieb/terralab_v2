from django.db import models

# Create your models here.
from django.utils import timezone
from django.contrib.gis.db import models as gis_models
from PIL import Image
import os

# Create your models here.
# MOVIMENTO INDÍGENA

class OIsRegional(models.Model):
    ois_reg = models.CharField(max_length=255)
    ois_reg_sigla = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=255)
    nome_repr = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)

    def __str__(self):
        return self.ois_reg


class OIsLocal(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=255)
    nome_repr = models.CharField(max_length=255)
    cargo_repr = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class OIRegLoc(models.Model):
    oiregional = models.ForeignKey(OIsRegional, on_delete=models.CASCADE)
    oilocal = models.ForeignKey(OIsLocal, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.oiregional.ois_reg} - {self.oilocal.nome}"


class TIs(models.Model):
    nome = models.CharField(max_length=255)
    area = models.FloatField()
    fase = models.CharField(max_length=255)
    etnia = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255)
    uf = models.CharField(max_length=255)
    modalidade = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Aldeia(models.Model):
    nome = models.CharField(max_length=255)
    tis = models.ForeignKey(TIs, on_delete=models.CASCADE)
    populacao = models.IntegerField()
    ano = models.IntegerField()

    def __str__(self):
        return self.nome


class Indigena(models.Model):
    nome = models.CharField(max_length=255)
    etnia = models.CharField(max_length=255)
    genero = models.CharField(max_length=255)
    cpf = models.CharField(max_length=255)
    rg = models.CharField(max_length=255)
    data_nasc = models.DateField()
    aldeia = models.ForeignKey(Aldeia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
    

# MOVIMENTO INDÍGENA - IGATI

class IGATI(models.Model):
    tipo = models.CharField(max_length=255)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class TIsIGATI(models.Model):
    igati = models.ForeignKey(IGATI, on_delete=models.CASCADE)
    tis = models.ForeignKey(TIs, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.igati.nome} - {self.tis.nome}"



# GESTÃO DE PROJETOS - FINANCIADORES/INTITUIÇÕES

class Financiador(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.sigla


class Instituicao(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Equipe(models.Model):
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=255)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} - {self.instituicao}"

# GESTÃO DE PROJETOS - PROGRAMAS / PROJETOS / COMPONENTES / ATIVIDADES / EQUIPE

class Programa(models.Model):
    """Área temática institucional que agrupa Projetos estrategicamente.
    Distinto de AreaTematica, que classifica Atividades individualmente."""
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'
        ordering = ['sigla']

    def __str__(self):
        return self.sigla


class Projeto(models.Model):
    nome = models.CharField(max_length=255)
    nome_fant = models.CharField(max_length=255)
    programas = models.ManyToManyField(
        Programa, related_name='projetos', blank=True,
        verbose_name='Programas'
    )
    financiadores = models.ManyToManyField(
        Financiador, related_name='projetos', blank=True,
        verbose_name='Financiadores'
    )
    projeto_pai = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='subprojetos',
        verbose_name='Projeto pai'
    )

    def __str__(self):
        if self.projeto_pai_id:
            return f"{self.projeto_pai.nome_fant} / {self.nome_fant}"
        return self.nome_fant


class Componente(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)

    def __str__(self):
        return f"Componente {self.codigo}: {self.nome}"


class Atividade(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Atividade {self.codigo}: {self.nome}"


class EquipeProjeto(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.equipe.nome} - {self.equipe.instituicao}"


class ProjetoOI(models.Model):
    oilocal = models.ForeignKey(OIsLocal, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.oilocal.nome} - {self.projeto.nome}"


class ProjetoTI(models.Model):
    tis = models.ForeignKey(TIs, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tis.nome} - {self.projeto.nome}"


class ProjetoIndicador(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='projeto_indicadores')
    indicador = models.ForeignKey('Indicador', on_delete=models.CASCADE, related_name='projeto_indicadores')

    class Meta:
        unique_together = ('projeto', 'indicador')
        verbose_name = 'Indicador do Projeto'
        verbose_name_plural = 'Indicadores do Projeto'

    def __str__(self):
        return f"{self.projeto.nome_fant} — {self.indicador.nome}"


class ProjetoIndicadorFin(models.Model):
    projeto               = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='projeto_indicadores_fin')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.CASCADE, related_name='projeto_indicadores_fin')

    class Meta:
        unique_together = ('projeto', 'indicador_financiador')
        verbose_name = 'Indicador de Financiador do Projeto'
        verbose_name_plural = 'Indicadores de Financiadores do Projeto'

    def __str__(self):
        return f"{self.projeto.nome_fant} — {self.indicador_financiador}"


# GESTÃO DE PROJETOS - ÁREAS TEMÁTICAS E VÍNCULOS DE ATIVIDADE

class AreaTematica(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Área Temática'
        verbose_name_plural = 'Áreas Temáticas'

    def __str__(self):
        return self.nome


class Subatividade(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='subatividades')

    def __str__(self):
        return f"Subatividade {self.codigo}: {self.nome}"


class AtividadeAreaTematica(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='areas_tematicas')
    area_tematica = models.ForeignKey(AreaTematica, on_delete=models.CASCADE, related_name='atividades')

    class Meta:
        unique_together = ('atividade', 'area_tematica')
        verbose_name = 'Área Temática da Atividade'
        verbose_name_plural = 'Áreas Temáticas das Atividades'

    def __str__(self):
        return f"{self.atividade.codigo} — {self.area_tematica.nome}"


class AtividadeOILocal(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='ois_locais')
    oilocal = models.ForeignKey(OIsLocal, on_delete=models.CASCADE, related_name='atividades')

    class Meta:
        unique_together = ('atividade', 'oilocal')
        verbose_name = 'OI Local da Atividade'
        verbose_name_plural = 'OIs Locais das Atividades'

    def __str__(self):
        return f"{self.atividade.codigo} — {self.oilocal.nome}"


class AtividadeOIRegional(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='ois_regionais')
    oiregional = models.ForeignKey(OIsRegional, on_delete=models.CASCADE, related_name='atividades')

    class Meta:
        unique_together = ('atividade', 'oiregional')
        verbose_name = 'OI Regional da Atividade'
        verbose_name_plural = 'OIs Regionais das Atividades'

    def __str__(self):
        return f"{self.atividade.codigo} — {self.oiregional.ois_reg}"


class AtividadeTI(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='tis')
    ti = models.ForeignKey(TIs, on_delete=models.CASCADE, related_name='atividades')

    class Meta:
        unique_together = ('atividade', 'ti')
        verbose_name = 'Terra Indígena da Atividade'
        verbose_name_plural = 'Terras Indígenas das Atividades'

    def __str__(self):
        return f"{self.atividade.codigo} — {self.ti.nome}"


# GESTÃO DE PROJETOS - INDICADORES/METAS/REGISTROS

INDICADOR_TIPO_CHOICES = [
    ('pessoas',           'Pessoas'),
    ('organizacoes',      'Organizações'),
    ('area',              'Área'),
    ('areas_protegidas',  'Áreas Protegidas'),
    ('eventos',           'Eventos'),
    ('planos',            'Planos'),
    ('parcerias',         'Parcerias'),
    ('mobilizados',       'Recursos Mobilizados'),
    ('produtos',          'Produtos'),
    ('contratos',         'Contratos'),
    ('redes',             'Redes'),
    ('pequenos_projetos', 'Pequenos Projetos'),
    ('fundos',            'Fundos'),
    ('leis_politicas',    'Leis e Políticas'),
    ('outro',             'Outro'),
]

SCORE_PLANO = {
    'em desenvolvimento': 1,
    'proposto':           2,
    'adotado':            3,
    'em implementacao':   4,
    'implementado':       5,
}


class Indicador(models.Model):
    TIPO_CHOICES = INDICADOR_TIPO_CHOICES

    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    reporte = models.CharField(max_length=255)
    tipo = models.CharField(max_length=30, choices=INDICADOR_TIPO_CHOICES, default='outro')

    # Desagregações — Pessoas
    desag_homens            = models.BooleanField(default=False, verbose_name='Homens')
    desag_mulheres          = models.BooleanField(default=False, verbose_name='Mulheres')
    desag_jovens            = models.BooleanField(default=False, verbose_name='Jovens')
    desag_pct               = models.BooleanField(default=False, verbose_name='PCT (grupo)')
    desag_pct_indigenas     = models.BooleanField(default=False, verbose_name='PCT — Indígenas')
    desag_pct_extrativistas = models.BooleanField(default=False, verbose_name='PCT — Extrativistas')
    desag_pct_quilombolas   = models.BooleanField(default=False, verbose_name='PCT — Quilombolas')
    desag_servidor_publico  = models.BooleanField(default=False, verbose_name='Servidor Público')
    tem_foco                = models.BooleanField(default=False, verbose_name='Coletar foco da ação')

    # Desagregações — Organizações
    desag_org_sc            = models.BooleanField(default=False, verbose_name='Sociedade Civil')
    desag_org_indigenas     = models.BooleanField(default=False, verbose_name='Org. Indígenas')
    desag_org_extrativistas = models.BooleanField(default=False, verbose_name='Org. Extrativistas')

    # Desagregações — Área (modos)
    desag_restrito = models.BooleanField(default=False, verbose_name='Área Restrita (HA manual)')
    desag_direto   = models.BooleanField(default=False, verbose_name='Área Direta (M2M → soma HA)')
    desag_indireto = models.BooleanField(default=False, verbose_name='Área Indireta (M2M → soma HA)')

    # Desagregações — Seletores de área protegida (área direto/indireto + áreas protegidas)
    desag_ti  = models.BooleanField(default=False, verbose_name='Terra Indígena (TI)')
    desag_uc  = models.BooleanField(default=False, verbose_name='Unidade de Conservação (UC)')
    desag_pa  = models.BooleanField(default=False, verbose_name='Projeto de Assentamento (PA)')
    desag_tuc = models.BooleanField(default=False, verbose_name='Território de Uso Comum (TUC)')

    # Desagregações — Eventos
    desag_formacoes     = models.BooleanField(default=False, verbose_name='Formações')
    desag_seminarios    = models.BooleanField(default=False, verbose_name='Seminários')
    desag_encontros     = models.BooleanField(default=False, verbose_name='Encontros')
    desag_reunioes      = models.BooleanField(default=False, verbose_name='Reuniões')
    desag_participantes = models.BooleanField(default=False, verbose_name='Registrar participantes')

    def __str__(self):
        return self.nome


class IndicadorFinanciador(models.Model):
    financiador = models.ForeignKey(
        Financiador, on_delete=models.CASCADE,
        related_name='indicadores_proprios',
        verbose_name='Financiador',
    )
    nome      = models.CharField(max_length=255)
    codigo    = models.CharField(max_length=255, blank=True)
    descricao = models.CharField(max_length=255, blank=True)
    reporte   = models.CharField(max_length=255, blank=True)
    tipo      = models.CharField(max_length=30, choices=INDICADOR_TIPO_CHOICES, default='outro')

    # Desagregações — Pessoas
    desag_homens            = models.BooleanField(default=False, verbose_name='Homens')
    desag_mulheres          = models.BooleanField(default=False, verbose_name='Mulheres')
    desag_jovens            = models.BooleanField(default=False, verbose_name='Jovens')
    desag_pct               = models.BooleanField(default=False, verbose_name='PCT (grupo)')
    desag_pct_indigenas     = models.BooleanField(default=False, verbose_name='PCT — Indígenas')
    desag_pct_extrativistas = models.BooleanField(default=False, verbose_name='PCT — Extrativistas')
    desag_pct_quilombolas   = models.BooleanField(default=False, verbose_name='PCT — Quilombolas')
    desag_servidor_publico  = models.BooleanField(default=False, verbose_name='Servidor Público')
    tem_foco                = models.BooleanField(default=False, verbose_name='Coletar foco da ação')

    # Desagregações — Organizações
    desag_org_sc            = models.BooleanField(default=False, verbose_name='Sociedade Civil')
    desag_org_indigenas     = models.BooleanField(default=False, verbose_name='Org. Indígenas')
    desag_org_extrativistas = models.BooleanField(default=False, verbose_name='Org. Extrativistas')

    # Desagregações — Área (modos)
    desag_restrito = models.BooleanField(default=False, verbose_name='Área Restrita (HA manual)')
    desag_direto   = models.BooleanField(default=False, verbose_name='Área Direta (M2M → soma HA)')
    desag_indireto = models.BooleanField(default=False, verbose_name='Área Indireta (M2M → soma HA)')

    # Desagregações — Seletores de área protegida
    desag_ti  = models.BooleanField(default=False, verbose_name='Terra Indígena (TI)')
    desag_uc  = models.BooleanField(default=False, verbose_name='Unidade de Conservação (UC)')
    desag_pa  = models.BooleanField(default=False, verbose_name='Projeto de Assentamento (PA)')
    desag_tuc = models.BooleanField(default=False, verbose_name='Território de Uso Comum (TUC)')

    # Desagregações — Eventos
    desag_formacoes     = models.BooleanField(default=False, verbose_name='Formações')
    desag_seminarios    = models.BooleanField(default=False, verbose_name='Seminários')
    desag_encontros     = models.BooleanField(default=False, verbose_name='Encontros')
    desag_reunioes      = models.BooleanField(default=False, verbose_name='Reuniões')
    desag_participantes = models.BooleanField(default=False, verbose_name='Registrar participantes')

    class Meta:
        verbose_name = 'Indicador de Financiador'
        verbose_name_plural = 'Indicadores de Financiadores'

    def __str__(self):
        return f"{self.financiador.sigla} — {self.nome}"


class Meta(models.Model):
    atividade   = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    indicador   = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    base        = models.FloatField()
    meta        = models.FloatField()
    data        = models.DateField(verbose_name='Prazo / Fim do período')
    data_inicio = models.DateField(null=True, blank=True, verbose_name='Início do período de apuração')

    def __str__(self):
        return f"{self.atividade.codigo} - {self.indicador.nome} - {self.base} - {self.meta}"

    @property
    def realizado(self):
        """Uso pontual (detalhe de uma Meta). Para listagens, usar anotação na queryset."""
        from django.db.models import Sum
        registros = AtividadeRegistro.objects.filter(atividade=self.atividade)
        if self.data_inicio:
            registros = registros.filter(data_inicio__gte=self.data_inicio, data_inicio__lte=self.data)
        tipo = self.indicador.tipo
        SUM_MAP = {
            'pessoas':           (Pessoas,        'total_pessoas'),
            'organizacoes':      (Organizacoes,   'total_organizacoes'),
            'area':              (Area,            'total_ha'),
            'areas_protegidas':  (AreasProtegidas, 'total'),
            'eventos':           (Evento,          'total'),
            'redes':             (Rede,            'quantidade'),
            'pequenos_projetos': (PequenoProjeto,  'quantidade'),
            'fundos':            (Fundo,           'quantidade'),
            'leis_politicas':    (Leis,            'total_leis'),
            'parcerias':         (Parcerias,       'total_parcerias'),
            'mobilizados':       (Mobilizados,     'valor_mobilizado'),
            'produtos':          (Produtos,        'total_produtos'),
            'outro':             (Outro,           'valor'),
        }
        COUNT_MAP = {
            'contratos': Contratos,
        }
        if tipo in SUM_MAP:
            Model, field = SUM_MAP[tipo]
            result = Model.objects.filter(
                atividade_registro__in=registros, indicador=self.indicador
            ).aggregate(total=Sum(field))
            return result['total'] or 0
        elif tipo in COUNT_MAP:
            return COUNT_MAP[tipo].objects.filter(
                atividade_registro__in=registros, indicador=self.indicador
            ).count()
        elif tipo == 'planos':
            ultimo = Planos.objects.filter(
                atividade_registro__atividade=self.atividade,
                indicador=self.indicador
            ).select_related('plano').order_by('-pk').first()
            if not ultimo or not ultimo.plano:
                return 0
            return SCORE_PLANO.get(ultimo.plano.situacao, 0)
        return 0

    @property
    def percentual(self):
        return round((self.realizado / self.meta) * 100, 1) if self.meta else 0


class MetaFinanciador(models.Model):
    atividade             = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='metas_financiador')
    indicador_financiador = models.ForeignKey(IndicadorFinanciador, on_delete=models.CASCADE, related_name='metas')
    base        = models.FloatField()
    meta        = models.FloatField()
    data        = models.DateField(verbose_name='Prazo / Fim do período')
    data_inicio = models.DateField(null=True, blank=True, verbose_name='Início do período de apuração')

    def __str__(self):
        return f"{self.atividade.codigo} - {self.indicador_financiador.nome}"

    @property
    def realizado(self):
        from django.db.models import Sum
        tipo = self.indicador_financiador.tipo
        registros = AtividadeRegistro.objects.filter(atividade=self.atividade)
        if self.data_inicio:
            registros = registros.filter(data_inicio__gte=self.data_inicio, data_inicio__lte=self.data)
        SUM_MAP = {
            'pessoas':           (Pessoas,        'total_pessoas'),
            'organizacoes':      (Organizacoes,   'total_organizacoes'),
            'area':              (Area,            'total_ha'),
            'areas_protegidas':  (AreasProtegidas, 'total'),
            'eventos':           (Evento,          'total'),
            'redes':             (Rede,            'quantidade'),
            'pequenos_projetos': (PequenoProjeto,  'quantidade'),
            'fundos':            (Fundo,           'quantidade'),
            'leis_politicas':    (Leis,            'total_leis'),
            'parcerias':         (Parcerias,       'total_parcerias'),
            'mobilizados':       (Mobilizados,     'valor_mobilizado'),
            'produtos':          (Produtos,        'total_produtos'),
            'outro':             (Outro,           'valor'),
        }
        COUNT_MAP = {
            'contratos': Contratos,
        }
        if tipo in SUM_MAP:
            Model, field = SUM_MAP[tipo]
            result = Model.objects.filter(
                atividade_registro__in=registros,
                indicador_financiador=self.indicador_financiador
            ).aggregate(total=Sum(field))
            return result['total'] or 0
        elif tipo in COUNT_MAP:
            return COUNT_MAP[tipo].objects.filter(
                atividade_registro__in=registros,
                indicador_financiador=self.indicador_financiador
            ).count()
        elif tipo == 'planos':
            ultimo = Planos.objects.filter(
                atividade_registro__atividade=self.atividade,
                indicador_financiador=self.indicador_financiador
            ).select_related('plano').order_by('-pk').first()
            if not ultimo or not ultimo.plano:
                return 0
            return SCORE_PLANO.get(ultimo.plano.situacao, 0)
        return 0

    @property
    def percentual(self):
        return round((self.realizado / self.meta) * 100, 1) if self.meta else 0


class AtividadeRegistro(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    subatividade = models.ForeignKey(Subatividade, on_delete=models.SET_NULL, null=True, blank=True)
    equipe_projeto = models.ForeignKey(EquipeProjeto, on_delete=models.CASCADE)
    equipe_adicional = models.ManyToManyField(EquipeProjeto, related_name='atividades_registradas', blank=True)
    data_inicio = models.DateField()
    data_final = models.DateField()
    desafios = models.CharField(max_length=255, blank=True)
    propostas = models.CharField(max_length=255, blank=True)
    sucesso = models.CharField(max_length=255, blank=True)
    melhores_praticas = models.CharField(max_length=255, blank=True)
    descricao = models.TextField()
    local = models.CharField(max_length=255)
    comentarios = models.TextField(blank=True)
    email_organizacao = models.EmailField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"{self.data_inicio} - {self.projeto.nome}/COMP-{self.componente.codigo}/ATIV-{self.atividade.codigo} - {self.atividade.nome}"


class AtividadeRegistroFoto(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, related_name='fotos_set')
    foto = models.ImageField(upload_to='fotos/', max_length=255)
    foto_thumbnail = models.ImageField(upload_to='fotos/thumbnails/', blank=True, editable=False, max_length=255)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto:
            img_path = self.foto.path
            with Image.open(img_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.thumbnail((300, 300))
                thumbnail_dir = os.path.join(os.path.dirname(img_path), 'thumbnails')
                if not os.path.exists(thumbnail_dir):
                    os.makedirs(thumbnail_dir)
                thumbnail_path = os.path.join(thumbnail_dir, os.path.basename(img_path))
                img.save(thumbnail_path, format='JPEG', quality=85)
                self.foto_thumbnail.name = os.path.join('fotos/thumbnails/', os.path.basename(img_path))
            super().save(update_fields=['foto_thumbnail'])

    def __str__(self):
        return f"Foto - {self.atividade_registro}"


class AtividadeRegistroListaPresenca(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, related_name='listas_presenca_set')
    arquivo = models.FileField(upload_to='listas_presenca/', max_length=255)

    def __str__(self):
        return f"Lista de presença - {self.atividade_registro}"


# GESTÃO DE PROJETOS

# CATÁLOGOS GEOGRÁFICOS
class UC(models.Model):
    nome = models.CharField(max_length=255)
    area = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Unidade de Conservação'
        verbose_name_plural = 'Unidades de Conservação'

    def __str__(self):
        return self.nome


class PA(models.Model):
    nome = models.CharField(max_length=255)
    area = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Projeto de Assentamento'
        verbose_name_plural = 'Projetos de Assentamento'

    def __str__(self):
        return self.nome


class TUC(models.Model):
    nome = models.CharField(max_length=255)
    area = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Território de Uso Comum'
        verbose_name_plural = 'Territórios de Uso Comum'

    def __str__(self):
        return self.nome


# ÁREA (unifica AreaRestrito + AreaDireto + AreaGeral)
class Area(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    # Modo restrito — HA manual
    ha_restrito = models.FloatField(null=True, blank=True)
    # Modos direto/indireto — seleção M2M + soma automática
    tis  = models.ManyToManyField(TIs,  blank=True, related_name='areas')
    ucs  = models.ManyToManyField(UC,   blank=True, related_name='areas')
    pas  = models.ManyToManyField(PA,   blank=True, related_name='areas')
    tucs = models.ManyToManyField(TUC,  blank=True, related_name='areas')
    total_ha = models.FloatField(default=0.0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        if self.ha_restrito is not None:
            self.total_ha = self.ha_restrito
        else:
            total = 0.0
            for m2m in (self.tis, self.ucs, self.pas, self.tucs):
                total += m2m.aggregate(s=models.Sum('area'))['s'] or 0.0
            self.total_ha = total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} — {self.total_ha} ha"


# ÁREAS PROTEGIDAS (conta unidades por tipo)
class AreasProtegidas(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    tis  = models.ManyToManyField(TIs,  blank=True, related_name='areas_protegidas')
    ucs  = models.ManyToManyField(UC,   blank=True, related_name='areas_protegidas')
    pas  = models.ManyToManyField(PA,   blank=True, related_name='areas_protegidas')
    tucs = models.ManyToManyField(TUC,  blank=True, related_name='areas_protegidas')
    total_tis  = models.PositiveIntegerField(default=0, editable=False)
    total_ucs  = models.PositiveIntegerField(default=0, editable=False)
    total_pas  = models.PositiveIntegerField(default=0, editable=False)
    total_tucs = models.PositiveIntegerField(default=0, editable=False)
    total      = models.PositiveIntegerField(default=0, editable=False)
    total_ha   = models.FloatField(default=0.0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')
        verbose_name = 'Áreas Protegidas'
        verbose_name_plural = 'Áreas Protegidas'

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        self.total_tis  = self.tis.count()
        self.total_ucs  = self.ucs.count()
        self.total_pas  = self.pas.count()
        self.total_tucs = self.tucs.count()
        self.total = self.total_tis + self.total_ucs + self.total_pas + self.total_tucs
        ha = 0.0
        for m2m in (self.tis, self.ucs, self.pas, self.tucs):
            ha += m2m.aggregate(s=models.Sum('area'))['s'] or 0.0
        self.total_ha = ha
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} — {self.total} áreas protegidas"
    
FOCO_CHOICES = [
    ('implementacao', 'Implementação melhorada/monitoramento/vigilância'),
    ('ativ_prod',     'Meios de subsistência/cadeia de valor sustentáveis melhorados'),
    ('governanca',   'Fortalecimento institucional/capacitação organizacional/governança'),
]

# PESSOAS
class Pessoas(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    total_pessoas         = models.PositiveIntegerField(default=0)
    homens                = models.PositiveIntegerField(null=True, blank=True)
    mulheres              = models.PositiveIntegerField(null=True, blank=True)
    jovens                = models.PositiveIntegerField(null=True, blank=True)
    pct_indigenas         = models.PositiveIntegerField(null=True, blank=True)
    pct_extrativistas     = models.PositiveIntegerField(null=True, blank=True)
    pct_quilombolas       = models.PositiveIntegerField(null=True, blank=True)
    servidor_publico      = models.PositiveIntegerField(null=True, blank=True)
    foco                  = models.CharField(max_length=20, choices=FOCO_CHOICES, blank=True)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_pessoas}"

# LEIS E POLÍTICAS
class Lei(models.Model):
    TIPO_CHOICES = [
        ('PGTA', 'PGTA'),
    ]
    
    SITUACAO_CHOICES = [
        ('em desenvolvimento', 'Em Desenvolvimento'),
        ('proposto', 'Proposto'),
        ('aprovado', 'Aprovado'),
        ('implementado', 'Implementado')
    ]

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255, choices=TIPO_CHOICES)
    situacao = models.CharField(max_length=255, choices=SITUACAO_CHOICES)

    def __str__(self):
        return f"{self.nome} - {self.tipo} - {self.situacao}"

class Leis(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    leis       = models.ManyToManyField(Lei, related_name='leis')
    total_leis = models.PositiveIntegerField(default=0, editable=False)
    total_em_desenvolvimento = models.PositiveIntegerField(default=0, editable=False)
    total_propostas          = models.PositiveIntegerField(default=0, editable=False)
    total_aprovadas          = models.PositiveIntegerField(default=0, editable=False)
    total_implementadas      = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_leis              = self.leis.count()
        self.total_em_desenvolvimento = self.leis.filter(situacao='em desenvolvimento').count()
        self.total_propostas          = self.leis.filter(situacao='proposto').count()
        self.total_aprovadas          = self.leis.filter(situacao='aprovado').count()
        self.total_implementadas      = self.leis.filter(situacao='implementado').count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_leis} leis"

class LeiHistorico(models.Model):
    lei = models.ForeignKey(Lei, on_delete=models.CASCADE)
    situacao_anterior = models.CharField(max_length=255, choices=Lei.SITUACAO_CHOICES)
    situacao_nova = models.CharField(max_length=255, choices=Lei.SITUACAO_CHOICES)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=255)  # Ou usar um ForeignKey para o modelo de usuário

    def __str__(self):
        return f"{self.lei.nome} - Alteração de {self.situacao_anterior} para {self.situacao_nova} em {self.data_alteracao}"
    
# ORGANIZAÇÕES
class Organizacoes(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    total_organizacoes    = models.PositiveIntegerField(default=0)
    org_sociedade_civil   = models.PositiveIntegerField(null=True, blank=True, verbose_name='Sociedade Civil')
    org_indigenas         = models.PositiveIntegerField(null=True, blank=True, verbose_name='Org. Indígenas')
    org_extrativistas     = models.PositiveIntegerField(null=True, blank=True, verbose_name='Org. Extrativistas')
    foco                  = models.CharField(max_length=20, choices=FOCO_CHOICES, blank=True)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_organizacoes} organizações"

# EVENTOS
class Evento(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    formacoes   = models.PositiveIntegerField(null=True, blank=True)
    seminarios  = models.PositiveIntegerField(null=True, blank=True)
    encontros   = models.PositiveIntegerField(null=True, blank=True)
    reunioes    = models.PositiveIntegerField(null=True, blank=True)
    participantes = models.PositiveIntegerField(null=True, blank=True)
    total       = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        self.total = sum(v for v in [self.formacoes, self.seminarios, self.encontros, self.reunioes] if v)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} — {self.total} eventos"


# REDES
REDE_TIPO_CHOICES = [
    ('local',         'Local'),
    ('regional',      'Regional'),
    ('nacional',      'Nacional'),
    ('internacional', 'Internacional'),
]

class Rede(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    nome       = models.CharField(max_length=255, blank=True)
    tipo       = models.CharField(max_length=50, choices=REDE_TIPO_CHOICES, blank=True)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.atividade_registro} — {self.nome or self.tipo} ({self.quantidade})"


# PEQUENOS PROJETOS
class PequenoProjeto(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    quantidade  = models.PositiveIntegerField(default=0)
    tipo        = models.CharField(max_length=100, blank=True)
    tema        = models.CharField(max_length=100, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Pequeno Projeto'
        verbose_name_plural = 'Pequenos Projetos'

    def __str__(self):
        return f"{self.atividade_registro} — {self.quantidade} pequenos projetos"


# FUNDOS
FUNDO_TIPO_CHOICES = [
    ('publico',       'Público'),
    ('privado',       'Privado'),
    ('internacional', 'Internacional'),
    ('misto',         'Misto'),
]

class Fundo(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    quantidade  = models.PositiveIntegerField(default=0)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    tipo        = models.CharField(max_length=50, choices=FUNDO_TIPO_CHOICES, blank=True)

    def __str__(self):
        return f"{self.atividade_registro} — {self.quantidade} fundos"


# OUTRO
class Outro(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    descricao = models.TextField(blank=True)
    valor     = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def __str__(self):
        return f"{self.atividade_registro} — outro"


# PLANOS
class Plano(models.Model):
    TIPO_CHOICES = [
        ('PGTA',                   'PGTA'),
        ('Plano de Adaptação',     'Plano de Adaptação'),
        ('Plano de Manejo',        'Plano de Manejo'),
        ('Plano de Enfrentamento', 'Plano de Enfrentamento'),
        ('Plano de Diagnóstico',   'Plano de Diagnóstico'),
        ('Outro',                  'Outro'),
    ]

    SITUACAO_CHOICES = [
        ('em desenvolvimento', 'Em Desenvolvimento'),
        ('proposto',           'Proposto'),
        ('adotado',            'Adotado'),
        ('em implementacao',   'Em Implementação'),
        ('implementado',       'Implementado'),
    ]

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255, choices=TIPO_CHOICES)
    situacao = models.CharField(max_length=255, choices=SITUACAO_CHOICES)
    tis = models.ManyToManyField(TIs, related_name='planos', blank=True,
                                  verbose_name='Terras Indígenas')

    def __str__(self):
        return f"{self.nome} - {self.tipo} - {self.situacao}"

class Planos(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    plano = models.ForeignKey(
        'Plano', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='registros',
        verbose_name='Plano',
    )
    situacao_anterior = models.CharField(
        max_length=255, choices=Plano.SITUACAO_CHOICES,
        blank=True, editable=False
    )
    situacao_nova = models.CharField(
        max_length=255, choices=Plano.SITUACAO_CHOICES,
        default='em desenvolvimento'
    )

    def save(self, *args, **kwargs):
        plano = self.plano
        if plano and not self.pk:  # apenas na criação
            self.situacao_anterior = plano.situacao
            if plano.situacao != self.situacao_nova:
                PlanoHistorico.objects.create(
                    plano=plano,
                    situacao_anterior=plano.situacao,
                    situacao_nova=self.situacao_nova,
                    usuario=str(self.atividade_registro.equipe_projeto.equipe.nome)
                )
                plano.situacao = self.situacao_nova
                plano.save(update_fields=['situacao'])
        super().save(*args, **kwargs)

    def __str__(self):
        nome = self.plano.nome if self.plano else '?'
        return f"{self.atividade_registro} — {nome}: {self.situacao_anterior} → {self.situacao_nova}"


class PlanoHistorico(models.Model):
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE)
    situacao_anterior = models.CharField(max_length=255, choices=Plano.SITUACAO_CHOICES)
    situacao_nova = models.CharField(max_length=255, choices=Plano.SITUACAO_CHOICES)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=255)  # Ou usar um ForeignKey para um modelo de usuário, se necessário

    def __str__(self):
        return f"{self.plano.nome} - Alteração de {self.situacao_anterior} para {self.situacao_nova} em {self.data_alteracao}"
    
# PARCERIAS
PARCERIA_TIPO_CHOICES = [
    ('governo_federal',            'Governo Federal'),
    ('governo_estadual_municipal', 'Governo Estadual / Municipal'),
    ('osc_ong',                    'OSC / ONG'),
    ('organizacao_internacional',  'Organização Internacional'),
    ('inst_ensino',                'Instituição de Ensino'),
    ('inst_pesquisa',              'Instituição de Pesquisa'),
]

class Parceria(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=PARCERIA_TIPO_CHOICES, blank=True)

    def __str__(self):
        return self.nome


class Parcerias(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    parcerias             = models.ManyToManyField(Parceria, related_name='parcerias')
    total_parcerias                  = models.PositiveIntegerField(default=0, editable=False)
    total_governo_federal            = models.PositiveIntegerField(default=0, editable=False)
    total_governo_estadual_municipal = models.PositiveIntegerField(default=0, editable=False)
    total_osc_ong                    = models.PositiveIntegerField(default=0, editable=False)
    total_organizacao_internacional  = models.PositiveIntegerField(default=0, editable=False)
    total_inst_ensino                = models.PositiveIntegerField(default=0, editable=False)
    total_inst_pesquisa              = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_parcerias                  = self.parcerias.count()
        self.total_governo_federal            = self.parcerias.filter(tipo='governo_federal').count()
        self.total_governo_estadual_municipal = self.parcerias.filter(tipo='governo_estadual_municipal').count()
        self.total_osc_ong                    = self.parcerias.filter(tipo='osc_ong').count()
        self.total_organizacao_internacional  = self.parcerias.filter(tipo='organizacao_internacional').count()
        self.total_inst_ensino                = self.parcerias.filter(tipo='inst_ensino').count()
        self.total_inst_pesquisa              = self.parcerias.filter(tipo='inst_pesquisa').count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_parcerias} parcerias"
    
# MOBILIZADOS

class Mobilizados(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    valor_mobilizado = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_apoio = models.CharField(max_length=255, choices=[
        ('Contribuição em dinheiro', 'Contribuição em dinheiro'),
        ('Voluntariado', 'Voluntariado'),
        ('Doação do tempo dos funcionários', 'Doação do tempo dos funcionários'),
        ('Doação de suprimentos, equipamentos', 'Doação de suprimentos, equipamentos'),
        ('Propriedade intelectual', 'Propriedade intelectual'),
    ])
    fonte_apoio = models.CharField(max_length=255, choices=[
        ('Renda proveniente da atividades/projeto', 'Renda proveniente da atividades/projeto'),
        ('Empresas', 'Empresas'),
        ('Fundação privada', 'Fundação privada'),
        ('Outros doadores (incluindo multilaterais)', 'Outros doadores (incluindo multilaterais)'),
        ('Outras organizações sem fins lucrativos', 'Outras organizações sem fins lucrativos'),
        ('Indivíduo de alta renda/Investidor anjo', 'Indivíduo de alta renda/Investidor anjo'),
        ('OUTRO (especifique)', 'OUTRO (especifique)'),
    ])

    class Meta:
        verbose_name = 'Mobilizado'
        verbose_name_plural = 'Mobilizados'
        unique_together = ('atividade_registro', 'indicador')

    def __str__(self):
        return f"Mobilizado - Valor: {self.valor_mobilizado}"

# PRODUTOS
PRODUTO_TIPO_CHOICES = [
    ('revista',        'Revista'),
    ('boletim',        'Boletim'),
    ('livro',          'Livro'),
    ('sistematizacao', 'Sistematização de Experiências'),
    ('nota_tecnica',   'Nota Técnica'),
    ('relatorio',      'Relatório'),
    ('cartilha',       'Cartilha'),
]

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=PRODUTO_TIPO_CHOICES, blank=True)

    def __str__(self):
        return self.nome


class Produtos(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    produtos              = models.ManyToManyField(Produto, related_name='produtos')
    total_produtos        = models.PositiveIntegerField(default=0, editable=False)
    total_revistas        = models.PositiveIntegerField(default=0, editable=False)
    total_boletins        = models.PositiveIntegerField(default=0, editable=False)
    total_livros          = models.PositiveIntegerField(default=0, editable=False)
    total_sistematizacoes = models.PositiveIntegerField(default=0, editable=False)
    total_notas_tecnicas  = models.PositiveIntegerField(default=0, editable=False)
    total_relatorios      = models.PositiveIntegerField(default=0, editable=False)
    total_cartilhas       = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_produtos        = self.produtos.count()
        self.total_revistas        = self.produtos.filter(tipo='revista').count()
        self.total_boletins        = self.produtos.filter(tipo='boletim').count()
        self.total_livros          = self.produtos.filter(tipo='livro').count()
        self.total_sistematizacoes = self.produtos.filter(tipo='sistematizacao').count()
        self.total_notas_tecnicas  = self.produtos.filter(tipo='nota_tecnica').count()
        self.total_relatorios      = self.produtos.filter(tipo='relatorio').count()
        self.total_cartilhas       = self.produtos.filter(tipo='cartilha').count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_produtos} produtos"
    
# CONTRATOS
class Contrato(models.Model):
    ESTADO_CHOICES = [
        ('alinhamento_realizado', 'Alinhamento Realizado'),
        ('em_desenvolvimento',    'Contrato em Desenvolvimento'),
        ('assinado',              'Contrato Assinado'),
    ]

    nome   = models.CharField(max_length=100)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='alinhamento_realizado')
    valor  = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                 verbose_name='Valor do contrato (R$)')
    produtos = models.ManyToManyField(Produto, related_name='contratos')

    def __str__(self):
        produtos_nomes = ', '.join([p.nome for p in self.produtos.all()])
        return f"{self.nome} - {self.get_estado_display()} - Produtos: {produtos_nomes}"


class Contratos(models.Model):
    atividade_registro    = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador             = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    indicador_financiador = models.ForeignKey('IndicadorFinanciador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    contratos   = models.ManyToManyField(Contrato, related_name='contratos_registro')
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, editable=False)

    class Meta:
        unique_together = ('atividade_registro', 'indicador')

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.valor_total = self.contratos.aggregate(total=models.Sum('valor'))['total']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.contratos.count()} contratos"
# MODELOS E OUTROS REGISTROS
class Modelo(models.Model):
    nome = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'

    def __str__(self):
        return self.nome
    
class AtividadeRegistroModelo(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    indicador = models.ForeignKey('Indicador', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Em desenvolvimento/proposto', 'Em desenvolvimento/proposto'),
            ('Implementação ativa', 'Implementação ativa'),
            ('Difundido (modelo adotado em outro lugar)', 'Difundido (modelo adotado em outro lugar)'),
        ],
        verbose_name='Status do Modelo'
    )

    class Meta:
        verbose_name = 'Atividade Registro Modelo'
        verbose_name_plural = 'Atividades Registro Modelos'

    def __str__(self):
        return f"{self.atividade_registro} - {self.modelo} - {self.status}"

# FORMAÇÃO INDÍGENA
class FormacaoIndigena(models.Model):
    formacao = models.CharField(max_length=255)
    indigena = models.ForeignKey(Indigena, on_delete=models.CASCADE)

    def __str__(self):
        return self.formacao

# POLÍTICA PÚBLICA INDÍGENA

## FUNAI

class CR(models.Model):
    nome = models.CharField(max_length=255)
    coordenador = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class CTL(models.Model):
    nome = models.CharField(max_length=255)
    coordenador = models.CharField(max_length=255)
    cr = models.ForeignKey(CR, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


## SAÚDE INDÍGENA

class DSEI(models.Model):
    nome = models.CharField(max_length=255)
    coordenador = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Posto(models.Model):
    nome = models.CharField(max_length=255)
    dsei = models.ForeignKey(DSEI, on_delete=models.CASCADE)
    aldeia = models.ForeignKey(Aldeia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Casai(models.Model):
    nome = models.CharField(max_length=255)
    dsei = models.ForeignKey(DSEI, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Polo(models.Model):
    nome = models.CharField(max_length=255)
    dsei = models.ForeignKey(DSEI, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class AIS(models.Model):
    nome = models.CharField(max_length=255)
    dsei = models.ForeignKey(DSEI, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


## EDUCAÇÃO INDÍGENA

class Escola(models.Model):
    nome = models.CharField(max_length=255)
    esfera = models.CharField(max_length=255)
    aldeia = models.ForeignKey(Aldeia, on_delete=models.CASCADE)
    coordenador = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Professores(models.Model):
    nome = models.CharField(max_length=255)
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome