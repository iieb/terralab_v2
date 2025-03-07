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

# GESTÃO DE PROJETOS - PROJETOS/COMPONENTES/ATIVIDADES/EQUIPE

class Projeto(models.Model):
    nome = models.CharField(max_length=255)
    nome_fant = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


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


# GESTÃO DE PROJETOS - INDICADORES/METAS/REGISTROS

class Indicador(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    reporte = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Meta(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    base = models.FloatField()
    meta = models.FloatField()
    data = models.DateField()

    def __str__(self):
        return f"{self.atividade.codigo} - {self.indicador.nome} - {self.base} - {self.meta}"


class AtividadeRegistro(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    equipe_projeto = models.ForeignKey(EquipeProjeto, on_delete=models.CASCADE)
    equipe_adicional = models.ManyToManyField(EquipeProjeto, related_name='atividades_registradas', blank=True)
    data_inicio = models.DateField()
    data_final = models.DateField()
    desafios = models.CharField(max_length=255, blank=True)
    propostas = models.CharField(max_length=255, blank=True)
    sucesso = models.CharField(max_length=255, blank=True)
    melhores_praticas = models.CharField(max_length=255, blank=True)
    fotos = models.ImageField(upload_to='fotos/', blank = True)  # Usar ImageField para suportar upload de mídia
    fotos_thumbnail = models.ImageField(upload_to='fotos/thumbnails/', blank=True, editable=False)
    descricao = models.TextField()
    local = models.CharField(max_length=255)
    comentarios = models.TextField(blank=True)
    lista_presenca = models.ImageField(upload_to='listas_presenca/', blank=True)  # Novo campo para lista de presença
    email_organizacao = models.EmailField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.fotos:
            # Caminho da imagem original
            img_path = self.fotos.path

            # Abrindo a imagem usando Pillow
            with Image.open(img_path) as img:
                # Se a imagem estiver em RGBA, converta para RGB
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Definindo o tamanho máximo da miniatura
                img.thumbnail((300, 300))  # Redimensiona mantendo a proporção

                # Definindo o caminho da miniatura
                thumbnail_dir = os.path.join(os.path.dirname(img_path), 'thumbnails')
                # Verificar se o diretório existe, se não, cria-o
                if not os.path.exists(thumbnail_dir):
                    os.makedirs(thumbnail_dir)

                thumbnail_path = os.path.join(thumbnail_dir, os.path.basename(img_path))

                # Salvando a miniatura no caminho definido
                img.save(thumbnail_path, format='JPEG', quality=85)

                # Atualizando o campo fotos_thumbnail com o caminho da miniatura
                self.fotos_thumbnail.name = os.path.join('fotos/thumbnails/', os.path.basename(img_path))

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.data_inicio} - {self.projeto.nome}/COMP-{self.componente.codigo}/ATIV-{self.atividade.codigo} - {self.atividade.nome}"


class AtividadeRegistroEquipe(models.Model):
    equipe_projeto = models.ForeignKey(EquipeProjeto, on_delete=models.CASCADE)
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.equipe_projeto} - {self.atividade_registro}"

# GESTÃO DE PROJETOS - INDICADORES USAID

# 10.2-1 restrito - OK
class AreaRestrito(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    ti = models.ForeignKey(TIs, on_delete=models.CASCADE, related_name='area_restrito')
    area_em_ha = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Área Restrita'
        verbose_name_plural = 'Áreas Restritas'

    def __str__(self):
        return f"{self.atividade_registro} - {self.ti.nome} - {self.area_em_ha} ha"

# 10.2-2 direto - OK
class AreaDireto(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    tis = models.ManyToManyField(TIs, related_name='area_direto')
    total_tis = models.PositiveIntegerField(default=0, editable=False)
    total_area = models.FloatField(default=0.0, editable=False)  # Novo campo para armazenar a soma da área das TIs

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        
        # Calcula o total de TIs e a soma da área
        self.total_tis = self.tis.count()
        self.total_area = self.tis.aggregate(total_area=models.Sum('area'))['total_area'] or 0.0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_tis} TIs - {self.total_area} ha de área"

# 10.2-3 geral - OK
class AreaGeral(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    tis = models.ManyToManyField(TIs, related_name='area_geral')
    total_tis = models.PositiveIntegerField(default=0, editable=False)
    total_area = models.FloatField(default=0.0, editable=False)  # Novo campo para armazenar a soma da área das TIs

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        
        # Calcula o total de TIs e a soma da área
        self.total_tis = self.tis.count()
        self.total_area = self.tis.aggregate(total_area=models.Sum('area'))['total_area'] or 0.0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_tis} TIs - {self.total_area} ha de área"
    
# 10.2-4 treinados - OK
class Treinados(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, default=1)
    total_pessoas = models.PositiveIntegerField(default=0)
    homens = models.PositiveIntegerField(default=0)
    mulheres = models.PositiveIntegerField(default=0)
    jovens = models.PositiveIntegerField(default=0)
    FOCO_CHOICES = [
        ('implementacao', 'Implementação melhorada/monitoramento/vigilância'),
        ('ativ_prod', 'Meios de subsistência/cadeia de valor sustentáveis melhorados'),
        ('governanca', 'Fortalecimento institucional/capacitação organizacional/governança'),
    ]
    foco_treinamento = models.CharField(max_length=20, choices=FOCO_CHOICES, default='governanca')

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_pessoas}"

# 10.2-5 Leis Políticas - OK
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
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    leis = models.ManyToManyField(Lei, related_name='leis')
    total_leis = models.PositiveIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        # Evitar contar leis antes que a instância tenha um ID
        if self.pk is None:
            super().save(*args, **kwargs)

        # Atualiza o campo `total_leis` com a contagem de leis selecionadas
        self.total_leis = self.leis.count()
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
    
# 7 Capacitados - OK
class Organizacao(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Capacitados(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, default=1)
    organizacoes = models.ManyToManyField(Organizacao, related_name='capacitados')
    total_organizacoes = models.PositiveIntegerField(default=0, editable=False)
    foco_capacitacao = models.CharField(max_length=50, choices=[
        ('implementacao', 'Implementação melhorada/monitoramento/vigilância'),
        ('ativ_prod', 'Meios de subsistência/cadeia de valor sustentáveis melhorados'),
        ('governanca', 'Fortalecimento institucional/capacitação organizacional/governança')
    ])

    def save(self, *args, **kwargs):
        # Evite contar organizações antes que a instância tenha um ID
        if self.pk is None:
            super().save(*args, **kwargs)
        
        # Atualiza o campo `total_organizacoes` com a contagem de organizações selecionadas
        self.total_organizacoes = self.organizacoes.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_organizacoes} organizações - {self.foco_capacitacao}"
    
# 8 aplicação - OK
class Aplicacao(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    total_pessoas = models.PositiveIntegerField()
    homens = models.PositiveIntegerField()
    mulheres = models.PositiveIntegerField()
    jovens = models.PositiveIntegerField()

    def __str__(self):
        return f"Aplicação - Total: {self.total_pessoas}"
    
# 9 Planos APs - OK
class Plano(models.Model):
    TIPO_CHOICES = [
        ('PGTA', 'PGTA'),
        ('Plano de Enfrentamento', 'Plano de Enfrentamento'),
        ('Plano de Diagnóstico', 'Plano de Diagnóstico')
    ]
    
    SITUACAO_CHOICES = [
        ('em desenvolvimento', 'Em Desenvolvimento'),
        ('proposto', 'Proposto'),
        ('adotado', 'Adotado'),
        ('implementado', 'Implementado')
    ]

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255, choices=TIPO_CHOICES)
    situacao = models.CharField(max_length=255, choices=SITUACAO_CHOICES)

    def __str__(self):
        return f"{self.nome} - {self.tipo} - {self.situacao}"

class Planos(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, default=1)
    planos = models.ManyToManyField(Plano, related_name='planos')
    total_planos = models.PositiveIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        # Evitar contar planos antes que a instância tenha um ID
        if self.pk is None:
            super().save(*args, **kwargs)

        # Atualiza o campo `total_planos` com a contagem de planos selecionados
        self.total_planos = self.planos.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_planos} planos"


    def __str__(self):
        return f"{self.nome} - {self.tipo} - {self.situacao}"
    
class PlanoHistorico(models.Model):
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE)
    situacao_anterior = models.CharField(max_length=255, choices=[('em desenvolvimento', 'Em Desenvolvimento'), ('proposto', 'Proposto'), ('adotado', 'Adotado'), ('implementado', 'Implementado')])
    situacao_nova = models.CharField(max_length=255, choices=[('em desenvolvimento', 'Em Desenvolvimento'), ('proposto', 'Proposto'), ('adotado', 'Adotado'), ('implementado', 'Implementado')])
    data_alteracao = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=255)  # Ou usar um ForeignKey para um modelo de usuário, se necessário

    def __str__(self):
        return f"{self.plano.nome} - Alteração de {self.situacao_anterior} para {self.situacao_nova} em {self.data_alteracao}"
    
# 10 Parcerias - OK
class Parceria(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class Parcerias(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    parcerias = models.ManyToManyField(Parceria, related_name='parcerias')
    total_parcerias = models.PositiveIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_parcerias = self.parcerias.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_parcerias} parcerias"
    
# 11 mobilizados - OK

class Mobilizados(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
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

    def __str__(self):
        return f"Mobilizado - Valor: {self.valor_mobilizado}"
    
# 12 beneficios PPPs - N/A

# 13 produtos - OK
class Produto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Produtos(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE, default=1)
    produtos = models.ManyToManyField(Produto, related_name='produtos')
    total_produtos = models.PositiveIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_produtos = self.produtos.count()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.atividade_registro} - {self.total_produtos} produtos"
    
# 14 contratos - OK
class Contrato(models.Model):
    ESTADO_CHOICES = [
        ('alinhamento_realizado', 'Alinhamento Realizado'),
        ('em_desenvolvimento', 'Contrato em Desenvolvimento'),
        ('assinado', 'Contrato Assinado'),
    ]

    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='alinhamento_realizado')
    produtos = models.ManyToManyField(Produto, related_name='contratos')

    def __str__(self):
        produtos_nomes = ', '.join([produto.nome for produto in self.produtos.all()])
        return f"{self.nome} - {self.get_estado_display()} - Produtos: {produtos_nomes}"

class Contratos(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
    contratos = models.ManyToManyField(Contrato, related_name='contratos_registro')

    def __str__(self):
        return f"{self.atividade_registro} - {self.contratos.count()} contratos"
# 15 modelos
class Modelo(models.Model):
    nome = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'

    def __str__(self):
        return self.nome
    
class AtividadeRegistroModelo(models.Model):
    atividade_registro = models.ForeignKey(AtividadeRegistro, on_delete=models.CASCADE)
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

class FormacaoIndigena(models.Model):
    formacao = models.CharField(max_length=255)
    indigena = models.ForeignKey(Indigena, on_delete=models.CASCADE)

    def __str__(self):
        return self.formacao


# FUNAI

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


# SAÚDE INDÍGENA

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


# EDUCAÇÃO INDÍGENA

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