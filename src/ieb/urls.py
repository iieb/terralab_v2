from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import atividade_registro_view, load_componentes, load_atividades, load_equipes, load_equipes_adicionais,load_indicadores, atividade_registro_detalhe_view, teste_parcerias_view,adicionar_parceria, adicionar_plano,atualizar_situacao_plano, adicionar_produto, adicionar_contrato, atualizar_estado_contrato, adicionar_lei, atualizar_situacao_lei, adicionar_modelo
from . import views 

urlpatterns = [
    path('atividade_registro/', atividade_registro_view, name='atividade_registro'),
    path('ajax/load-componentes/', load_componentes, name='load_componentes'),
    path('ajax/load-atividades/', load_atividades, name='load_atividades'),
    path('ajax/load-equipes/', load_equipes, name='load_equipes'),
    path('ajax/load-equipes-adicionais/', load_equipes_adicionais, name='load_equipes_adicionais'),
    path('load_indicadores/', load_indicadores, name='load_indicadores'),
    path('atividade/<int:pk>/', atividade_registro_detalhe_view, name='atividade_registro_detalhe'),
    path('teste_parcerias/', teste_parcerias_view, name='teste_parcerias'),  # Nova rota para o template de teste
    path('adicionar_parceria/', adicionar_parceria, name='adicionar_parceria'),  # Adicione esta linha
    path('adicionar-plano/', adicionar_plano, name='adicionar_plano'),
    path('atualizar_situacao_plano/', atualizar_situacao_plano, name='atualizar_situacao_plano'),
    path('adicionar_produto/', adicionar_produto, name='adicionar_produto'),
    path('adicionar_contrato/', adicionar_contrato, name='adicionar_contrato'),
    path('atualizar_estado_contrato/', atualizar_estado_contrato, name='atualizar_estado_contrato'),
    path('adicionar_lei/', adicionar_lei, name='adicionar_lei'),
    path('atualizar_situacao_lei/', atualizar_situacao_lei, name='atualizar_situacao_lei'),
    path('adicionar_modelo/', adicionar_modelo, name='adicionar_modelo'),
    path('atividade/<int:pk>/anterior/', views.atividade_registro_anterior, name='atividade_registro_anterior'),
    path('atividade/<int:pk>/proximo/', views.atividade_registro_proximo, name='atividade_registro_proximo'),


]