"""Script para mostrar todos os dados do banco de dados"""
import os
from dotenv import load_dotenv
load_dotenv()

from database.models import db, Cliente, Sessao, Dispositivo, Conexao, MensagemChat, LogAuditoria
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print('='*80)
    print('TABELA: CLIENTES')
    print('='*80)
    clientes = Cliente.query.all()
    print(f'Total: {len(clientes)}')
    for c in clientes:
        print(f'ID:{c.id} | Nome:{c.nome} | Email:{c.email} | Nivel:{c.nivel_acesso} | Ativo:{c.ativo}')
        print(f'   Tel:{c.telefone} | Empresa:{c.empresa} | Cidade:{c.cidade} | Estado:{c.estado}')
        print(f'   Cadastro:{c.data_cadastro} | Ultimo:{c.ultimo_acesso}')
        print('-'*80)
    
    print()
    print('='*80)
    print('TABELA: SESSOES')
    print('='*80)
    sessoes = Sessao.query.all()
    print(f'Total: {len(sessoes)} | Ativas: {len([s for s in sessoes if s.ativa])}')
    for s in sessoes:
        print(f'ID:{s.id} | Cliente:{s.cliente_id} | Ativa:{s.ativa} | IP:{s.ip_address}')
        print(f'   Inicio:{s.data_inicio} | Token:{s.token[:20] if s.token else None}...')
    
    print()
    print('='*80)
    print('TABELA: DISPOSITIVOS')
    print('='*80)
    dispositivos = Dispositivo.query.all()
    print(f'Total: {len(dispositivos)}')
    for d in dispositivos:
        print(f'ID:{d.id} | Cliente:{d.cliente_id} | Nome:{d.nome} | Tipo:{d.tipo}')
        print(f'   IP:{d.ip_local} | Pub:{d.ip_publico} | SO:{d.sistema_operacional}')
        print(f'   Ultimo HB:{d.ultimo_heartbeat}')
    
    print()
    print('='*80)
    print('TABELA: CONEXOES')
    print('='*80)
    conexoes = Conexao.query.all()
    print(f'Total: {len(conexoes)}')
    for co in conexoes[:10]:
        print(f'ID:{co.id} | Disp:{co.dispositivo_id} | IP:{co.ip_address} | Data:{co.data_conexao}')
    if len(conexoes) > 10:
        print(f'... e mais {len(conexoes)-10} conexoes')
    
    print()
    print('='*80)
    print('TABELA: MENSAGENS CHAT')
    print('='*80)
    total_msgs = MensagemChat.query.count()
    msgs = MensagemChat.query.order_by(MensagemChat.data_hora.desc()).limit(10).all()
    print(f'Total: {total_msgs} | Ultimas 10:')
    for m in msgs:
        print(f'ID:{m.id} | Cliente:{m.cliente_id} | Sala:{m.sala} | Data:{m.data_hora}')
        conteudo = m.conteudo[:50] if m.conteudo else '-'
        print(f'   Msg: {conteudo}...')
    
    print()
    print('='*80)
    print('TABELA: LOGS AUDITORIA')
    print('='*80)
    total_logs = LogAuditoria.query.count()
    logs = LogAuditoria.query.order_by(LogAuditoria.data_hora.desc()).limit(10).all()
    print(f'Total: {total_logs} | Ultimos 10:')
    for l in logs:
        print(f'ID:{l.id} | Cliente:{l.cliente_id} | Acao:{l.acao} | IP:{l.ip_address}')
        desc = l.descricao[:50] if l.descricao else '-'
        print(f'   Desc: {desc}')
    
    print()
    print('='*80)
    print('RESUMO')
    print('='*80)
    print(f'Clientes: {len(clientes)}')
    print(f'Sessoes: {len(sessoes)} (Ativas: {len([s for s in sessoes if s.ativa])})')
    print(f'Dispositivos: {len(dispositivos)}')
    print(f'Conexoes: {len(conexoes)}')
    print(f'Mensagens: {total_msgs}')
    print(f'Logs: {total_logs}')
