import re
import time
import logging
import requests

from app.scraper.exceptions import SiteInstavelError, CNPJInvalidoError
from app.utils.validators import clean_cnpj

URL_RECEITAWS = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"

log = logging.getLogger(__name__)


def extrair_dados_simples_nacional(cnpj: str) -> dict:
    """
    Consulta os dados do Simples Nacional para o CNPJ informado via API ReceitaWS.
    """
    cnpj_limpo = clean_cnpj(cnpj)

    log.info("[ReceitaWS] Consultando CNPJ=%s", cnpj_limpo)
    return _consultar_api(cnpj_limpo, cnpj)


# ---------------------------------------------------------------------------
# Extração via API ReceitaWS
# ---------------------------------------------------------------------------

def _consultar_api(cnpj_limpo: str, cnpj_original: str) -> dict:
    """Consulta a API pública ReceitaWS, que agrega dados diretamente da RFB."""
    try:
        resp = requests.get(
            URL_RECEITAWS.format(cnpj=cnpj_limpo),
            timeout=8,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise SiteInstavelError(f"ReceitaWS inacessível: {exc}") from exc

    data = resp.json()

    if data.get("status") == "ERROR":
        raise CNPJInvalidoError(f"CNPJ {cnpj_original} inválido ou não encontrado.")

    simples = data.get("simples") or {}
    simei = data.get("simei") or {}

    return {
        "cnpj": cnpj_original,
        "nome_empresarial": data.get("nome", "NÃO INFORMADO"),
        "situacao_simples_nacional": (
            "Optante pelo Simples Nacional"
            if simples.get("optante")
            else "NÃO optante pelo Simples Nacional"
        ),
        "situacao_simei": (
            "Optante pelo SIMEI"
            if simei.get("optante")
            else "NÃO enquadrado no SIMEI"
        ),
    }


