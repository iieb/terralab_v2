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

    def get_formset(self, request, obj=None, **kwargs):
        self._projeto_id = obj.componente.projeto_id if (obj and obj.componente_id) else None
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'indicador' and getattr(self, '_projeto_id', None):
            kwargs['queryset'] = Indicador.objects.filter(
                projeto_indicadores__projeto_id=self._projeto_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MetaFinanciadorInline(admin.TabularInline):
    model = MetaFinanciador
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        self._projeto_id = obj.componente.projeto_id if (obj and obj.componente_id) else None
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'indicador_financiador' and getattr(self, '_projeto_id', None):
            kwargs['queryset'] = IndicadorFinanciador.objects.filter(
                projeto_indicadores_fin__projeto_id=self._projeto_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProjetoIndicadorFinInline(admin.TabularInline):
    model = ProjetoIndicadorFin
    extra = 1


class IndicadorFinanciadorInline(admin.TabularInline):
    model = IndicadorFinanciador
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
    inlines = [SubprojetoInline, ProjetoIndicadorInline, ProjetoIndicadorFinInline, ComponenteInline, ProjetoOIInline, ProjetoTIInline]


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    inlines = [SubatividadeInline, MetaInline, MetaFinanciadorInline, AtividadeAreaTematicaInline, AtividadeOILocalInline, AtividadeOIRegionalInline, AtividadeTIInline]


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
    fieldsets = (
        (None, {'fields': ('nome', 'codigo', 'tipo', 'descricao', 'reporte')}),
        ('Desagregações — Pessoas', {
            'fields': (
                'desag_homens', 'desag_mulheres', 'desag_jovens',
                'desag_pct', 'desag_pct_indigenas', 'desag_pct_extrativistas',
                'desag_pct_quilombolas', 'desag_servidor_publico', 'tem_foco',
            ),
            'classes': ('collapse',),
        }),
        ('Desagregações — Organizações', {
            'fields': ('desag_org_sc', 'desag_org_indigenas', 'desag_org_extrativistas'),
            'classes': ('collapse',),
            'description': 'tem_foco acima também se aplica a organizações.',
        }),
        ('Desagregações — Área', {
            'fields': ('desag_restrito', 'desag_direto', 'desag_indireto'),
            'classes': ('collapse',),
        }),
        ('Seletores de Área Protegida', {
            'fields': ('desag_ti', 'desag_uc', 'desag_pa', 'desag_tuc'),
            'classes': ('collapse',),
            'description': 'Usados por tipo=area (modos direto/indireto) e tipo=areas_protegidas.',
        }),
        ('Desagregações — Eventos', {
            'fields': (
                'desag_formacoes', 'desag_seminarios',
                'desag_encontros', 'desag_reunioes', 'desag_participantes',
            ),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Componente)
@admin.register(Financiador)
class FinanciadorAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome')
    search_fields = ('nome', 'sigla')
    inlines = [IndicadorFinanciadorInline]


@admin.register(IndicadorFinanciador)
class IndicadorFinanciadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'tipo', 'financiador')
    list_filter = ('tipo', 'financiador')
    search_fields = ('nome', 'codigo')
    fieldsets = (
        (None, {'fields': ('financiador', 'nome', 'codigo', 'tipo', 'descricao', 'reporte')}),
        ('Desagregações — Pessoas', {
            'fields': (
                'desag_homens', 'desag_mulheres', 'desag_jovens',
                'desag_pct', 'desag_pct_indigenas', 'desag_pct_extrativistas',
                'desag_pct_quilombolas', 'desag_servidor_publico', 'tem_foco',
            ),
            'classes': ('collapse',),
        }),
        ('Desagregações — Organizações', {
            'fields': ('desag_org_sc', 'desag_org_indigenas', 'desag_org_extrativistas'),
            'classes': ('collapse',),
            'description': 'tem_foco acima também se aplica a organizações.',
        }),
        ('Desagregações — Área', {
            'fields': ('desag_restrito', 'desag_direto', 'desag_indireto'),
            'classes': ('collapse',),
        }),
        ('Seletores de Área Protegida', {
            'fields': ('desag_ti', 'desag_uc', 'desag_pa', 'desag_tuc'),
            'classes': ('collapse',),
            'description': 'Usados por tipo=area (modos direto/indireto) e tipo=areas_protegidas.',
        }),
        ('Desagregações — Eventos', {
            'fields': (
                'desag_formacoes', 'desag_seminarios',
                'desag_encontros', 'desag_reunioes', 'desag_participantes',
            ),
            'classes': ('collapse',),
        }),
    )
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
admin.site.register(ProjetoIndicadorFin)
admin.site.register(MetaFinanciador)
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
class PlanoHistoricoInline(admin.TabularInline):
    model = PlanoHistorico
    extra = 0
    readonly_fields = ('situacao_anterior', 'situacao_nova', 'data_alteracao', 'usuario')
    can_delete = False


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'situacao')
    list_filter = ('tipo', 'situacao')
    search_fields = ('nome',)
    filter_horizontal = ('tis',)
    inlines = [PlanoHistoricoInline]


@admin.register(Planos)
class PlanosAdmin(admin.ModelAdmin):
    list_display = ('atividade_registro', 'indicador', 'plano', 'situacao_anterior', 'situacao_nova')
    list_filter = ('situacao_nova',)
    raw_id_fields = ('atividade_registro', 'indicador', 'plano')


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