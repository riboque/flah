"""
Modelos do Banco de Dados - SQLAlchemy ORM
Suporta: PostgreSQL, MySQL, SQLite
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class Cliente(db.Model):
    """Modelo para clientes/usuários do sistema"""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256))
    telefone = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    cargo = db.Column(db.String(50))
    endereco = db.Column(db.Text)
    cidade = db.Column(db.String(50))
    estado = db.Column(db.String(50))
    pais = db.Column(db.String(50), default='Brasil')
    cep = db.Column(db.String(15))
    cpf_cnpj = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    nivel_acesso = db.Column(db.String(20), default='usuario')  # admin, moderador, usuario
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    dados_extras = db.Column(db.Text)  # JSON para dados adicionais
    
    # Relacionamentos
    dispositivos = db.relationship('Dispositivo', backref='cliente', lazy='dynamic', cascade='all, delete-orphan')
    conexoes = db.relationship('Conexao', backref='cliente', lazy='dynamic', cascade='all, delete-orphan')
    mensagens = db.relationship('MensagemChat', backref='cliente', lazy='dynamic', cascade='all, delete-orphan')
    sessoes = db.relationship('Sessao', backref='cliente', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_senha(self, senha):
        """Define a senha criptografada"""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, senha)
    
    def get_dados_extras(self):
        """Retorna dados extras como dicionário"""
        if self.dados_extras:
            try:
                return json.loads(self.dados_extras)
            except:
                return {}
        return {}
    
    def set_dados_extras(self, dados):
        """Define dados extras a partir de dicionário"""
        self.dados_extras = json.dumps(dados, ensure_ascii=False)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'empresa': self.empresa,
            'cargo': self.cargo,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'pais': self.pais,
            'cep': self.cep,
            'cpf_cnpj': self.cpf_cnpj,
            'ativo': self.ativo,
            'nivel_acesso': self.nivel_acesso,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'observacoes': self.observacoes,
            'dados_extras': self.get_dados_extras(),
            'total_dispositivos': self.dispositivos.count() if self.dispositivos else 0
        }
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Dispositivo(db.Model):
    """Modelo para dispositivos registrados"""
    __tablename__ = 'dispositivos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(50))  # desktop, laptop, servidor, mobile
    sistema_operacional = db.Column(db.String(50))
    versao_so = db.Column(db.String(50))
    hostname = db.Column(db.String(100))
    ip_local = db.Column(db.String(45))
    ip_publico = db.Column(db.String(45))
    mac_address = db.Column(db.String(20))
    processador = db.Column(db.String(100))
    memoria_total = db.Column(db.String(20))
    disco_total = db.Column(db.String(20))
    is_virtual = db.Column(db.Boolean, default=False)
    virtual_type = db.Column(db.String(50))  # VMware, VirtualBox, Hyper-V, etc
    ativo = db.Column(db.Boolean, default=True)
    ultimo_heartbeat = db.Column(db.DateTime)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    info_extra = db.Column(db.Text)  # JSON para informações adicionais
    
    # Relacionamento com conexões
    conexoes = db.relationship('Conexao', backref='dispositivo', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_info_extra(self):
        """Retorna info extra como dicionário"""
        if self.info_extra:
            try:
                return json.loads(self.info_extra)
            except:
                return {}
        return {}
    
    def set_info_extra(self, info):
        """Define info extra a partir de dicionário"""
        self.info_extra = json.dumps(info, ensure_ascii=False)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'tipo': self.tipo,
            'sistema_operacional': self.sistema_operacional,
            'versao_so': self.versao_so,
            'hostname': self.hostname,
            'ip_local': self.ip_local,
            'ip_publico': self.ip_publico,
            'mac_address': self.mac_address,
            'processador': self.processador,
            'memoria_total': self.memoria_total,
            'disco_total': self.disco_total,
            'is_virtual': self.is_virtual,
            'virtual_type': self.virtual_type,
            'ativo': self.ativo,
            'ultimo_heartbeat': self.ultimo_heartbeat.isoformat() if self.ultimo_heartbeat else None,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'info_extra': self.get_info_extra(),
            'cliente_nome': self.cliente.nome if self.cliente else None
        }
    
    def __repr__(self):
        return f'<Dispositivo {self.hostname}>'


class Conexao(db.Model):
    """Modelo para histórico de conexões"""
    __tablename__ = 'conexoes'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    dispositivo_id = db.Column(db.Integer, db.ForeignKey('dispositivos.id'), nullable=True)
    ip_origem = db.Column(db.String(45))
    ip_destino = db.Column(db.String(45))
    porta_origem = db.Column(db.Integer)
    porta_destino = db.Column(db.Integer)
    protocolo = db.Column(db.String(10))  # TCP, UDP
    status = db.Column(db.String(20))  # ESTABLISHED, CLOSE_WAIT, TIME_WAIT, etc
    processo = db.Column(db.String(100))
    pid = db.Column(db.Integer)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    duracao_segundos = db.Column(db.Integer)
    bytes_enviados = db.Column(db.BigInteger, default=0)
    bytes_recebidos = db.Column(db.BigInteger, default=0)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'dispositivo_id': self.dispositivo_id,
            'ip_origem': self.ip_origem,
            'ip_destino': self.ip_destino,
            'porta_origem': self.porta_origem,
            'porta_destino': self.porta_destino,
            'protocolo': self.protocolo,
            'status': self.status,
            'processo': self.processo,
            'pid': self.pid,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'duracao_segundos': self.duracao_segundos,
            'bytes_enviados': self.bytes_enviados,
            'bytes_recebidos': self.bytes_recebidos
        }
    
    def __repr__(self):
        return f'<Conexao {self.ip_origem}:{self.porta_origem} -> {self.ip_destino}:{self.porta_destino}>'


class MensagemChat(db.Model):
    """Modelo para mensagens do chat"""
    __tablename__ = 'mensagens_chat'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    sala = db.Column(db.String(50), default='geral')
    usuario = db.Column(db.String(100))
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='texto')  # texto, imagem, arquivo, sistema
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    editada = db.Column(db.Boolean, default=False)
    deletada = db.Column(db.Boolean, default=False)
    resposta_para = db.Column(db.Integer, db.ForeignKey('mensagens_chat.id'), nullable=True)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'sala': self.sala,
            'usuario': self.usuario,
            'mensagem': self.mensagem if not self.deletada else '[Mensagem removida]',
            'tipo': self.tipo,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'editada': self.editada,
            'deletada': self.deletada,
            'resposta_para': self.resposta_para
        }
    
    def __repr__(self):
        return f'<MensagemChat {self.id} de {self.usuario}>'


class Sessao(db.Model):
    """Modelo para sessões ativas"""
    __tablename__ = 'sessoes'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    token = db.Column(db.String(256), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    dispositivo_info = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_expiracao = db.Column(db.DateTime)
    ultima_atividade = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'token': self.token[:20] + '...' if self.token else None,
            'ip_address': self.ip_address,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'ultima_atividade': self.ultima_atividade.isoformat() if self.ultima_atividade else None,
            'ativa': self.ativa
        }
    
    def __repr__(self):
        return f'<Sessao {self.id} cliente={self.cliente_id}>'


class LogAuditoria(db.Model):
    """Modelo para logs de auditoria"""
    __tablename__ = 'logs_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    acao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    dados = db.Column(db.Text)  # JSON
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    nivel = db.Column(db.String(20), default='info')  # info, warning, error, critical
    
    def to_dict(self):
        """Converte para dicionário"""
        dados_dict = {}
        if self.dados:
            try:
                dados_dict = json.loads(self.dados)
            except:
                pass
        
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'acao': self.acao,
            'descricao': self.descricao,
            'ip_address': self.ip_address,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'nivel': self.nivel,
            'dados': dados_dict
        }
    
    def __repr__(self):
        return f'<LogAuditoria {self.acao} em {self.data_hora}>'
