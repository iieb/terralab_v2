from django.core.management.base import BaseCommand
from django.db import transaction

from ieb.models import (
    Atividade,
    AtividadeRegistro,
    Componente,
    Equipe,
    EquipeProjeto,
    Financiador,
    Fundo,
    Indicador,
    Instituicao,
    Meta,
    Organizacoes,
    Pessoas,
    Plano,
    Planos,
    Programa,
    Projeto,
    ProjetoIndicador,
    Area,
)


class Command(BaseCommand):
    help = 'Cria ou atualiza massa fictícia Danida para validar o dashboard no navegador.'

    @transaction.atomic
    def handle(self, *args, **options):
        financiador, _ = Financiador.objects.get_or_create(
            sigla='DANIDA',
            defaults={'nome': 'Danish International Development Agency'},
        )
        instituicao, _ = Instituicao.objects.get_or_create(
            nome='Instituição Demo Danida',
            defaults={'sigla': 'IDD'},
        )
        programa, _ = Programa.objects.get_or_create(
            sigla='DANIDA',
            defaults={'nome': 'Programa Danida', 'descricao': 'Programa fictício para validação do dashboard', 'ativo': True},
        )
        equipe, _ = Equipe.objects.get_or_create(
            cpf='00000000000',
            defaults={
                'nome': 'Equipe Demo Danida',
                'cargo': 'Analista',
                'instituicao': instituicao,
            },
        )

        projetos_config = [
            {
                'nome': 'Projeto Danida Territórios Vivos',
                'nome_fant': 'Danida Territórios Vivos',
                'componentes': [
                    {
                        'codigo': 'C1',
                        'nome': 'Governança Territorial',
                        'atividades': [
                            {'codigo': 'A1', 'nome': 'Formação de lideranças', 'descricao': 'Ciclo de formação comunitária'},
                            {'codigo': 'A2', 'nome': 'Fundos de apoio local', 'descricao': 'Estruturação de fundos comunitários'},
                        ],
                    },
                ],
            },
            {
                'nome': 'Projeto Danida Sociobioeconomia',
                'nome_fant': 'Danida Sociobioeconomia',
                'componentes': [
                    {
                        'codigo': 'C1',
                        'nome': 'Economias da Sociobiodiversidade',
                        'atividades': [
                            {'codigo': 'A1', 'nome': 'Fortalecimento de organizações', 'descricao': 'Apoio a organizações comunitárias'},
                            {'codigo': 'A2', 'nome': 'Planos territoriais', 'descricao': 'Acompanhamento de planos e áreas'},
                        ],
                    },
                ],
            },
        ]

        indicadores_config = [
            {
                'codigo': 'DAN-PES',
                'nome': 'Pessoas apoiadas',
                'tipo': 'pessoas',
                'descricao': 'Total de pessoas alcançadas pelas ações Danida',
                'reporte': 'Semestral',
            },
            {
                'codigo': 'DAN-ORG',
                'nome': 'Organizações fortalecidas',
                'tipo': 'organizacoes',
                'descricao': 'Organizações apoiadas no período',
                'reporte': 'Semestral',
            },
            {
                'codigo': 'DAN-ARE',
                'nome': 'Área com gestão fortalecida',
                'tipo': 'area',
                'descricao': 'Hectares acompanhados pelo projeto',
                'reporte': 'Semestral',
            },
            {
                'codigo': 'DAN-FUN',
                'nome': 'Fundos estruturados',
                'tipo': 'fundos',
                'descricao': 'Fundos apoiados pelas ações',
                'reporte': 'Semestral',
            },
            {
                'codigo': 'DAN-PLA',
                'nome': 'Planos acompanhados',
                'tipo': 'planos',
                'descricao': 'Planos com evolução registrada',
                'reporte': 'Semestral',
            },
        ]

        indicadores = {}
        for item in indicadores_config:
            indicador, _ = Indicador.objects.update_or_create(
                codigo=item['codigo'],
                defaults={
                    'nome': item['nome'],
                    'descricao': item['descricao'],
                    'reporte': item['reporte'],
                    'tipo': item['tipo'],
                },
            )
            indicadores[item['tipo']] = indicador

        for projeto_data in projetos_config:
            projeto, _ = Projeto.objects.update_or_create(
                nome_fant=projeto_data['nome_fant'],
                defaults={'nome': projeto_data['nome']},
            )
            projeto.financiadores.add(financiador)
            projeto.programas.add(programa)
            EquipeProjeto.objects.get_or_create(equipe=equipe, projeto=projeto)

            for indicador in indicadores.values():
                ProjetoIndicador.objects.get_or_create(projeto=projeto, indicador=indicador)

            for componente_data in projeto_data['componentes']:
                componente, _ = Componente.objects.update_or_create(
                    projeto=projeto,
                    codigo=componente_data['codigo'],
                    defaults={
                        'nome': componente_data['nome'],
                        'instituicao': instituicao,
                    },
                )

                for atividade_data in componente_data['atividades']:
                    atividade, _ = Atividade.objects.update_or_create(
                        componente=componente,
                        codigo=atividade_data['codigo'],
                        defaults={
                            'nome': atividade_data['nome'],
                            'descricao': atividade_data['descricao'],
                        },
                    )
                    self._seed_activity_data(projeto, componente, atividade, equipe, indicadores)

        self.stdout.write(self.style.SUCCESS('Massa fictícia Danida criada/atualizada com sucesso.'))

    def _seed_activity_data(self, projeto, componente, atividade, equipe, indicadores):
        equipe_projeto = EquipeProjeto.objects.get(projeto=projeto, equipe=equipe)
        prefixo = f"[DASH_DANIDA_FIXTURE:{projeto.nome_fant}:{atividade.codigo}]"

        registros_config = [
            {
                'inicio': '2026-01-15',
                'fim': '2026-01-16',
                'local': 'Território piloto 1',
                'descricao': f'{prefixo} Registro inicial de execução.',
                'pessoas': {'total_pessoas': 18, 'homens': 8, 'mulheres': 10, 'jovens': 6, 'pct_indigenas': 12, 'foco': 'soc_civil'},
                'organizacoes': {'total_organizacoes': 3, 'org_sociedade_civil': 2, 'org_indigenas': 1, 'org_governo': 0, 'foco': 'gov_territorial'},
                'area': {'ha_restrito': 120.5, 'total_ha': 120.5},
                'fundos': {'quantidade': 1, 'valor_total': '15000.00', 'tipo': 'publico'},
                'plano_nome': f'Plano {projeto.nome_fant} {atividade.codigo}',
                'plano_tipo': 'PGTA',
                'plano_situacao': 'em desenvolvimento',
            },
            {
                'inicio': '2026-03-10',
                'fim': '2026-03-11',
                'local': 'Território piloto 2',
                'descricao': f'{prefixo} Registro intermediário de execução.',
                'pessoas': {'total_pessoas': 24, 'homens': 11, 'mulheres': 13, 'jovens': 9, 'pct_indigenas': 16, 'foco': 'defesa_direitos'},
                'organizacoes': {'total_organizacoes': 4, 'org_sociedade_civil': 2, 'org_indigenas': 1, 'org_governo': 1, 'foco': 'sociobiodiversidade'},
                'area': {'ha_restrito': 180.0, 'total_ha': 180.0},
                'fundos': {'quantidade': 2, 'valor_total': '32000.00', 'tipo': 'internacional'},
                'plano_nome': f'Plano {projeto.nome_fant} {atividade.codigo}',
                'plano_tipo': 'Plano de Manejo',
                'plano_situacao': 'adotado',
            },
            {
                'inicio': '2026-05-20',
                'fim': '2026-05-21',
                'local': 'Território piloto 3',
                'descricao': f'{prefixo} Registro avançado de execução.',
                'pessoas': {'total_pessoas': 12, 'homens': 5, 'mulheres': 7, 'jovens': 4, 'pct_indigenas': 8, 'foco': 'soc_civil'},
                'organizacoes': {'total_organizacoes': 2, 'org_sociedade_civil': 1, 'org_indigenas': 1, 'org_governo': 0, 'foco': 'defesa_direitos'},
                'area': {'ha_restrito': 90.0, 'total_ha': 90.0},
                'fundos': {'quantidade': 1, 'valor_total': '12000.00', 'tipo': 'privado'},
                'plano_nome': f'Plano {projeto.nome_fant} {atividade.codigo}',
                'plano_tipo': 'Plano de Adaptação',
                'plano_situacao': 'implementado',
            },
        ]

        metas_config = [
            {'tipo': 'pessoas', 'base': 0, 'meta': 40, 'data_inicio': '2026-01-01', 'data': '2026-06-30'},
            {'tipo': 'organizacoes', 'base': 0, 'meta': 12, 'data_inicio': '2026-01-01', 'data': '2026-06-30'},
            {'tipo': 'area', 'base': 0, 'meta': 500, 'data_inicio': '2026-01-01', 'data': '2026-06-30'},
            {'tipo': 'fundos', 'base': 0, 'meta': 6, 'data_inicio': '2026-01-01', 'data': '2026-06-30'},
            {'tipo': 'planos', 'base': 0, 'meta': 4, 'data_inicio': '2026-01-01', 'data': '2026-06-30'},
        ]

        for meta_data in metas_config:
            Meta.objects.update_or_create(
                atividade=atividade,
                indicador=indicadores[meta_data['tipo']],
                data=meta_data['data'],
                defaults={
                    'base': meta_data['base'],
                    'meta': meta_data['meta'],
                    'data_inicio': meta_data['data_inicio'],
                },
            )

        for registro_data in registros_config:
            registro, _ = AtividadeRegistro.objects.update_or_create(
                atividade=atividade,
                data_inicio=registro_data['inicio'],
                defaults={
                    'projeto': projeto,
                    'componente': componente,
                    'subatividade': None,
                    'equipe_projeto': equipe_projeto,
                    'data_final': registro_data['fim'],
                    'desafios': 'Validação de dashboard',
                    'propostas': 'Ajustes a partir da homologação',
                    'sucesso': 'Dados consistentes para painel',
                    'melhores_praticas': 'Uso de massa fictícia controlada',
                    'descricao': registro_data['descricao'],
                    'local': registro_data['local'],
                    'comentarios': 'Registro criado automaticamente para validação visual do dashboard Danida.',
                    'email_organizacao': 'danida.demo@example.com',
                },
            )

            Pessoas.objects.update_or_create(
                atividade_registro=registro,
                indicador=indicadores['pessoas'],
                defaults=registro_data['pessoas'],
            )
            Organizacoes.objects.update_or_create(
                atividade_registro=registro,
                indicador=indicadores['organizacoes'],
                defaults=registro_data['organizacoes'],
            )
            Area.objects.update_or_create(
                atividade_registro=registro,
                indicador=indicadores['area'],
                defaults=registro_data['area'],
            )
            Fundo.objects.update_or_create(
                atividade_registro=registro,
                indicador=indicadores['fundos'],
                defaults=registro_data['fundos'],
            )

            plano, _ = Plano.objects.update_or_create(
                nome=registro_data['plano_nome'],
                defaults={
                    'tipo': registro_data['plano_tipo'],
                    'situacao': registro_data['plano_situacao'],
                },
            )
            Planos.objects.update_or_create(
                atividade_registro=registro,
                indicador=indicadores['planos'],
                defaults={
                    'plano': plano,
                    'situacao_nova': registro_data['plano_situacao'],
                },
            )
