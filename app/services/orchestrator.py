import time
import pandas as pd
from typing import List, Dict, Any
from app.db.repository import (
    criar_log_execucao,
    atualizar_etapa_log,
    finalizar_log_com_sucesso,
    finalizar_log_com_erro,
    salvar_consulta_simples
)
from app.scraper.consulta_cnpj import extrair_dados_simples_nacional
from app.scraper.exceptions import CNPJInvalidoError, SiteInstavelError

def processar_cnpj_unico(cnpj: str, agendado_por: str = "usuario") -> Dict[str, Any]:
    """Orquestra a extração e salvamento para um único CNPJ."""
    start_time = time.time()
    id_execucao = criar_log_execucao(
        nome_processo="Consulta Simples Nacional Único",
        area="Compliance",
        agendado_por=agendado_por
    )
    
    try:
        atualizar_etapa_log(id_execucao, "extraindo_dados", {"cnpj_alvo": cnpj})
        
        # Chama o scraper
        dados_extraidos = extrair_dados_simples_nacional(cnpj)
        
        atualizar_etapa_log(id_execucao, "salvando_banco", {"status": "sucesso_extracao"})
        
        # Salva no banco de dados
        salvar_consulta_simples(dados_extraidos)
        
        tempo_total = time.time() - start_time
        finalizar_log_com_sucesso(id_execucao, tempo_total)
        
        return {
            "sucesso": True,
            "dados": dados_extraidos,
            "id_execucao": id_execucao
        }
        
    except CNPJInvalidoError as e:
        # Tratado como regra de negócio, não necessariamente um erro sistêmico grave
        tempo_total = time.time() - start_time
        finalizar_log_com_erro(id_execucao, e, tempo_total)
        return {"sucesso": False, "erro": str(e), "tipo": "regra_negocio"}
        
    except Exception as e:
        tempo_total = time.time() - start_time
        finalizar_log_com_erro(id_execucao, e, tempo_total)
        return {"sucesso": False, "erro": "Erro interno ao processar a consulta.", "tipo": "sistema"}


def processar_lote_planilha(df: pd.DataFrame, coluna_cnpj: str, agendado_por: str = "usuario") -> Dict[str, Any]:
    """Processa uma lista de CNPJs a partir de um DataFrame Pandas."""
    start_time = time.time()
    id_execucao = criar_log_execucao(
        nome_processo="Consulta Simples Nacional Lote",
        area="Compliance",
        agendado_por=agendado_por
    )
    
    resultados = []
    erros = 0
    sucessos = 0
    
    try:
        cnpjs = df[coluna_cnpj].dropna().astype(str).tolist()
        total = len(cnpjs)
        
        atualizar_etapa_log(id_execucao, "iniciando_lote", {"total_cnpjs": total})
        
        for idx, cnpj in enumerate(cnpjs):
            try:
                # Atualiza log a cada 10 registros para não sobrecarregar o DB
                if idx % 10 == 0:
                    atualizar_etapa_log(id_execucao, "processando_lote", {"processados": idx, "total": total})
                
                dados = extrair_dados_simples_nacional(cnpj)
                salvar_consulta_simples(dados)
                
                resultados.append({"cnpj": cnpj, "status": "Sucesso", **dados})
                sucessos += 1
                
            except CNPJInvalidoError:
                resultados.append({"cnpj": cnpj, "status": "CNPJ Inválido"})
                erros += 1
            except Exception as e:
                resultados.append({"cnpj": cnpj, "status": f"Erro: {str(e)}"})
                erros += 1
                
        tempo_total = time.time() - start_time
        atualizar_etapa_log(id_execucao, "finalizando_lote", {"sucessos": sucessos, "erros": erros})
        finalizar_log_com_sucesso(id_execucao, tempo_total)
        
        df_res = pd.DataFrame(resultados)
        if "data_hora_processamento" in df_res.columns:
            df_res["data_hora_processamento"] = pd.to_datetime(
                df_res["data_hora_processamento"]
            ).dt.tz_convert('America/Sao_Paulo').dt.strftime('%d/%m/%Y %H:%M:%S')

        return {
            "sucesso": True,
            "resumo": {"total": total, "sucessos": sucessos, "erros": erros},
            "resultados_df": df_res,
            "id_execucao": id_execucao
        }
        
    except Exception as e:
        tempo_total = time.time() - start_time
        finalizar_log_com_erro(id_execucao, e, tempo_total)
        return {"sucesso": False, "erro": str(e)}
