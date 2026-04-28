import re

def clean_cnpj(cnpj: str) -> str:
    """Remove caracteres especiais do CNPJ e retorna apenas os números."""
    return re.sub(r'[^0-9]', '', str(cnpj))

def is_valid_cnpj(cnpj: str) -> bool:
    """Valida o formato básico de um CNPJ (apenas tamanho, para não bloquear o fluxo atoa)."""
    cleaned = clean_cnpj(cnpj)
    return len(cleaned) == 14
