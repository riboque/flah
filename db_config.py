"""
Configurações do Banco de Dados Online
Suporta: PostgreSQL, MySQL, SQLite, e outros

Configure a URL do banco de dados através de variáveis de ambiente:
- DATABASE_URL: URL completa do banco de dados

Exemplos de URLs:
- PostgreSQL: postgresql://usuario:senha@host:5432/database
- MySQL: mysql://usuario:senha@host:3306/database
- SQLite: sqlite:///app.db
- PostgreSQL (Heroku): postgres://...
- CockroachDB: cockroachdb://...
- ElephantSQL: postgresql://...
"""
import os

# ============================================
# CONFIGURAÇÃO DO BANCO DE DADOS ONLINE
# ============================================

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Garantir que a pasta data existe
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Opção 1: URL completa do banco (recomendado para produção)
# Exemplos de serviços gratuitos:
# - ElephantSQL (PostgreSQL): https://www.elephantsql.com
# - PlanetScale (MySQL): https://planetscale.com
# - Railway (PostgreSQL/MySQL): https://railway.app
# - Neon (PostgreSQL): https://neon.tech
# - Supabase (PostgreSQL): https://supabase.com
# - Aiven (PostgreSQL/MySQL): https://aiven.io
# - CockroachDB: https://www.cockroachlabs.com

DATABASE_URL = os.environ.get('DATABASE_URL')

# Se não houver URL, usar SQLite local como fallback
if not DATABASE_URL:
    # Usar caminho absoluto para SQLite
    SQLITE_PATH = os.path.join(DATA_DIR, 'clientes.db')
    DATABASE_URL = f'sqlite:///{SQLITE_PATH}'

# Correção para URLs do Heroku (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


# ============================================
# CONFIGURAÇÕES ESPECÍFICAS DE CADA PROVEDOR
# ============================================

# ElephantSQL (PostgreSQL gratuito)
# Cadastre-se em: https://www.elephantsql.com
# ELEPHANTSQL_URL = "postgresql://usuario:senha@tiny.db.elephantsql.com/database"

# Neon (PostgreSQL serverless)
# Cadastre-se em: https://neon.tech
# NEON_URL = "postgresql://usuario:senha@ep-xxx.us-east-1.aws.neon.tech/database?sslmode=require"

# PlanetScale (MySQL serverless)
# Cadastre-se em: https://planetscale.com
# PLANETSCALE_URL = "mysql://usuario:senha@aws.connect.psdb.cloud/database?ssl=true"

# Supabase (PostgreSQL)
# Cadastre-se em: https://supabase.com
# SUPABASE_URL = "postgresql://postgres:senha@db.xxx.supabase.co:5432/postgres"

# Railway
# Cadastre-se em: https://railway.app
# RAILWAY_URL = "postgresql://postgres:senha@containers-xxx.railway.app:5432/railway"


# ============================================
# CLASSE DE CONFIGURAÇÃO DO SQLALCHEMY
# ============================================

class DatabaseConfig:
    """Configurações do SQLAlchemy"""
    
    # URL do banco de dados
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Desabilitar tracking de modificações (melhora performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pool de conexões
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verifica conexão antes de usar
        'pool_recycle': 300,    # Reciclar conexões a cada 5 minutos
        'pool_size': 10,        # Número de conexões no pool
        'max_overflow': 20,     # Conexões extras permitidas
    }
    
    # Configurações para PostgreSQL com SSL (comum em provedores cloud)
    if 'postgresql' in DATABASE_URL or 'postgres' in DATABASE_URL:
        if 'sslmode' not in DATABASE_URL:
            # Adicionar SSL para provedores cloud
            if any(provider in DATABASE_URL for provider in ['neon', 'supabase', 'railway', 'elephant']):
                if '?' in DATABASE_URL:
                    SQLALCHEMY_DATABASE_URI = DATABASE_URL + '&sslmode=require'
                else:
                    SQLALCHEMY_DATABASE_URI = DATABASE_URL + '?sslmode=require'


def get_database_url():
    """Retorna a URL do banco de dados configurada"""
    return DatabaseConfig.SQLALCHEMY_DATABASE_URI


def test_connection():
    """Testa a conexão com o banco de dados"""
    from sqlalchemy import create_engine, text
    
    try:
        engine = create_engine(get_database_url())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[DB] ✓ Conexão com banco de dados OK!")
            return True
    except Exception as e:
        print(f"[DB] ✗ Erro na conexão: {e}")
        return False


# ============================================
# HELPER PARA CONFIGURAR VARIÁVEIS DE AMBIENTE
# ============================================

def setup_env_example():
    """Cria arquivo .env.example com variáveis de ambiente"""
    env_content = """# Configuração do Banco de Dados Online
# Copie este arquivo para .env e configure suas credenciais

# === OPÇÃO 1: URL Completa (Recomendado) ===
# DATABASE_URL=postgresql://usuario:senha@host:5432/database

# === OPÇÃO 2: Provedores específicos ===

# ElephantSQL (PostgreSQL gratuito)
# DATABASE_URL=postgresql://usuario:senha@tiny.db.elephantsql.com/database

# Neon (PostgreSQL serverless)
# DATABASE_URL=postgresql://usuario:senha@ep-xxx.us-east-1.aws.neon.tech/database?sslmode=require

# Supabase (PostgreSQL)
# DATABASE_URL=postgresql://postgres:senha@db.xxx.supabase.co:5432/postgres

# PlanetScale (MySQL serverless)
# DATABASE_URL=mysql://usuario:senha@aws.connect.psdb.cloud/database?ssl=true

# Railway (PostgreSQL/MySQL)
# DATABASE_URL=postgresql://postgres:senha@containers-xxx.railway.app:5432/railway

# === CONFIGURAÇÕES ADICIONAIS ===
FLASK_ENV=development
FLASK_SECRET_KEY=sua_chave_secreta_aqui
"""
    return env_content
