import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AtividadeRegistroForm
from .models import (
    Programa, Projeto, Componente, Atividade, EquipeProjeto,
    Indicador, IndicadorFinanciador, Meta, MetaFinanciador,
    AtividadeRegistro, AtividadeRegistroFoto, AtividadeRegistroListaPresenca,
    Pessoas, Organizacoes, Area, AreasProtegidas, Evento, Rede, PequenoProjeto, Fundo, Outro,
    Leis, Planos, Parceria, Parcerias, Plano, PlanoHistorico,
    TIs, UC, PA, TUC,
    Produtos, Produto, Contrato, Contratos,
    Lei, LeiHistorico, Mobilizados, Modelo, AtividadeRegistroModelo,
)
from django.views.decorators.csrf import csrf_exempt
import unicodedata
import re
from decimal import Decimal, InvalidOperation
from django.db import transaction
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
    return _atividade_registro_process(request, template='atividade_registro_form.html')


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

def load_subatividades(request):
    atividade_id = request.GET.get('atividade')
    from .models import Subatividade
    subatividades = Subatividade.objects.filter(atividade_id=atividade_id)
    data = [{'id': s.id, 'nome': str(s)} for s in subatividades]
    return JsonResponse(data, safe=False)

def load_equipes(request):
    projeto_id = request.GET.get('projeto')
    equipes = EquipeProjeto.objects.filter(projeto_id=projeto_id).all()
    equipes_data = [{'id': equipe.id, 'nome': str(equipe)} for equipe in equipes]

    return JsonResponse(equipes_data, safe=False)

def load_equipes_adicionais(request):
    projeto_id = request.GET.get('projeto')
    equipes = EquipeProjeto.objects.filter(projeto_id=projeto_id).all()
    return JsonResponse(list(equipes.values('id', 'equipe__nome')), safe=False)

@login_required
def load_indicadores(request):
    atividade_id = request.GET.get('atividade')
    projeto_id = request.GET.get('projeto')

    # Indicadores base
    base_qs = Indicador.objects.all()
    if projeto_id:
        base_qs = base_qs.filter(projeto_indicadores__projeto_id=projeto_id)
    if atividade_id:
        base_qs = base_qs.filter(meta__atividade_id=atividade_id)

    # Indicadores de financiador
    fin_qs = IndicadorFinanciador.objects.all()
    if projeto_id:
        fin_qs = fin_qs.filter(projeto_indicadores_fin__projeto_id=projeto_id)
    if atividade_id:
        fin_qs = fin_qs.filter(metas__atividade_id=atividade_id)

    planos_qs = Plano.objects.all()
    if projeto_id:
        planos_qs = planos_qs.filter(tis__projetoti__projeto_id=projeto_id).distinct()
    available_plans = list(planos_qs.values('id', 'nome', 'situacao', 'tipo'))

    DESAG_FIELDS = [
        'desag_homens', 'desag_mulheres', 'desag_jovens',
        'desag_pct', 'desag_pct_indigenas', 'desag_pct_extrativistas', 'desag_pct_quilombolas',
        'desag_servidor_publico', 'tem_foco',
        'desag_org_sc', 'desag_org_indigenas', 'desag_org_extrativistas',
        'desag_restrito', 'desag_direto', 'desag_indireto',
        'desag_ti', 'desag_uc', 'desag_pa', 'desag_tuc',
        'desag_formacoes', 'desag_seminarios', 'desag_encontros', 'desag_reunioes',
        'desag_participantes',
    ]

    data = [
        {
            'id': i.id, 'nome': i.nome, 'tipo': i.tipo,
            'available_plans': available_plans if i.tipo == 'planos' else None,
            'financiador_nome': None, 'is_fin': False,
            'desagregacoes': {f: getattr(i, f) for f in DESAG_FIELDS},
        }
        for i in base_qs.distinct()
    ] + [
        {
            'id': i.id, 'nome': i.nome, 'tipo': i.tipo,
            'available_plans': available_plans if i.tipo == 'planos' else None,
            'financiador_nome': i.financiador.sigla, 'is_fin': True,
            'desagregacoes': {f: getattr(i, f) for f in DESAG_FIELDS},
        }
        for i in fin_qs.select_related('financiador').distinct()
    ]
    return JsonResponse(data, safe=False)

def atividade_registro_detalhe_view(request, pk):
    atividade_registro = get_object_or_404(AtividadeRegistro, pk=pk)

    return render(request, 'atividade_registro_detalhe.html', {
        'atividade_registro': atividade_registro,
        'fotos': atividade_registro.fotos_set.all(),
        'listas_presenca': atividade_registro.listas_presenca_set.all(),
        'pessoas': Pessoas.objects.filter(atividade_registro=atividade_registro),
        'organizacoes': Organizacoes.objects.filter(atividade_registro=atividade_registro),
        'area': Area.objects.filter(atividade_registro=atividade_registro),
        'areas_protegidas': AreasProtegidas.objects.filter(atividade_registro=atividade_registro),
        'eventos': Evento.objects.filter(atividade_registro=atividade_registro),
        'redes': Rede.objects.filter(atividade_registro=atividade_registro),
        'pequenos_projetos': PequenoProjeto.objects.filter(atividade_registro=atividade_registro),
        'fundos': Fundo.objects.filter(atividade_registro=atividade_registro),
        'outro': Outro.objects.filter(atividade_registro=atividade_registro),
        'parcerias': Parcerias.objects.filter(atividade_registro=atividade_registro).first(),
        'planos': Planos.objects.filter(atividade_registro=atividade_registro).select_related('plano'),
        'produtos': Produtos.objects.filter(atividade_registro=atividade_registro).first(),
        'contratos': Contratos.objects.filter(atividade_registro=atividade_registro).first(),
        'leis': Leis.objects.filter(atividade_registro=atividade_registro).first(),
        'mobilizados': Mobilizados.objects.filter(atividade_registro=atividade_registro).first(),
        'modelos': AtividadeRegistroModelo.objects.filter(atividade_registro=atividade_registro).select_related('modelo'),
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
    atividade_registro = AtividadeRegistro.objects.get(id=atividade_registro_id)

    pdf_context = {
        'atividade_registro': atividade_registro,
        'fotos': atividade_registro.fotos_set.all(),
        'listas_presenca': atividade_registro.listas_presenca_set.all(),
        'pessoas': Pessoas.objects.filter(atividade_registro=atividade_registro),
        'organizacoes': Organizacoes.objects.filter(atividade_registro=atividade_registro),
        'area': Area.objects.filter(atividade_registro=atividade_registro),
        'areas_protegidas': AreasProtegidas.objects.filter(atividade_registro=atividade_registro),
        'eventos': Evento.objects.filter(atividade_registro=atividade_registro),
        'parcerias': Parcerias.objects.filter(atividade_registro=atividade_registro).first(),
        'planos': Planos.objects.filter(atividade_registro=atividade_registro).select_related('plano'),
        'produtos': Produtos.objects.filter(atividade_registro=atividade_registro).first(),
        'contratos': Contratos.objects.filter(atividade_registro=atividade_registro).first(),
        'leis': Leis.objects.filter(atividade_registro=atividade_registro).first(),
        'mobilizados': Mobilizados.objects.filter(atividade_registro=atividade_registro).first(),
        'modelos': AtividadeRegistroModelo.objects.filter(atividade_registro=atividade_registro).select_related('modelo'),
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
    recipient_list = [settings.MONITORING_EMAIL]
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

    # Montar nome do PDF
    def _slug(text):
        text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^\w]', '_', text)
        return re.sub(r'_+', '_', text).strip('_')

    ar = atividade_registro
    partes = [_slug(ar.projeto.nome_fant), _slug(ar.atividade.codigo)]
    if ar.subatividade:
        partes.append(_slug(ar.subatividade.codigo))
    partes.append(ar.data_inicio.strftime('%Y%m%d'))
    partes.append(_slug(ar.equipe_projeto.equipe.nome))
    pdf_filename = '_'.join(partes) + '.pdf'

    # Anexar o PDF ao e-mail
    email.attach(pdf_filename, pdf_content, 'application/pdf')

    # Enviar o e-mail
    email.send()

def atividade_registro_view_v2(request):
    """Versão v2 do formulário de registro — mesmo processamento, novo template."""
    return _atividade_registro_process(request, template='atividade_registro_form_v2.html')


def _atividade_registro_process(request, template='atividade_registro_form.html'):
    if request.method == 'POST':
        form = AtividadeRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            # Bug A fix: only one form.save(); all DB writes inside atomic block
            with transaction.atomic():
                atividade_registro = form.save()

                for foto in request.FILES.getlist('fotos'):
                    AtividadeRegistroFoto.objects.create(atividade_registro=atividade_registro, foto=foto)
                for lista in request.FILES.getlist('lista_presenca'):
                    AtividadeRegistroListaPresenca.objects.create(atividade_registro=atividade_registro, arquivo=lista)

                # One dict per indicador_id, keyed by tipo
                pessoas_map          = {}  # {id: {total_pessoas, homens, mulheres, jovens, ...}}
                organizacoes_map     = {}  # {id: {total_organizacoes, org_sc, org_ind, org_ext, foco}}
                area_map             = {}  # {id: {ha_restrito, tis, ucs, pas, tucs}}
                areas_protegidas_map = {}  # {id: {tis, ucs, pas, tucs}}
                eventos_map          = {}  # {id: {formacoes, seminarios, encontros, reunioes, participantes}}
                redes_map            = {}  # {id: {nome, tipo, quantidade}}
                pequenos_projetos_map = {} # {id: {quantidade, tipo, tema, valor_total}}
                fundos_map           = {}  # {id: {quantidade, valor_total, tipo}}
                outro_map            = {}  # {id: {descricao, valor}}
                planos_map           = {}  # {id: {situacao_nova, plano_id}}
                parcerias_map        = {}  # {id: {parcerias: [ids]}}
                produtos_map         = {}  # {id: {produtos: [ids]}}
                contratos_map        = {}  # {id: {contratos: [ids]}}
                leis_map             = {}  # {id: {leis: [ids]}}
                mobilizados_map      = {}  # {id: {valor_mobilizado, tipo_apoio, fonte_apoio}}
                modelos_map          = {}  # {id: {modelos: [], status: {}}}
                indicadores_por_id   = {}  # {id: Indicador obj}

                # Parallel maps for IndicadorFinanciador (fin_ prefix)
                fin_pessoas_map          = {}
                fin_organizacoes_map     = {}
                fin_area_map             = {}
                fin_areas_protegidas_map = {}
                fin_eventos_map          = {}
                fin_redes_map            = {}
                fin_pequenos_projetos_map = {}
                fin_fundos_map           = {}
                fin_outro_map            = {}
                fin_parcerias_map        = {}
                fin_produtos_map         = {}
                fin_contratos_map        = {}
                fin_leis_map             = {}
                fin_mobilizados_map      = {}
                indicadores_fin_por_id   = {}  # {id: IndicadorFinanciador obj}

                for key in request.POST:
                    if not key.startswith('indicadores_'):
                        continue

                    is_fin = key.startswith('indicadores_fin_')
                    try:
                        if is_fin:
                            parts = key.split('_', 3)   # ['indicadores', 'fin', '{id}', '{field}']
                            indicador_fin_id = int(parts[2])
                            field_name = parts[3]
                            ind_fin = IndicadorFinanciador.objects.get(id=indicador_fin_id)
                            indicadores_fin_por_id[indicador_fin_id] = ind_fin
                            tipo = ind_fin.tipo
                        else:
                            parts = key.split('_', 2)
                            indicador_id = int(parts[1])
                            field_name = parts[2]
                            indicador = Indicador.objects.get(id=indicador_id)
                            indicadores_por_id[indicador_id] = indicador
                            tipo = indicador.tipo
                    except (ValueError, IndexError, Indicador.DoesNotExist, IndicadorFinanciador.DoesNotExist) as e:
                        logger.warning("Indicador inválido no POST de AtividadeRegistro — chave=%s erro=%s", key, e)
                        continue

                    value = request.POST[key]
                    _id   = indicador_fin_id if is_fin else indicador_id

                    # ── helpers for int/float parsing ──────────────────────────
                    def _int(v):
                        try: return int(v)
                        except (ValueError, TypeError): return None

                    def _float(v):
                        try: return float(str(v).replace(',', '.'))
                        except (ValueError, TypeError): return None

                    if tipo == 'pessoas':
                        _m = fin_pessoas_map if is_fin else pessoas_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'total_pessoas': d['total_pessoas'] = _int(value) or 0
                        elif field_name == 'homens': d['homens'] = _int(value)
                        elif field_name == 'mulheres': d['mulheres'] = _int(value)
                        elif field_name == 'jovens': d['jovens'] = _int(value)
                        elif field_name == 'pct_indigenas': d['pct_indigenas'] = _int(value)
                        elif field_name == 'pct_extrativistas': d['pct_extrativistas'] = _int(value)
                        elif field_name == 'pct_quilombolas': d['pct_quilombolas'] = _int(value)
                        elif field_name == 'servidor_publico': d['servidor_publico'] = _int(value)
                        elif field_name == 'foco': d['foco'] = value

                    elif tipo == 'organizacoes':
                        _m = fin_organizacoes_map if is_fin else organizacoes_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'total_organizacoes': d['total_organizacoes'] = _int(value) or 0
                        elif field_name == 'org_sociedade_civil': d['org_sociedade_civil'] = _int(value)
                        elif field_name == 'org_indigenas': d['org_indigenas'] = _int(value)
                        elif field_name == 'org_extrativistas': d['org_extrativistas'] = _int(value)
                        elif field_name == 'foco': d['foco'] = value

                    elif tipo == 'area':
                        _m = fin_area_map if is_fin else area_map
                        d = _m.setdefault(_id, {'tis': [], 'ucs': [], 'pas': [], 'tucs': []})
                        if field_name == 'ha_restrito': d['ha_restrito'] = _float(value)
                        elif field_name == 'tis': d['tis'].extend(request.POST.getlist(key))
                        elif field_name == 'ucs': d['ucs'].extend(request.POST.getlist(key))
                        elif field_name == 'pas': d['pas'].extend(request.POST.getlist(key))
                        elif field_name == 'tucs': d['tucs'].extend(request.POST.getlist(key))

                    elif tipo == 'areas_protegidas':
                        _m = fin_areas_protegidas_map if is_fin else areas_protegidas_map
                        d = _m.setdefault(_id, {'tis': [], 'ucs': [], 'pas': [], 'tucs': []})
                        if field_name == 'tis': d['tis'].extend(request.POST.getlist(key))
                        elif field_name == 'ucs': d['ucs'].extend(request.POST.getlist(key))
                        elif field_name == 'pas': d['pas'].extend(request.POST.getlist(key))
                        elif field_name == 'tucs': d['tucs'].extend(request.POST.getlist(key))

                    elif tipo == 'eventos':
                        _m = fin_eventos_map if is_fin else eventos_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'formacoes': d['formacoes'] = _int(value)
                        elif field_name == 'seminarios': d['seminarios'] = _int(value)
                        elif field_name == 'encontros': d['encontros'] = _int(value)
                        elif field_name == 'reunioes': d['reunioes'] = _int(value)
                        elif field_name == 'participantes': d['participantes'] = _int(value)

                    elif tipo == 'redes':
                        _m = fin_redes_map if is_fin else redes_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'nome': d['nome'] = value
                        elif field_name == 'tipo': d['tipo'] = value
                        elif field_name == 'quantidade': d['quantidade'] = _int(value) or 0

                    elif tipo == 'pequenos_projetos':
                        _m = fin_pequenos_projetos_map if is_fin else pequenos_projetos_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'quantidade': d['quantidade'] = _int(value) or 0
                        elif field_name == 'tipo': d['tipo'] = value
                        elif field_name == 'tema': d['tema'] = value
                        elif field_name == 'valor_total': d['valor_total'] = _float(value)

                    elif tipo == 'fundos':
                        _m = fin_fundos_map if is_fin else fundos_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'quantidade': d['quantidade'] = _int(value) or 0
                        elif field_name == 'valor_total': d['valor_total'] = _float(value)
                        elif field_name == 'tipo': d['tipo'] = value

                    elif tipo == 'outro':
                        _m = fin_outro_map if is_fin else outro_map
                        d = _m.setdefault(_id, {})
                        if field_name == 'descricao': d['descricao'] = value
                        elif field_name == 'valor': d['valor'] = _float(value)

                    elif tipo == 'planos' and not is_fin:
                        d = planos_map.setdefault(_id, {})
                        if field_name == 'situacao_nova': d['situacao_nova'] = value
                        elif field_name == 'plano_id': d['plano_id'] = _int(value)

                    elif tipo == 'parcerias':
                        _m = fin_parcerias_map if is_fin else parcerias_map
                        d = _m.setdefault(_id, {'parcerias': []})
                        if field_name == 'parcerias': d['parcerias'].extend(request.POST.getlist(key))

                    elif tipo == 'produtos':
                        _m = fin_produtos_map if is_fin else produtos_map
                        d = _m.setdefault(_id, {'produtos': []})
                        if field_name == 'produtos': d['produtos'].extend(request.POST.getlist(key))

                    elif tipo == 'contratos':
                        _m = fin_contratos_map if is_fin else contratos_map
                        d = _m.setdefault(_id, {'contratos': []})
                        if field_name == 'contratos': d['contratos'].extend(request.POST.getlist(key))

                    elif tipo == 'leis_politicas':
                        _m = fin_leis_map if is_fin else leis_map
                        d = _m.setdefault(_id, {'leis': []})
                        if field_name == 'leis': d['leis'].extend(request.POST.getlist(key))

                    elif tipo == 'mobilizados':
                        _m = fin_mobilizados_map if is_fin else mobilizados_map
                        d = _m.setdefault(_id, {'valor_mobilizado': None, 'tipo_apoio': None, 'fonte_apoio': None})
                        if field_name == 'valor_mobilizado': d['valor_mobilizado'] = value
                        elif field_name == 'tipo_apoio': d['tipo_apoio'] = value
                        elif field_name == 'fonte_apoio': d['fonte_apoio'] = value

                # ── Helper: create M2M result (Area / AreasProtegidas) ─────────
                def _create_m2m_result(Model, ar, ind_or_fin, data, is_fin_flag):
                    has_restrito = data.get('ha_restrito') is not None
                    has_m2m = any(data.get(f) for f in ('tis', 'ucs', 'pas', 'tucs'))
                    if not (has_restrito or has_m2m):
                        return
                    kw = {'atividade_registro': ar}
                    if is_fin_flag:
                        kw['indicador_financiador'] = ind_or_fin
                    else:
                        kw['indicador'] = ind_or_fin
                    if 'ha_restrito' in data:
                        kw['ha_restrito'] = data['ha_restrito']
                    inst = Model(**kw)
                    inst.save()
                    for field in ('tis', 'ucs', 'pas', 'tucs'):
                        if data.get(field):
                            getattr(inst, field).set(data[field])
                    inst.save()  # recalcula total_ha / totals

                # ── Indicador base — criação dos objetos ────────────────────────
                for ind_id, data in pessoas_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    Pessoas.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in organizacoes_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    Organizacoes.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in area_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    _create_m2m_result(Area, atividade_registro, ind, data, False)

                for ind_id, data in areas_protegidas_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    _create_m2m_result(AreasProtegidas, atividade_registro, ind, data, False)

                for ind_id, data in eventos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if any(v for v in data.values()):
                        Evento.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in redes_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data.get('quantidade'):
                        Rede.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in pequenos_projetos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data.get('quantidade'):
                        PequenoProjeto.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in fundos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data.get('quantidade'):
                        Fundo.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in outro_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data.get('descricao') or data.get('valor'):
                        Outro.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                for ind_id, data in planos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    plano_id = data.get('plano_id')
                    plano = Plano.objects.filter(pk=plano_id).first() if plano_id else None
                    if data.get('situacao_nova') and plano:
                        Planos.objects.create(
                            atividade_registro=atividade_registro,
                            indicador=ind,
                            plano=plano,
                            situacao_nova=data['situacao_nova']
                        )

                for ind_id, data in parcerias_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data['parcerias']:
                        inst = Parcerias(atividade_registro=atividade_registro, indicador=ind)
                        inst.save()
                        inst.parcerias.set(data['parcerias'])
                        inst.total_parcerias = len(data['parcerias'])
                        inst.save()

                for ind_id, data in produtos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data['produtos']:
                        inst = Produtos(atividade_registro=atividade_registro, indicador=ind)
                        inst.save()
                        inst.produtos.set(data['produtos'])
                        inst.total_produtos = inst.produtos.count()
                        inst.save()

                for ind_id, data in contratos_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data['contratos']:
                        inst = Contratos(atividade_registro=atividade_registro, indicador=ind)
                        inst.save()
                        inst.contratos.set(data['contratos'])
                        inst.save()

                for ind_id, data in leis_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data['leis']:
                        inst = Leis(atividade_registro=atividade_registro, indicador=ind)
                        inst.save()
                        inst.leis.set(data['leis'])
                        inst.save()

                for ind_id, data in mobilizados_map.items():
                    ind = indicadores_por_id.get(ind_id)
                    if data['valor_mobilizado'] and data['tipo_apoio'] and data['fonte_apoio']:
                        Mobilizados.objects.create(atividade_registro=atividade_registro, indicador=ind, **data)

                # ── IndicadorFinanciador — criação paralela ─────────────────────
                for fin_id, data in fin_pessoas_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    Pessoas.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_organizacoes_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    Organizacoes.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_area_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    _create_m2m_result(Area, atividade_registro, ind_fin, data, True)

                for fin_id, data in fin_areas_protegidas_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    _create_m2m_result(AreasProtegidas, atividade_registro, ind_fin, data, True)

                for fin_id, data in fin_eventos_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if any(v for v in data.values()):
                        Evento.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_redes_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data.get('quantidade'):
                        Rede.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_pequenos_projetos_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data.get('quantidade'):
                        PequenoProjeto.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_fundos_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data.get('quantidade'):
                        Fundo.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_outro_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data.get('descricao') or data.get('valor'):
                        Outro.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                for fin_id, data in fin_parcerias_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data['parcerias']:
                        inst = Parcerias(atividade_registro=atividade_registro, indicador_financiador=ind_fin)
                        inst.save()
                        inst.parcerias.set(data['parcerias'])
                        inst.total_parcerias = len(data['parcerias'])
                        inst.save()

                for fin_id, data in fin_produtos_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data['produtos']:
                        inst = Produtos(atividade_registro=atividade_registro, indicador_financiador=ind_fin)
                        inst.save()
                        inst.produtos.set(data['produtos'])
                        inst.total_produtos = inst.produtos.count()
                        inst.save()

                for fin_id, data in fin_contratos_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data['contratos']:
                        inst = Contratos(atividade_registro=atividade_registro, indicador_financiador=ind_fin)
                        inst.save()
                        inst.contratos.set(data['contratos'])
                        inst.save()

                for fin_id, data in fin_leis_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data['leis']:
                        inst = Leis(atividade_registro=atividade_registro, indicador_financiador=ind_fin)
                        inst.save()
                        inst.leis.set(data['leis'])
                        inst.save()

                for fin_id, data in fin_mobilizados_map.items():
                    ind_fin = indicadores_fin_por_id.get(fin_id)
                    if data['valor_mobilizado'] and data['tipo_apoio'] and data['fonte_apoio']:
                        Mobilizados.objects.create(atividade_registro=atividade_registro, indicador_financiador=ind_fin, **data)

                email_organizacao = form.cleaned_data.get('email_organizacao')

            # Email notification outside the atomic block (side effect)
            try:
                enviar_email_notificacao(atividade_registro.id, email_organizacao)
            except Exception as e:
                print(f"Aviso: falha ao enviar e-mail de notificação: {e}")
            messages.success(request, 'Registro de atividade salvo com sucesso!')
            return redirect('atividade_registro_detalhe', pk=atividade_registro.pk)
        else:
            messages.error(request, f'Erro ao salvar: {form.errors.as_text()}')
    else:
        form = AtividadeRegistroForm()

    parcerias    = Parceria.objects.all()
    planos       = Plano.objects.all()
    tis_list     = TIs.objects.all()
    ucs_list     = UC.objects.all()
    pas_list     = PA.objects.all()
    tucs_list    = TUC.objects.all()
    produtos     = Produto.objects.all()
    contratos    = Contrato.objects.all()
    leis         = Lei.objects.all()
    modelos_existentes = Modelo.objects.all()

    _foco_options = [
        {"value": "implementacao", "label": "Implementação melhorada/monitoramento/vigilância"},
        {"value": "ativ_prod", "label": "Meios de subsistência/cadeia de valor sustentáveis melhorados"},
        {"value": "governanca", "label": "Fortalecimento institucional/capacitação organizacional/governança"},
    ]

    indicadores_config = {
        "pessoas": [
            {"name": "total_pessoas", "type": "number", "label": "Total de Pessoas"},
            {"name": "homens", "type": "number", "label": "Homens", "desag_key": "desag_homens"},
            {"name": "mulheres", "type": "number", "label": "Mulheres", "desag_key": "desag_mulheres"},
            {"name": "jovens", "type": "number", "label": "Jovens", "desag_key": "desag_jovens"},
            {"name": "pct_indigenas", "type": "number", "label": "Indígenas", "desag_key": "desag_pct_indigenas"},
            {"name": "pct_extrativistas", "type": "number", "label": "Extrativistas", "desag_key": "desag_pct_extrativistas"},
            {"name": "pct_quilombolas", "type": "number", "label": "Quilombolas", "desag_key": "desag_pct_quilombolas"},
            {"name": "servidor_publico", "type": "number", "label": "Servidor Público", "desag_key": "desag_servidor_publico"},
            {"name": "foco", "type": "select", "label": "Foco", "options": _foco_options, "desag_key": "tem_foco"},
        ],
        "organizacoes": [
            {"name": "total_organizacoes", "type": "number", "label": "Total de Organizações"},
            {"name": "org_sociedade_civil", "type": "number", "label": "Sociedade Civil", "desag_key": "desag_org_sc"},
            {"name": "org_indigenas", "type": "number", "label": "Org. Indígenas", "desag_key": "desag_org_indigenas"},
            {"name": "org_extrativistas", "type": "number", "label": "Org. Extrativistas", "desag_key": "desag_org_extrativistas"},
            {"name": "foco", "type": "select", "label": "Foco", "options": _foco_options, "desag_key": "tem_foco"},
        ],
        "area": [
            {"name": "ha_restrito", "type": "number", "label": "Área restrita (ha)", "step": "0.01", "desag_key": "desag_restrito"},
            {"name": "tis", "type": "checkbox", "label": "TIs", "options": [{'value': t.id, 'label': t.nome} for t in tis_list], "desag_key": "desag_ti"},
            {"name": "ucs", "type": "checkbox", "label": "UCs", "options": [{'value': u.id, 'label': u.nome} for u in ucs_list], "desag_key": "desag_uc"},
            {"name": "pas", "type": "checkbox", "label": "PAs", "options": [{'value': p.id, 'label': p.nome} for p in pas_list], "desag_key": "desag_pa"},
            {"name": "tucs", "type": "checkbox", "label": "TUCs", "options": [{'value': t.id, 'label': t.nome} for t in tucs_list], "desag_key": "desag_tuc"},
        ],
        "areas_protegidas": [
            {"name": "tis", "type": "checkbox", "label": "TIs", "options": [{'value': t.id, 'label': t.nome} for t in tis_list], "desag_key": "desag_ti"},
            {"name": "ucs", "type": "checkbox", "label": "UCs", "options": [{'value': u.id, 'label': u.nome} for u in ucs_list], "desag_key": "desag_uc"},
            {"name": "pas", "type": "checkbox", "label": "PAs", "options": [{'value': p.id, 'label': p.nome} for p in pas_list], "desag_key": "desag_pa"},
            {"name": "tucs", "type": "checkbox", "label": "TUCs", "options": [{'value': t.id, 'label': t.nome} for t in tucs_list], "desag_key": "desag_tuc"},
        ],
        "eventos": [
            {"name": "formacoes", "type": "number", "label": "Formações", "desag_key": "desag_formacoes"},
            {"name": "seminarios", "type": "number", "label": "Seminários", "desag_key": "desag_seminarios"},
            {"name": "encontros", "type": "number", "label": "Encontros", "desag_key": "desag_encontros"},
            {"name": "reunioes", "type": "number", "label": "Reuniões", "desag_key": "desag_reunioes"},
            {"name": "participantes", "type": "number", "label": "Participantes", "desag_key": "desag_participantes"},
        ],
        "redes": [
            {"name": "nome", "type": "text", "label": "Nome da Rede"},
            {"name": "tipo", "type": "select", "label": "Tipo", "options": [
                {"value": "local", "label": "Local"},
                {"value": "regional", "label": "Regional"},
                {"value": "nacional", "label": "Nacional"},
                {"value": "internacional", "label": "Internacional"},
            ]},
            {"name": "quantidade", "type": "number", "label": "Quantidade"},
        ],
        "pequenos_projetos": [
            {"name": "quantidade", "type": "number", "label": "Quantidade"},
            {"name": "tipo", "type": "text", "label": "Tipo"},
            {"name": "tema", "type": "text", "label": "Tema"},
            {"name": "valor_total", "type": "number", "label": "Valor Total (R$)", "step": "0.01"},
        ],
        "fundos": [
            {"name": "quantidade", "type": "number", "label": "Quantidade"},
            {"name": "valor_total", "type": "number", "label": "Valor Total (R$)", "step": "0.01"},
            {"name": "tipo", "type": "text", "label": "Tipo"},
        ],
        "leis_politicas": [
            {"name": "leis", "type": "checkbox", "label": "Leis", "options": [{'value': l.id, 'label': str(l)} for l in leis]},
        ],
        "planos": [
            {"name": "situacao_nova", "type": "select", "label": "Situação após esta atividade",
             "options": [{"value": s, "label": l} for s, l in Plano.SITUACAO_CHOICES]},
        ],
        "parcerias": [
            {"name": "parcerias", "type": "checkbox", "label": "Parcerias", "options": [{'value': p.id, 'label': f"{p.nome} - {p.tipo}"} for p in parcerias]},
        ],
        "produtos": [
            {"name": "produtos", "type": "checkbox", "label": "Produtos", "options": [{'value': p.id, 'label': p.nome} for p in produtos]},
        ],
        "contratos": [
            {"name": "contratos", "type": "checkbox", "label": "Contratos", "options": [{'value': c.id, 'label': str(c)} for c in contratos]},
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
        "outro": [
            {"name": "descricao", "type": "text", "label": "Descrição"},
            {"name": "valor", "type": "number", "label": "Valor (R$)", "step": "0.01"},
        ],
    }

    produtos_options = [{'value': p.id, 'label': p.nome} for p in produtos]

    return render(request, template, {
        'form': form,
        'indicadores_config': indicadores_config,
        'produtos_options': produtos_options,
    })


def apresentacao_moore(request):
    return render(request, 'apresentacao_moore.html')


# ---------------------------------------------------------------------------
# DASHBOARD DE MONITORAMENTO
# ---------------------------------------------------------------------------

def monitoramento_registros_view(request):
    """Listagem de AtividadeRegistro com filtros por programa, projeto, atividade e data."""
    qs = AtividadeRegistro.objects.select_related(
        'projeto', 'componente', 'atividade', 'subatividade', 'equipe_projeto__equipe'
    ).order_by('-data_inicio')

    programa_id = request.GET.get('programa')
    projeto_id = request.GET.get('projeto')
    atividade_id = request.GET.get('atividade')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if programa_id:
        qs = qs.filter(projeto__programas__id=programa_id)
    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)
    if atividade_id:
        qs = qs.filter(atividade_id=atividade_id)
    if data_inicio:
        qs = qs.filter(data_inicio__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data_inicio__lte=data_fim)

    registros = qs.distinct()

    context = {
        'registros': registros,
        'total': registros.count(),
        'programas': Programa.objects.filter(ativo=True).order_by('sigla'),
        'projetos': Projeto.objects.filter(projeto_pai__isnull=True).order_by('nome_fant'),
        'atividades': Atividade.objects.select_related('componente__projeto').order_by('codigo') if projeto_id else [],
        'filtros': request.GET,
    }
    return render(request, 'monitoramento_registros.html', context)


def monitoramento_metas_view(request):
    """Metas por projeto com realizado e percentual de cumprimento."""
    projeto_id = request.GET.get('projeto')

    base_qs = Meta.objects.select_related(
        'atividade__componente__projeto', 'indicador'
    ).order_by(
        'atividade__componente__projeto__nome_fant',
        'atividade__codigo',
        'indicador__nome',
    )
    fin_qs = MetaFinanciador.objects.select_related(
        'atividade__componente__projeto',
        'indicador_financiador__financiador',
    ).order_by(
        'atividade__componente__projeto__nome_fant',
        'atividade__codigo',
        'indicador_financiador__nome',
    )

    if projeto_id:
        base_qs = base_qs.filter(atividade__componente__projeto_id=projeto_id)
        fin_qs = fin_qs.filter(atividade__componente__projeto_id=projeto_id)

    metas = []
    for m in base_qs:
        metas.append({
            'projeto': m.atividade.componente.projeto.nome_fant,
            'atividade': f"{m.atividade.codigo} — {m.atividade.nome}",
            'indicador': m.indicador.nome,
            'tipo': m.indicador.get_tipo_display(),
            'financiador': None,
            'base': m.base,
            'meta': m.meta,
            'realizado': m.realizado,
            'percentual': m.percentual,
            'data': m.data,
        })
    for m in fin_qs:
        metas.append({
            'projeto': m.atividade.componente.projeto.nome_fant,
            'atividade': f"{m.atividade.codigo} — {m.atividade.nome}",
            'indicador': m.indicador_financiador.nome,
            'tipo': m.indicador_financiador.get_tipo_display(),
            'financiador': m.indicador_financiador.financiador.sigla,
            'base': m.base,
            'meta': m.meta,
            'realizado': m.realizado,
            'percentual': m.percentual,
            'data': m.data,
        })
    metas.sort(key=lambda x: (x['projeto'], x['atividade'], x['indicador']))

    context = {
        'metas': metas,
        'projetos': Projeto.objects.filter(projeto_pai__isnull=True).order_by('nome_fant'),
        'projeto_selecionado': projeto_id,
    }
    return render(request, 'monitoramento_metas.html', context)


