"""Script para testar login diretamente no Flask"""
import os
import sys
sys.path.insert(0, '.')

# Carregar variáveis de ambiente ANTES de qualquer import
from dotenv import load_dotenv
load_dotenv()

print(f"[ENV] DATABASE_URL: {os.environ.get('DATABASE_URL', 'NAO DEFINIDO')[:60]}...")

from flask import Flask
from database.models import db, Cliente
from database.db_config import DatabaseConfig

app = Flask(__name__)
app.config.from_object(DatabaseConfig)
db.init_app(app)

print(f"[FLASK] SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')[:60]}...")

with app.app_context():
    # Testar diretamente
    email = 'admin@sistema.local'
    senha = 'admin123'
    
    print(f"\n[TEST] Buscando cliente: {email}")
    cliente = Cliente.query.filter_by(email=email, ativo=True).first()
    
    if cliente:
        print(f"[OK] Cliente encontrado: {cliente.nome}")
        print(f"[INFO] Hash: {cliente.senha_hash[:50]}...")
        
        result = cliente.verificar_senha(senha)
        print(f"[TEST] Verificação de senha: {result}")
        
        if not result:
            print("\n[FIX] Resetando senha...")
            cliente.set_senha(senha)
            db.session.commit()
            
            result2 = cliente.verificar_senha(senha)
            print(f"[TEST] Nova verificação: {result2}")
    else:
        print("[ERRO] Cliente não encontrado!")
        
        # Listar todos os clientes
        print("\n[INFO] Clientes no banco:")
        for c in Cliente.query.limit(5).all():
            print(f"  - {c.email} ({c.nome})")
