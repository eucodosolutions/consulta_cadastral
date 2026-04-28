-- Tabela 1: logs_execucao
CREATE TABLE IF NOT EXISTS public.logs_execucao (
    id_execucao UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_processo VARCHAR(255) NOT NULL,
    nome_recurso VARCHAR(255) NOT NULL,
    agendado_por VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pendente', 'em_execucao', 'concluido', 'falha')),
    ultima_etapa VARCHAR(255),
    etapa_iniciada_em TIMESTAMP WITH TIME ZONE,
    iniciado_em TIMESTAMP WITH TIME ZONE,
    finalizado_em TIMESTAMP WITH TIME ZONE,
    tempo_total_execucao DOUBLE PRECISION,
    mensagem_erro TEXT,
    pilha_erro TEXT,
    metadados JSONB
);

-- Tabela 2: consultar_simples_nacional
CREATE TABLE IF NOT EXISTS public.consultar_simples_nacional (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cnpj VARCHAR(20) NOT NULL,
    situacao_simples_nacional VARCHAR(255),
    nome_empresarial VARCHAR(255),
    situacao_simei VARCHAR(255),
    data_hora_processamento TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Opcional: Adicionar índices para acelerar buscas comuns
CREATE INDEX IF NOT EXISTS idx_logs_status ON public.logs_execucao(status);
CREATE INDEX IF NOT EXISTS idx_consultar_simples_cnpj ON public.consultar_simples_nacional(cnpj);

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================
-- Habilitar RLS nas tabelas para maior segurança
ALTER TABLE public.logs_execucao ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consultar_simples_nacional ENABLE ROW LEVEL SECURITY;

-- Políticas de Segurança (Policies)
-- Nota: Como o script Python está configurado para utilizar a Service Role Key (sb_secret_...), 
-- ele já tem permissão irrestrita por padrão, bypassando o RLS. 
-- No entanto, se futuramente você utilizar a chave "anon" (Publishable key) no frontend, 
-- precisará de políticas específicas. Abaixo está um exemplo de política permissiva inicial:

-- CREATE POLICY "Permitir leitura para todos" ON public.logs_execucao FOR SELECT USING (true);
-- CREATE POLICY "Permitir insercao para todos" ON public.logs_execucao FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Permitir atualizacao para todos" ON public.logs_execucao FOR UPDATE USING (true);

-- CREATE POLICY "Permitir leitura para todos" ON public.consultar_simples_nacional FOR SELECT USING (true);
-- CREATE POLICY "Permitir insercao para todos" ON public.consultar_simples_nacional FOR INSERT WITH CHECK (true);
