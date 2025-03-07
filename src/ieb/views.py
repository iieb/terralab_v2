import json

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .forms import AtividadeRegistroForm
from .models import Projeto, Componente, Atividade, EquipeProjeto, Indicador, Meta, AtividadeRegistro, Treinados, Leis, Planos, Capacitados, Organizacao, Parceria, Parcerias, Plano, PlanoHistorico, TIs, AreaDireto, AreaGeral, AreaRestrito, Produtos, Produto, Contrato, Contratos, Lei, LeiHistorico, Aplicacao, Mobilizados, Modelo, AtividadeRegistroModelo
from django.views.decorators.csrf import csrf_exempt
import unicodedata
import re
from decimal import Decimal, InvalidOperation
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
import os
from io import BytesIO

def normalize_string(s):
    # Remover acentos e caracteres especiais
    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8')
    # Converter para minúsculas e substituir espaços por underscores
    s = re.sub(r'\s+', '_', s.lower())
    return s

def atividade_registro_view(request):
    if request.method == 'POST':
        form = AtividadeRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            atividade_registro = form.save()

            # Inicialização das variáveis para capturar os dados
            treinados_data = {'total_pessoas': None, 'homens': None, 'mulheres': None, 'jovens': None, 'foco_treinamento': None}
            planos_data = {'nome': '', 'tipo': '', 'situacao': ''}
            capacitados_data = {
                'organizacoes': [],
                'total_organizacoes': 0,
                'foco_capacitacao': None  # Novo campo
            }
            parcerias_data = {'parcerias': [], 'total_parcerias': 0}  # Adicionar suporte para Parcerias
            area_geral_data = {'tis': []}
            area_direto_data = {'tis': []}
            area_restrito_data = {'ti': None, 'area_em_ha': None}
            produtos_data = {'produtos': [], 'total_produtos': 0}
            contratos_data = {'contratos': []}
            leis_data = {'leis': []}
            aplicacao_data = {'total_pessoas': None, 'homens': None, 'mulheres': None, 'jovens': None}
            mobilizados_data = {
                'valor_mobilizado': None,
                'tipo_apoio': None,
                'fonte_apoio': None,
            }
            modelos_data = {
                'modelos': [],   # IDs dos modelos selecionados
                'status': {}     # Dicionário com o status para cada modelo
            }


            treinados_exist = leis_exist = planos_exist = capacitados_exist = parcerias_exist = area_geral_exist = area_direto_exist = area_restrito_exist = produtos_exist = contratos_exist = leis_exist = aplicacao_exist = mobilizados_exist = modelos_exist = False

            # Processamento dos campos enviados pelo formulário
            for key, value in request.POST.items():
                if key.startswith('indicadores_'):
                    try:
                        parts = key.split('_')
                        indicador_id = int(parts[1])
                        field_name = '_'.join(parts[2:])
                        indicador = Indicador.objects.get(id=indicador_id)

                        if indicador.nome.lower() == 'treinados':
                            treinados_exist = True
                            if field_name == 'total_pessoas':
                                treinados_data['total_pessoas'] = int(value)
                            elif field_name == 'homens':
                                treinados_data['homens'] = int(value)
                            elif field_name == 'mulheres':
                                treinados_data['mulheres'] = int(value)
                            elif field_name == 'jovens':
                                treinados_data['jovens'] = int(value)
                            elif field_name == 'foco_treinamento':
                                treinados_data['foco_treinamento'] = value

                        elif indicador.nome.lower() == 'planos':
                            planos_exist = True
                            if field_name == 'nome':
                                planos_data['nome'] = value
                            elif field_name == 'tipo':
                                planos_data['tipo'] = value
                            elif field_name == 'situacao':
                                planos_data['situacao'] = value

                        elif indicador.nome.lower() == 'capacitados':
                            capacitados_exist = True
                            if field_name == 'organizacoes':
                                capacitados_data['organizacoes'].extend(request.POST.getlist(key))
                            elif field_name == 'foco_capacitacao':
                                capacitados_data['foco_capacitacao'] = value

                        elif indicador.nome.lower() == 'parcerias':
                            parcerias_exist = True
                            if field_name == 'parcerias':
                                parcerias_data['parcerias'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'área geral':
                            area_geral_exist = True
                            if field_name == 'tis':
                                area_geral_data['tis'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'área direto':
                            area_direto_exist = True
                            if field_name == 'tis':
                                area_direto_data['tis'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'área restrito':
                            area_restrito_exist = True
                            if field_name == 'ti':
                                area_restrito_data['ti'] = value  # Assumindo que `value` é o ID da TI selecionada
                            elif field_name == 'area_em_ha':
                                valor = value.replace(',', '.')
                                try:
                                    area_restrito_data['area_em_ha'] = Decimal(valor)
                                except (InvalidOperation, ValueError):
                                    area_restrito_data['area_em_ha'] = None  # Ou lidar com o erro de forma apropriada

                        elif indicador.nome.lower() == 'produtos':
                            produtos_exist = True
                            if field_name == 'produtos':
                                produtos_data['produtos'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'contratos':
                            contratos_exist = True
                            if field_name == 'contratos':
                                contratos_data['contratos'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'leis':
                            leis_exist = True
                            if field_name == 'leis':
                                leis_data['leis'].extend(request.POST.getlist(key))

                        elif indicador.nome.lower() == 'aplicação':
                            aplicacao_exist = True
                            if field_name == 'total_pessoas':
                                aplicacao_data['total_pessoas'] = int(value)
                            elif field_name == 'homens':
                                aplicacao_data['homens'] = int(value)
                            elif field_name == 'mulheres':
                                aplicacao_data['mulheres'] = int(value)
                            elif field_name == 'jovens':
                                aplicacao_data['jovens'] = int(value)

                        if indicador.nome.lower() == 'mobilizados':
                            mobilizados_exist = True
                            if field_name == 'valor_mobilizado':
                                mobilizados_data['valor_mobilizado'] = value  # Manter como string para DecimalField
                            elif field_name == 'tipo_apoio':
                                mobilizados_data['tipo_apoio'] = value
                            elif field_name == 'fonte_apoio':
                                mobilizados_data['fonte_apoio'] = value

                        if indicador.nome.lower() == 'modelos':
                            modelos_exist = True
                            if field_name == 'modelos':
                                modelos_data['modelos'].extend(request.POST.getlist(key))
                            elif field_name.startswith('status_modelo_'):
                                modelo_id = field_name.split('status_modelo_')[1]
                                status = value
                                modelos_data['status'][modelo_id] = status
                            elif field_name == 'novos_modelos':
                                novos_modelos = [nome.strip() for nome in value.split(',') if nome.strip()]
                                for nome in novos_modelos:
                                    novo_modelo = Modelo.objects.create(nome=nome)
                                    modelos_data['modelos'].append(str(novo_modelo.id))



                    except (Indicador.DoesNotExist, ValueError) as e:
                        print(f"Erro ao processar o indicador {key}: {e}")
                        continue

            # Salvar dados processados
            if treinados_exist and all(v is not None for v in treinados_data.values()):
                Treinados.objects.create(atividade_registro=atividade_registro, **treinados_data)

            if capacitados_exist and capacitados_data['organizacoes'] and capacitados_data['foco_capacitacao']:
                # Salvar instância de Capacitados
                capacitados_instance = Capacitados(
                    atividade_registro=atividade_registro,
                    foco_capacitacao=capacitados_data['foco_capacitacao']
                )
                capacitados_instance.save()

                # Associar organizações e atualizar total
                capacitados_instance.organizacoes.set(capacitados_data['organizacoes'])
                capacitados_instance.total_organizacoes = capacitados_instance.organizacoes.count()
                capacitados_instance.save()

            if parcerias_exist and parcerias_data['parcerias']:
                parcerias_instance = Parcerias(atividade_registro=atividade_registro)
                parcerias_instance.save()
                parcerias_instance.parcerias.set(parcerias_data['parcerias'])
                parcerias_instance.total_parcerias = len(parcerias_data['parcerias'])
                parcerias_instance.save()

            if planos_exist and planos_data['nome'] and planos_data['tipo'] and planos_data['situacao']:
                # Criar um novo plano associado ao registro de atividade
                Plano.objects.create(
                    atividade_registro=atividade_registro,
                    nome=planos_data['nome'],
                    tipo=planos_data['tipo'],
                    situacao=planos_data['situacao']
                )

            if area_geral_exist and area_geral_data['tis']:
                area_geral_instance = AreaGeral(atividade_registro=atividade_registro)
                area_geral_instance.save()
                area_geral_instance.tis.set(area_geral_data['tis'])
                area_geral_instance.total_tis = area_geral_instance.tis.count()
                area_geral_instance.save()

            if area_direto_exist and area_direto_data['tis']:
                area_direto_instance = AreaDireto(atividade_registro=atividade_registro)
                area_direto_instance.save()
                area_direto_instance.tis.set(area_direto_data['tis'])
                area_direto_instance.total_tis = area_direto_instance.tis.count()
                area_direto_instance.save()

            if area_restrito_exist and area_restrito_data['ti'] and area_restrito_data['area_em_ha']:
                area_restrito_instance = AreaRestrito(
                    atividade_registro=atividade_registro,
                    ti_id=area_restrito_data['ti'],
                    area_em_ha=area_restrito_data['area_em_ha']
                )
                area_restrito_instance.save()

            if produtos_exist and produtos_data['produtos']:
                produtos_instance = Produtos(atividade_registro=atividade_registro)
                produtos_instance.save()
                produtos_instance.produtos.set(produtos_data['produtos'])
                produtos_instance.total_produtos = produtos_instance.produtos.count()
                produtos_instance.save()

            if contratos_exist and contratos_data['contratos']:
                contratos_instance = Contratos(atividade_registro=atividade_registro)
                contratos_instance.save()
                contratos_instance.contratos.set(contratos_data['contratos'])
                contratos_instance.save()

            if leis_exist and leis_data['leis']:
                leis_instance = Leis(atividade_registro=atividade_registro)
                leis_instance.save()
                leis_instance.leis.set(leis_data['leis'])  # Correção aqui
                leis_instance.save()

            if aplicacao_exist and all(v is not None for v in aplicacao_data.values()):
                Aplicacao.objects.create(atividade_registro=atividade_registro, **aplicacao_data)

            if mobilizados_exist and mobilizados_data['valor_mobilizado'] and mobilizados_data['tipo_apoio'] and mobilizados_data['fonte_apoio']:
                Mobilizados.objects.create(atividade_registro=atividade_registro, **mobilizados_data)

            if modelos_exist:
                for modelo_id in modelos_data['modelos']:
                    status = modelos_data['status'].get(modelo_id, '')
                    if status:
                        AtividadeRegistroModelo.objects.create(
                            atividade_registro=atividade_registro,
                            modelo_id=int(modelo_id),
                            status=status
                        )


            atividade_registro = form.save()

            # Capturar o e-mail da organização inserido pelo usuário
            email_organizacao = form.cleaned_data.get('email_organizacao')

            # Enviar e-mail de notificação
            enviar_email_notificacao(atividade_registro.id, email_organizacao)

            messages.success(request, 'Registro de atividade salvo com sucesso!')
            return redirect('atividade_registro_detalhe', pk=atividade_registro.pk)
        else:
            messages.error(request, 'Erro ao salvar o registro de atividade. Verifique os campos e tente novamente.')
            print(form.errors)
    else:
        form = AtividadeRegistroForm()

    # Gerar o dicionário de configuração dos indicadores dinamicamente
    organizacoes = Organizacao.objects.all()
    organizacoes_options = [{'value': org.id, 'label': org.nome} for org in organizacoes]

    parcerias = Parceria.objects.all()
    parcerias_options = [{'value': p.id, 'label': f"{p.nome} - {p.tipo}"} for p in parcerias]

    planos = Plano.objects.all()
    planos_options = [{'value': plano.id, 'label': f'{plano.nome} - {plano.tipo} - {plano.situacao}'} for plano in planos]

    tis_list = TIs.objects.all()
    tis_options = [{'value': ti.id, 'label': ti.nome} for ti in tis_list]

    produtos = Produto.objects.all()
    produtos_options = [{'value': produto.id, 'label': produto.nome} for produto in produtos]

    contratos = Contrato.objects.all()
    contratos_options = [{'value': contrato.id, 'label': str(contrato)} for contrato in contratos]

    leis = Lei.objects.all()
    leis_options = [{'value': lei.id, 'label': str(lei)} for lei in leis]   

    modelos_existentes = Modelo.objects.all()
    modelos_options = [{'value': modelo.id, 'label': modelo.nome} for modelo in modelos_existentes]




    indicadores_config = {
        "treinados": [
            {"name": "total_pessoas", "type": "number", "label": "Total de Pessoas Treinadas"},
            {"name": "homens", "type": "number", "label": "Homens"},
            {"name": "mulheres", "type": "number", "label": "Mulheres"},
            {"name": "jovens", "type": "number", "label": "Jovens"},
            {"name": "foco_treinamento", "type": "select", "label": "Foco do Treinamento", "options": [
                {"value": "implementacao", "label": "Implementação melhorada/monitoramento/vigilância"},
                {"value": "ativ_prod", "label": "Meios de subsistência/cadeia de valor sustentáveis melhorados"},
                {"value": "governanca", "label": "Fortalecimento institucional/capacitação organizacional/governança"}
            ]}
        ],
        "leis": [
            {"name": "leis", "type": "checkbox", "label": "Leis", "options": leis_options}
        ],
        "planos": [
            {"name": "plano", "type": "checkbox", "label": "Planos", "options": planos_options}
        ],
        "capacitados": [
            {"name": "organizacoes", "type": "checkbox", "label": "Organizações", "options": organizacoes_options},
            {"name": "foco_capacitacao", "type": "select", "label": "Foco da Capacitação", "options": [
                {"value": "implementacao", "label": "Implementação melhorada/monitoramento/vigilância"},
                {"value": "ativ_prod", "label": "Meios de subsistência/cadeia de valor sustentáveis melhorados"},
                {"value": "governanca", "label": "Fortalecimento institucional/capacitação organizacional/governança"}
            ]}
        ],
        "parcerias": [
            {"name": "parcerias", "type": "checkbox", "label": "Parcerias", "options": parcerias_options}
        ],
        "area_geral": [
            {
                "name": "tis",
                "type": "checkbox",
                "label": "Selecione as TIs para Área Geral",
                "options": tis_options
            }
        ],
        "area_direto": [
            {
                "name": "tis",
                "type": "checkbox",
                "label": "Selecione as TIs para Área Direto",
                "options": tis_options
            }
        ],
        "area_restrito": [
            {
                "name": "ti",
                "type": "select",
                "label": "Selecione a TI para Área Restrito",
                "options": tis_options  # Certifique-se de que `tis_options` está no formato correto
            },
            {
                "name": "area_em_ha",
                "type": "number",
                "label": "Área em hectares (ha)",
                "step": "0.01"
            }
        ],
        "produtos": [
            {"name": "produtos", "type": "checkbox", "label": "Produtos", "options": produtos_options}
        ],
        "contratos": [
            {"name": "contratos", "type": "checkbox", "label": "Contratos", "options": contratos_options}
        ],
        normalize_string("Aplicação"): [
            {"name": "total_pessoas", "type": "number", "label": "Total de Pessoas"},
            {"name": "homens", "type": "number", "label": "Homens"},
            {"name": "mulheres", "type": "number", "label": "Mulheres"},
            {"name": "jovens", "type": "number", "label": "Jovens"},
        ],  
        "mobilizados": [
            {"name": "valor_mobilizado", "type": "number", "label": "Valor Mobilizado"},
            {"name": "tipo_apoio", "type": "select", "label": "Tipo de Apoio", "options": [
                {"value": "Contribuição em dinheiro", "label": "Contribuição em dinheiro"},
                {"value": "Voluntariado", "label": "Voluntariado"},
                {"value": "Doação do tempo dos funcionários", "label": "Doação do tempo dos funcionários"},
                {"value": "Doação de suprimentos, equipamentos", "label": "Doação de suprimentos, equipamentos"},
                {"value": "Propriedade intelectual", "label": "Propriedade intelectual"},
            ]},
            {"name": "fonte_apoio", "type": "select", "label": "Fonte de Apoio", "options": [
                {"value": "Renda proveniente da atividades/projeto", "label": "Renda proveniente da atividades/projeto"},
                {"value": "Empresas", "label": "Empresas"},
                {"value": "Fundação privada", "label": "Fundação privada"},
                {"value": "Outros doadores (incluindo multilaterais)", "label": "Outros doadores (incluindo multilaterais)"},
                {"value": "Outras organizações sem fins lucrativos", "label": "Outras organizações sem fins lucrativos"},
                {"value": "Indivíduo de alta renda/Investidor anjo", "label": "Indivíduo de alta renda/Investidor anjo"},
                {"value": "OUTRO (especifique)", "label": "OUTRO (especifique)"},
            ]},
        ],
        "modelos": [
            {
                "name": "modelos",
                "type": "checkbox",
                "label": "Selecione os Modelos",
                "options": modelos_options
            },
            {
                "name": "novos_modelos",
                "type": "text",
                "label": "Adicionar Novos Modelos (separados por vírgula)"
            },
            # O campo de status será renderizado dinamicamente no template
        ],
    }

    return render(request, 'atividade_registro_form.html', {
        'form': form,
        'indicadores_config': indicadores_config,  # Passando o dicionário para o template
        'produtos_options': produtos_options,  
    })

def load_componentes(request):
    projeto_id = request.GET.get('projeto')
    componentes = Componente.objects.filter(projeto_id=projeto_id).all()
    componente_data = [{'id': componente.id, 'nome': str(componente)} for componente in componentes]
    return JsonResponse(componente_data, safe=False)

def load_atividades(request):
    componente_id = request.GET.get('componente')
    atividades = Atividade.objects.filter(componente_id=componente_id).all()
    atividade_data = [{'id': atividade.id, 'nome': str(atividade)} for atividade in atividades]
    return JsonResponse(atividade_data, safe=False)

def load_equipes(request):
    projeto_id = request.GET.get('projeto')
    equipes = EquipeProjeto.objects.filter(projeto_id=projeto_id).all()
    equipes_data = [{'id': equipe.id, 'nome': str(equipe)} for equipe in equipes]

    return JsonResponse(equipes_data, safe=False)

def load_equipes_adicionais(request):
    projeto_id = request.GET.get('projeto')
    equipes = EquipeProjeto.objects.filter(projeto_id=projeto_id).all()
    return JsonResponse(list(equipes.values('id', 'equipe__nome')), safe=False)

def load_indicadores(request):
    atividade_id = request.GET.get('atividade')
    indicadores = Indicador.objects.filter(meta__atividade_id=atividade_id).distinct()
    data = [{'id': indicador.id, 'nome': indicador.nome} for indicador in indicadores]
    return JsonResponse(data, safe=False)

def atividade_registro_detalhe_view(request, pk):
    # Busca o registro específico com base na chave primária (pk)
    atividade_registro = get_object_or_404(AtividadeRegistro, pk=pk)
    
    # Obtém os indicadores e outros relacionamentos
    treinados = Treinados.objects.filter(atividade_registro=atividade_registro).first()
    capacitados = Capacitados.objects.filter(atividade_registro=atividade_registro).first()
    parcerias = Parcerias.objects.filter(atividade_registro=atividade_registro).first()
    area_restrito = AreaRestrito.objects.filter(atividade_registro=atividade_registro).first()
    area_direto = AreaDireto.objects.filter(atividade_registro=atividade_registro).first()
    area_geral = AreaGeral.objects.filter(atividade_registro=atividade_registro).first()
    produtos = Produtos.objects.filter(atividade_registro=atividade_registro).first()
    contratos = Contratos.objects.filter(atividade_registro=atividade_registro).first()
    leis = Leis.objects.filter(atividade_registro=atividade_registro).first()
    aplicacao = Aplicacao.objects.filter(atividade_registro=atividade_registro).first()
    mobilizados = Mobilizados.objects.filter(atividade_registro=atividade_registro).first()

    # Renderiza o template passando o registro encontrado e os indicadores
    return render(request, 'atividade_registro_detalhe.html', {
        'atividade_registro': atividade_registro,
        'treinados': treinados,
        'capacitados': capacitados,
        'parcerias': parcerias,
        'area_restrito': area_restrito,
        'area_direto': area_direto,
        'area_geral': area_geral,
        'produtos': produtos,
        'contratos': contratos,
        'leis': leis,
        'aplicacao': aplicacao,
        'mobilizados': mobilizados,
    })

def teste_parcerias_view(request):
    parcerias = Parceria.objects.all()
    return render(request, 'teste_parcerias.html', {'parcerias': parcerias})

def adicionar_parceria(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)

        nome = data.get("nome")
        tipo = data.get("tipo")
        if nome and tipo:
            nova_parceria = Parceria.objects.create(nome=nome, tipo=tipo)
            return JsonResponse({"id": nova_parceria.id, "nome": nova_parceria.nome, "tipo": nova_parceria.tipo})
        else:
            return JsonResponse({"error": "Nome e tipo não fornecidos"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

def adicionar_plano(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)

        nome = data.get("nome")
        tipo = data.get("tipo")
        situacao = data.get("situacao")
        if nome and tipo and situacao:
            novo_plano = Plano.objects.create(nome=nome, tipo=tipo, situacao=situacao)
            return JsonResponse({"id": novo_plano.id, "nome": novo_plano.nome, "tipo": novo_plano.tipo, "situacao": novo_plano.situacao})
        else:
            return JsonResponse({"error": "Nome, tipo e situação não fornecidos"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

def atualizar_situacao_plano(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            plano_id = data.get('plano_id')
            nova_situacao = data.get('situacao')

            plano = get_object_or_404(Plano, id=plano_id)

            # Registrar a alteração no histórico
            PlanoHistorico.objects.create(
                plano=plano,
                situacao_anterior=plano.situacao,
                situacao_nova=nova_situacao,
                usuario=request.user.username  # Se estiver usando autenticação de usuário
            )

            # Atualizar a situação atual do plano
            plano.situacao = nova_situacao
            plano.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        

def adicionar_produto(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)

        nome = data.get("nome")
        if nome:
            novo_produto = Produto.objects.create(nome=nome)
            return JsonResponse({"id": novo_produto.id, "nome": novo_produto.nome})
        else:
            return JsonResponse({"error": "Nome não fornecido"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

def adicionar_contrato(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)

        nome = data.get("nome")
        estado = data.get("estado")
        produtos_ids = data.get("produtos", [])

        if nome and estado:
            novo_contrato = Contrato.objects.create(nome=nome, estado=estado)
            if produtos_ids:
                novo_contrato.produtos.set(produtos_ids)
            return JsonResponse({
                "id": novo_contrato.id,
                "nome": novo_contrato.nome,
                "estado": novo_contrato.get_estado_display(),
                "produtos": list(novo_contrato.produtos.values('id', 'nome'))
            })
        else:
            return JsonResponse({"error": "Nome e estado não fornecidos"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

def atualizar_estado_contrato(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            contrato_id = data.get('contrato_id')
            novo_estado = data.get('estado')

            contrato = get_object_or_404(Contrato, id=contrato_id)

            # Atualizar o estado atual do contrato
            contrato.estado = novo_estado
            contrato.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def adicionar_lei(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)

        nome = data.get("nome")
        tipo = data.get("tipo")
        situacao = data.get("situacao")

        if nome and tipo and situacao:
            nova_lei = Lei.objects.create(nome=nome, tipo=tipo, situacao=situacao)
            return JsonResponse({
                "id": nova_lei.id,
                "nome": nova_lei.nome,
                "tipo": nova_lei.tipo,
                "situacao": nova_lei.situacao,
            })
        else:
            return JsonResponse({"error": "Dados incompletos"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def atualizar_situacao_lei(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lei_id = data.get('lei_id')
            nova_situacao = data.get('situacao')

            lei = get_object_or_404(Lei, id=lei_id)
            situacao_anterior = lei.situacao

            # Atualizar a situação atual da lei
            lei.situacao = nova_situacao
            lei.save()

            # Registrar no histórico (se o modelo LeiHistorico estiver sendo usado)
            LeiHistorico.objects.create(
                lei=lei,
                situacao_anterior=situacao_anterior,
                situacao_nova=nova_situacao,
                usuario=request.user.username  # Ajuste conforme necessário
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def adicionar_modelo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nome = data.get("nome")
            if nome:
                novo_modelo = Modelo.objects.create(nome=nome)
                return JsonResponse({"id": novo_modelo.id, "nome": novo_modelo.nome})
            else:
                return JsonResponse({"error": "Nome não fornecido"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar a solicitação JSON"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)

def atividade_registro_anterior(request, pk):
    # Obter o registro atual
    current_record = get_object_or_404(AtividadeRegistro, id=pk)
    # Encontrar o registro anterior
    previous_record = AtividadeRegistro.objects.filter(id__lt=current_record.id).order_by('-id').first()
    if previous_record:
        return redirect('atividade_registro_detalhe', pk=previous_record.id)
    else:
        # Se não houver registro anterior, redirecionar para o atual ou para uma página específica
        return redirect('atividade_registro_detalhe', pk=current_record.id)

def atividade_registro_proximo(request, pk):
    # Obter o registro atual
    current_record = get_object_or_404(AtividadeRegistro, id=pk)
    # Encontrar o próximo registro
    next_record = AtividadeRegistro.objects.filter(id__gt=current_record.id).order_by('id').first()
    if next_record:
        return redirect('atividade_registro_detalhe', pk=next_record.id)
    else:
        # Se não houver próximo registro, redirecionar para o atual ou para uma página específica
        return redirect('atividade_registro_detalhe', pk=current_record.id)
    

def gerar_pdf(template_src, context_dict):
    # Adiciona 'request': None ao contexto para que os blocos {% if request %} não sejam renderizados
    context_dict.update({'request': None})

    template_str = render_to_string(template_src, context_dict)
    result = BytesIO()

    # Cria o PDF a partir do HTML renderizado
    pdf = pisa.CreatePDF(BytesIO(template_str.encode("utf-8")), dest=result)

    # Verifica se o PDF foi criado com sucesso
    if not pdf.err:
        return result.getvalue()  # Retorna o conteúdo do PDF
    return None

def enviar_email_notificacao(atividade_registro_id, email_organizacao):
    # Buscar o registro de atividade novamente com as relações pré-carregadas
    atividade_registro = AtividadeRegistro.objects.get(id=atividade_registro_id)

    # Obter os indicadores associados manualmente
    parcerias = Parcerias.objects.filter(atividade_registro=atividade_registro)
    treinados = Treinados.objects.filter(atividade_registro=atividade_registro).first()
    capacitados = Capacitados.objects.filter(atividade_registro=atividade_registro).first()
    area_restrito = AreaRestrito.objects.filter(atividade_registro=atividade_registro).first()
    area_direto = AreaDireto.objects.filter(atividade_registro=atividade_registro).first()
    area_geral = AreaGeral.objects.filter(atividade_registro=atividade_registro).first()
    produtos = Produtos.objects.filter(atividade_registro=atividade_registro).first()
    contratos = Contratos.objects.filter(atividade_registro=atividade_registro).first()
    leis = Leis.objects.filter(atividade_registro=atividade_registro).first()
    aplicacao = Aplicacao.objects.filter(atividade_registro=atividade_registro).first()
    mobilizados = Mobilizados.objects.filter(atividade_registro=atividade_registro).first()

    # Criar o contexto do PDF
    pdf_context = {
        'atividade_registro': atividade_registro,
        'parcerias': parcerias,
        'treinados': treinados,
        'capacitados': capacitados,
        'area_restrito': area_restrito,
        'area_direto': area_direto,
        'area_geral': area_geral,
        'produtos': produtos,
        'contratos': contratos,
        'leis': leis,
        'aplicacao': aplicacao,
        'mobilizados': mobilizados,
    }

    pdf_content = gerar_pdf('atividade_registro_pdf.html', pdf_context)

    if pdf_content is None:
        print("Erro ao gerar o PDF do relatório.")
        return

    # Configurar o backend SMTP explicitamente
    backend = EmailBackend(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        fail_silently=False,
    )

    # Construir a mensagem de e-mail
    subject = 'Novo Registro de Atividade'
    message = f"""
    Um novo registro de atividade foi feito:

    Projeto: {atividade_registro.projeto}
    Atividade: {atividade_registro.atividade}
    Data de Início: {atividade_registro.data_inicio}
    Data Final: {atividade_registro.data_final}
    Descrição: {atividade_registro.descricao}
    Local: {atividade_registro.local}

    Em anexo está o relatório detalhado em PDF.

    Por favor, veja os detalhes no sistema.
    """

    # Definir destinatários
    recipient_list = ['monitoramento@iieb.org.br']
    if email_organizacao:
        recipient_list.append(email_organizacao)

    # Criar o email
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
        connection=backend
    )

    # Anexar o PDF ao e-mail
    email.attach('relatorio_atividade.pdf', pdf_content, 'application/pdf')

    # Enviar o e-mail
    email.send()



