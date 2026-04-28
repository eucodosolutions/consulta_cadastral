import traceback
from datetime import datetime, timezone
from app.db.client import supabase_client

def get_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def criar_log_execucao(nome_processo: str, area: str, agendado_por: str = "usuario", nome_recurso: str = "app_python") -> str:
    """Cria um registro inicial de log e retorna o id_execucao."""
    data = {
        "nome_processo": nome_processo,
        "nome_recurso": nome_recurso,
        "agendado_por": agendado_por,
        "area": area,
        "status": "em_execucao",
        "iniciado_em": get_now()
    }
    response = supabase_client.table("logs_execucao").insert(data).execute()
    return response.data[0]["id_execucao"]

def atualizar_etapa_log(id_execucao: str, etapa: str, metadados: dict = None):
    """Atualiza a etapa atual no log."""
    data = {
        "ultima_etapa": etapa,
        "etapa_iniciada_em": get_now()
    }
    if metadados:
        # Recupera os metadados antigos para fazer merge, caso seja necessário, 
        # mas por simplicidade, vamos substituir ou atualizar.
        data["metadados"] = metadados
        
    supabase_client.table("logs_execucao").update(data).eq("id_execucao", id_execucao).execute()

def finalizar_log_com_sucesso(id_execucao: str, tempo_total: float):
    """Marca o log como concluído."""
    data = {
        "status": "concluido",
        "finalizado_em": get_now(),
        "tempo_total_execucao": tempo_total,
        "ultima_etapa": "finalizado"
    }
    supabase_client.table("logs_execucao").update(data).eq("id_execucao", id_execucao).execute()

def finalizar_log_com_erro(id_execucao: str, erro: Exception, tempo_total: float = 0.0):
    """Registra uma falha no log."""
    data = {
        "status": "falha",
        "finalizado_em": get_now(),
        "tempo_total_execucao": tempo_total,
        "mensagem_erro": str(erro)[:500],  # Limitar tamanho
        "pilha_erro": traceback.format_exc()
    }
    supabase_client.table("logs_execucao").update(data).eq("id_execucao", id_execucao).execute()

def salvar_consulta_simples(dados: dict):
    """
    Salva os dados extraídos do portal.
    O dicionário 'dados' deve conter: cnpj, situacao_simples_nacional, nome_empresarial, situacao_simei.
    """
    dados["data_hora_processamento"] = get_now()
    return supabase_client.table("consultar_simples_nacional").insert(dados).execute()
