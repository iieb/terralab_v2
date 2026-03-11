from django.contrib import admin
from .models import *


# ---------------------------------------------------------------------------
# INLINES
# ---------------------------------------------------------------------------

class ProjetoIndicadorInline(admin.TabularInline):
    model = ProjetoIndicador
    extra = 1


class ProjetoOIInline(admin.TabularInline):
    model = ProjetoOI
    extra = 1


class ProjetoTIInline(admin.TabularInline):
    model = ProjetoTI
    extra = 1


class ComponenteInline(admin.TabularInline):
    model = Componente
    extra = 1


class SubatividadeInline(admin.TabularInline):
    model = Subatividade
    extra = 1


class MetaInline(admin.TabularInline):
    model = Meta
    extra = 1


class AtividadeAreaTematicaInline(admin.TabularInline):
    model = AtividadeAreaTematica
    extra = 1


class AtividadeOILocalInline(admin.TabularInline):
    model = AtividadeOILocal
    extra = 1


class AtividadeOIRegionalInline(admin.TabularInline):
    model = AtividadeOIRegional
    extra = 1


class AtividadeTIInline(admin.TabularInline):
    model = AtividadeTI
    extra = 1


# ---------------------------------------------------------------------------
# GESTÃO DE PROJETOS
# ---------------------------------------------------------------------------

class SubprojetoInline(admin.TabularInline):
    model = Projeto
    fk_name = 'projeto_pai'
    extra = 0
    fields = ('nome', 'nome_fant')
    verbose_name = 'Sub-projeto'
    verbose_name_plural = 'Sub-projetos'


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'sigla')


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome_fant', 'nome', 'projeto_pai')
    list_filter = ('programas', 'financiadores')
    search_fields = ('nome', 'nome_fant')
    filter_horizontal = ('programas', 'financiadores')
    inlines = [SubprojetoInline, ProjetoIndicadorInline, ComponenteInline, ProjetoOIInline, ProjetoTIInline]


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    inlines = [SubatividadeInline, MetaInline, AtividadeAreaTematicaInline, AtividadeOILocalInline, AtividadeOIRegionalInline, AtividadeTIInline]


@admin.register(Subatividade)
class SubatividadeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'atividade')
    list_filter = ('atividade__componente__projeto',)
    search_fields = ('nome', 'codigo')


@admin.register(AreaTematica)
class AreaTematicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'tipo', 'reporte')
    list_filter = ('tipo',)
    search_fields = ('nome', 'codigo')


admin.site.register(Componente)
admin.site.register(Financiador)
admin.site.register(Instituicao)
admin.site.register(Equipe)
admin.site.register(EquipeProjeto)
@admin.register(Meta)
class MetaAdmin(admin.ModelAdmin):
    list_display = ('atividade', 'indicador', 'base', 'meta', 'data', 'get_realizado', 'get_percentual')
    list_filter = ('indicador__tipo', 'atividade__componente__projeto')
    search_fields = ('atividade__nome', 'indicador__nome')

    @admin.display(description='Realizado')
    def get_realizado(self, obj):
        return obj.realizado

    @admin.display(description='%')
    def get_percentual(self, obj):
        return f"{obj.percentual}%"
admin.site.register(ProjetoOI)
admin.site.register(ProjetoTI)
admin.site.register(ProjetoIndicador)
admin.site.register(AtividadeAreaTematica)
admin.site.register(AtividadeOILocal)
admin.site.register(AtividadeOIRegional)
admin.site.register(AtividadeTI)

# ---------------------------------------------------------------------------
# ORGANIZAÇÕES INDÍGENAS
# ---------------------------------------------------------------------------

admin.site.register(OIsRegional)
admin.site.register(OIsLocal)
admin.site.register(OIRegLoc)
admin.site.register(TIs)
admin.site.register(Aldeia)
admin.site.register(Indigena)
admin.site.register(FormacaoIndigena)
admin.site.register(IGATI)
admin.site.register(TIsIGATI)

# ---------------------------------------------------------------------------
# REGISTROS DE ATIVIDADE E INDICADORES
# ---------------------------------------------------------------------------

admin.site.register(AtividadeRegistro)
admin.site.register(Treinados)
admin.site.register(Capacitados)
admin.site.register(Aplicacao)
admin.site.register(AreaRestrito)
admin.site.register(AreaDireto)
admin.site.register(AreaGeral)
admin.site.register(Leis)
admin.site.register(Lei)
admin.site.register(LeiHistorico)
admin.site.register(Planos)
admin.site.register(Plano)
admin.site.register(PlanoHistorico)
admin.site.register(Parcerias)
admin.site.register(Parceria)
admin.site.register(Mobilizados)
admin.site.register(Produtos)
admin.site.register(Produto)
admin.site.register(Contratos)
admin.site.register(Contrato)
admin.site.register(Modelo)
admin.site.register(AtividadeRegistroModelo)
admin.site.register(Organizacao)

# ---------------------------------------------------------------------------
# FUNAI / SAÚDE / EDUCAÇÃO
# ---------------------------------------------------------------------------

admin.site.register(CR)
admin.site.register(CTL)
admin.site.register(DSEI)
admin.site.register(Posto)
admin.site.register(Casai)
admin.site.register(Polo)
admin.site.register(AIS)
admin.site.register(Escola)
admin.site.register(Professores)