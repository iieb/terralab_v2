import json
import os

from django.core.management.base import BaseCommand, CommandError

from ieb.models import Atividade, Componente, Instituicao, Projeto, Subatividade

JSON_DEFAULT = '/Users/eduardo/Documents/IEB/dinamarca/atividades.json'


def _truncar(texto, limite=255):
    if len(texto) <= limite:
        return texto
    return texto[: limite - 3] + '...'


class Command(BaseCommand):
    help = (
        "Importa componentes, atividades e subatividades do projeto Dinamarca "
        "a partir do atividades.json (idempotente)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            default=JSON_DEFAULT,
            help=f'Caminho para o arquivo JSON (padrão: {JSON_DEFAULT})',
        )
        parser.add_argument(
            '--instituicao',
            type=int,
            help='ID da Instituicao para os componentes (padrão: primeira disponível)',
        )

    def handle(self, *args, **options):
        json_path = options['json']

        if not os.path.exists(json_path):
            raise CommandError(f'Arquivo não encontrado: {json_path}')

        # ── Projeto Dinamarca ────────────────────────────────────────────
        qs_projeto = Projeto.objects.filter(nome_fant__icontains='Dinamarca')
        if not qs_projeto.exists():
            raise CommandError(
                'Projeto "Dinamarca" não encontrado. Cadastre-o no admin antes de importar.'
            )
        if qs_projeto.count() > 1:
            lista = ', '.join(f'[{p.pk}] {p.nome_fant}' for p in qs_projeto)
            raise CommandError(
                f'Múltiplos projetos encontrados com "Dinamarca": {lista}. '
                'Use o nome exato ou refine o cadastro.'
            )
        projeto = qs_projeto.get()
        self.stdout.write(f'Projeto: [{projeto.pk}] {projeto.nome_fant}')

        # ── Instituição ──────────────────────────────────────────────────
        if options['instituicao']:
            try:
                instituicao = Instituicao.objects.get(pk=options['instituicao'])
            except Instituicao.DoesNotExist:
                raise CommandError(
                    f'Instituição com ID {options["instituicao"]} não encontrada.'
                )
        else:
            instituicao = Instituicao.objects.first()
            if not instituicao:
                raise CommandError(
                    'Nenhuma Instituição cadastrada. Crie uma antes de importar, '
                    'ou passe --instituicao <ID>.'
                )
            self.stdout.write(
                self.style.WARNING(
                    f'Instituição não informada — usando padrão: [{instituicao.pk}] {instituicao.nome}\n'
                    'Use --instituicao <ID> para especificar outra.'
                )
            )

        # ── Carregar JSON ────────────────────────────────────────────────
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        comp_criados = comp_exist = 0
        ativ_criados = ativ_exist = 0
        sub_criados  = sub_exist  = 0

        for comp_data in data:
            cod_comp  = comp_data['cod_componente']
            nome_comp = _truncar(comp_data['componente'])

            componente, created = Componente.objects.get_or_create(
                projeto=projeto,
                codigo=cod_comp,
                defaults={
                    'nome': nome_comp,
                    'instituicao': instituicao,
                },
            )
            if created:
                comp_criados += 1
                self.stdout.write(self.style.SUCCESS(f'  [COMP +] {cod_comp}: {nome_comp[:60]}'))
            else:
                comp_exist += 1
                self.stdout.write(f'  [COMP =] {cod_comp} (já existe)')

            for ativ_data in comp_data.get('atividades', []):
                cod_ativ  = ativ_data['cod_atividade']
                texto_ativ = ativ_data['atividade']

                atividade, created = Atividade.objects.get_or_create(
                    componente=componente,
                    codigo=cod_ativ,
                    defaults={
                        'nome': _truncar(texto_ativ),
                        'descricao': _truncar(texto_ativ),
                    },
                )
                if created:
                    ativ_criados += 1
                    self.stdout.write(self.style.SUCCESS(f'    [ATIV +] {cod_ativ}'))
                else:
                    ativ_exist += 1
                    self.stdout.write(f'    [ATIV =] {cod_ativ} (já existe)')

                for sub_data in ativ_data.get('subatividades', []):
                    cod_sub  = sub_data['cod_subatividade']
                    desc_sub = sub_data['descricao']

                    _, created = Subatividade.objects.get_or_create(
                        atividade=atividade,
                        codigo=cod_sub,
                        defaults={
                            'nome': _truncar(desc_sub),
                            'descricao': _truncar(desc_sub),
                        },
                    )
                    if created:
                        sub_criados += 1
                        self.stdout.write(self.style.SUCCESS(f'      [SUB +] {cod_sub}'))
                    else:
                        sub_exist += 1
                        self.stdout.write(f'      [SUB =] {cod_sub} (já existe)')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Concluído — '
            f'Componentes: {comp_criados} criados / {comp_exist} existentes | '
            f'Atividades: {ativ_criados} criadas / {ativ_exist} existentes | '
            f'Subatividades: {sub_criados} criadas / {sub_exist} existentes'
        ))
