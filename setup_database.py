"""
Script para testar e configurar o banco de dados
Execute: python setup_database.py
"""
import os
import sys

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("    CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    print()
    
    # Verificar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Importar a configuração correta
    from database.db_config import DATABASE_URL, get_database_url
    
    print(f"[INFO] URL do banco: {DATABASE_URL[:60]}...")
    print()
    
    # Testar conexão
    print("[1/4] Testando conexão com o banco de dados...")
    from database.db_config import test_connection
    if not test_connection():
        print("[ERRO] Não foi possível conectar ao banco de dados!")
        print("       Verifique suas configurações no arquivo .env")
        return False
    
    # Criar tabelas
    print("[2/4] Criando tabelas...")
    from flask import Flask
    from database.models import db
    from database.db_config import DatabaseConfig
    
    app = Flask(__name__)
    app.config.from_object(DatabaseConfig)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("[OK] Tabelas criadas com sucesso!")
    
    # Criar usuário admin padrão
    print("[3/4] Verificando usuário administrador...")
    from database.db_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    # Não chamar init_app novamente, já foi inicializado
    
    with app.app_context():
        from database.models import Cliente
        admin = Cliente.query.filter_by(email='admin@sistema.local').first()
        
        if not admin:
            print("     → Criando usuário admin padrão...")
            admin = db_manager.criar_cliente(
                nome='Administrador',
                email='admin@sistema.local',
                senha='admin123',  # MUDE ESSA SENHA!
                nivel_acesso='admin'
            )
            print(f"[OK] Admin criado! Email: admin@sistema.local | Senha: admin123")
            print("[!] IMPORTANTE: Mude a senha do admin após o primeiro login!")
        else:
            print("[OK] Usuário admin já existe.")
    
    # Mostrar estatísticas
    print("[4/4] Estatísticas do banco...")
    with app.app_context():
        stats = db_manager.obter_estatisticas()
        print(f"     → Total de clientes: {stats['total_clientes']}")
        print(f"     → Total de dispositivos: {stats['total_dispositivos']}")
        print(f"     → Dispositivos online: {stats['dispositivos_online']}")
    
    print()
    print("=" * 60)
    print("    CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("Próximos passos:")
    print("1. Inicie o servidor: python run.py")
    print("2. Acesse: http://localhost:5000")
    print("3. Use as APIs de banco: /api/db/...")
    print()
    print("APIs disponíveis:")
    print("  GET  /api/db/clientes          - Listar clientes")
    print("  POST /api/db/clientes          - Criar cliente")
    print("  GET  /api/db/dispositivos      - Listar dispositivos")
    print("  POST /api/db/auth/login        - Login")
    print("  GET  /api/db/estatisticas      - Estatísticas")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
