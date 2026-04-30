from django.core.management.base import BaseCommand
from ieb.models import Indicador

INDICADORES_DANIDA = [
    # ── FUNDOS ────────────────────────────────────────────────────────
    {
        "codigo":   "DANIDA-F01",
        "nome":     "Número de chamadas do fundo Rutî",
        "descricao": "Chamadas realizadas pelo fundo comunitário Rutî ao longo do projeto",
        "reporte":  "Anual",
        "tipo":     "fundos",
    },

    # ── ÁREA ──────────────────────────────────────────────────────────
    {
        "codigo":   "DANIDA-A01",
        "nome":     "Hectares de agroflorestas implementados",
        "descricao": "Área total em hectares com sistemas agroflorestais implantados",
        "reporte":  "Anual",
        "tipo":     "area",
        "desag_restrito": True,
    },
    {
        "codigo":   "DANIDA-A02",
        "nome":     "Hectares de TIs com autonomia no monitoramento e gestão da informação",
        "descricao": "Área de Terras Indígenas cujas comunidades possuem autonomia em monitoramento",
        "reporte":  "Anual",
        "tipo":     "area",
        "desag_direto": True,
        "desag_ti":     True,
    },

    # ── ORGANIZAÇÕES ──────────────────────────────────────────────────
    {
        "codigo":   "DANIDA-O01",
        "nome":     "OIs com aumento no acesso a políticas públicas para geração de renda",
        "descricao": "Organizações Indígenas que ampliaram acesso a políticas públicas",
        "reporte":  "Anual",
        "tipo":     "organizacoes",
        "desag_org_indigenas": True,
        "tem_foco":            True,
    },
    {
        "codigo":   "DANIDA-O02",
        "nome":     "OIs com melhoria na gestão organizacional e participação ativa em incidência política para proteção territorial",
        "descricao": "OIs com avanços em gestão interna e incidência política territorial",
        "reporte":  "Anual",
        "tipo":     "organizacoes",
        "desag_org_indigenas": True,
        "tem_foco":            True,
    },

    # ── PESSOAS ───────────────────────────────────────────────────────
    {
        "codigo":   "DANIDA-P01",
        "nome":     "Castanheiros com aumento na geração de renda",
        "descricao": "Extrativistas castanheiros que aumentaram a geração de renda",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },
    {
        "codigo":   "DANIDA-P02",
        "nome":     "Indígenas criadores de gado com aumento da geração de renda",
        "descricao": "Indígenas que criam gado e aumentaram a geração de renda",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },
    {
        "codigo":   "DANIDA-P03",
        "nome":     "Indígenas realizando ações de monitoramento e proteção territorial",
        "descricao": "Indígenas ativos em monitoramento e vigilância do território",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },
    {
        "codigo":   "DANIDA-P04",
        "nome":     "Indígenas treinados para promover ações de mitigação de mudança climática",
        "descricao": "Indígenas capacitados em ações de mitigação climática",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },
    {
        "codigo":   "DANIDA-P05",
        "nome":     "Indígenas treinados para diversificação da produção e cooperativismo para segurança alimentar",
        "descricao": "Indígenas treinados em produção diversificada e cooperativismo",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },
    {
        "codigo":   "DANIDA-P06",
        "nome":     "Indivíduos treinados em áreas relacionadas ao fortalecimento institucional de OIs",
        "descricao": "Pessoas capacitadas para fortalecer a gestão e incidência de OIs",
        "reporte":  "Anual",
        "tipo":     "pessoas",
        "desag_homens":       True,
        "desag_mulheres":     True,
        "desag_jovens":       True,
        "desag_pct_indigenas": True,
        "tem_foco":           True,
    },

    # ── PLANOS ────────────────────────────────────────────────────────
    {
        "codigo":   "DANIDA-PL01",
        "nome":     "Planos de adaptação a mudanças climáticas desenvolvidos e implementados",
        "descricao": "Planos de adaptação climática com ações em andamento ou concluídas",
        "reporte":  "Anual",
        "tipo":     "planos",
    },
    {
        "codigo":   "DANIDA-PL02",
        "nome":     "PGTAs com ações implementadas para mitigação das mudanças climáticas",
        "descricao": "Planos de Gestão Territorial e Ambiental com ações climáticas implementadas",
        "reporte":  "Anual",
        "tipo":     "planos",
    },
    {
        "codigo":   "DANIDA-PL03",
        "nome":     "Plano de negócios da pecuária sustentável desenvolvida",
        "descricao": "Planos de negócios para pecuária sustentável elaborados",
        "reporte":  "Anual",
        "tipo":     "planos",
    },
]


class Command(BaseCommand):
    help = "Cria os 14 indicadores do projeto Danida (idempotente via codigo)"

    def handle(self, *args, **options):
        criados = 0
        existentes = 0

        for dados in INDICADORES_DANIDA:
            codigo = dados.pop("codigo")
            obj, created = Indicador.objects.get_or_create(
                codigo=codigo,
                defaults=dados,
            )
            if created:
                criados += 1
                self.stdout.write(self.style.SUCCESS(f"  criado: [{obj.tipo}] {obj.nome}"))
            else:
                existentes += 1
                self.stdout.write(f"  já existe: {codigo}")

        self.stdout.write(self.style.SUCCESS(
            f"\nConcluído: {criados} criados, {existentes} já existiam."
        ))
        if criados or existentes:
            self.stdout.write(
                "\nPróximo passo: crie o Projeto Danida no Admin e vincule os "
                "indicadores via ProjetoIndicador."
            )
