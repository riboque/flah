"""Script para verificar e corrigir o usuário admin"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from database.models import db, Cliente
from database.db_config import DatabaseConfig

app = Flask(__name__)
app.config.from_object(DatabaseConfig)
db.init_app(app)

with app.app_context():
    admin = Cliente.query.filter_by(email='admin@sistema.local').first()
    
    if admin:
        print('[OK] Usuario encontrado!')
        print(f'  - ID: {admin.id}')
        print(f'  - Nome: {admin.nome}')
        print(f'  - Email: {admin.email}')
        print(f'  - Ativo: {admin.ativo}')
        print(f'  - Nivel: {admin.nivel_acesso}')
        
        if admin.senha_hash:
            print(f'  - Hash senha: {admin.senha_hash[:50]}...')
        else:
            print('  - Hash senha: NENHUM (senha nao definida!)')
        
        # Testar verificacao de senha
        print()
        print('[TESTE] Verificando senha "admin123"...')
        result = admin.verificar_senha('admin123')
        print(f'  - Resultado: {result}')
        
        if not result:
            print()
            print('[INFO] Senha incorreta! Resetando para "admin123"...')
            admin.set_senha('admin123')
            db.session.commit()
            print('[OK] Senha resetada!')
            result2 = admin.verificar_senha('admin123')
            print(f'  - Novo teste: {result2}')
            
            if result2:
                print()
                print('='*50)
                print('SENHA CORRIGIDA! Tente fazer login novamente.')
                print('Email: admin@sistema.local')
                print('Senha: admin123')
                print('='*50)
    else:
        print('[ERRO] Usuario admin@sistema.local NAO encontrado!')
        print()
        print('[INFO] Usuarios existentes:')
        for c in Cliente.query.limit(10).all():
            print(f'  - {c.id}: {c.email} ({c.nome})')
        
        print()
        print('[INFO] Criando usuario admin...')
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        admin = db_manager.criar_cliente(
            nome='Administrador',
            email='admin@sistema.local',
            senha='admin123',
            nivel_acesso='admin'
        )
        print(f'[OK] Admin criado! ID: {admin.id}')
        print()
        print('='*50)
        print('USUARIO ADMIN CRIADO!')
        print('Email: admin@sistema.local')
        print('Senha: admin123')
        print('='*50)
