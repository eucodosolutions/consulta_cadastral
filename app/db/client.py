from supabase import create_client, Client
from app.utils.config import SUPABASE_URL, SUPABASE_KEY

# Instância Singleton do cliente Supabase
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
