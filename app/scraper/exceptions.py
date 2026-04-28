class APIConsultaError(Exception):
    """Classe base para erros durante a consulta de dados."""
    pass

class SiteInstavelError(APIConsultaError):
    """Exceção levantada quando a API da ReceitaWS está fora do ar ou muito lenta."""
    pass

class CNPJInvalidoError(APIConsultaError):
    """Exceção levantada quando a API informa que o CNPJ é inválido ou inexistente."""
    pass
