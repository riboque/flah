"""
Gerenciador de Banco de Dados
Fornece métodos de alto nível para operações CRUD
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_, func
import secrets

from .models import db, Cliente, Dispositivo, Conexao, MensagemChat, Sessao, LogAuditoria


class DatabaseManager:
    """Classe para gerenciar operações do banco de dados"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa com a aplicação Flask"""
        self.app = app
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
    
    # ========================
    # OPERAÇÕES DE CLIENTES
    # ========================
    
    def criar_cliente(self, nome: str, email: str, senha: str = None, **kwargs) -> Cliente:
        """Cria um novo cliente"""
        cliente = Cliente(
            nome=nome,
            email=email,
            telefone=kwargs.get('telefone'),
            empresa=kwargs.get('empresa'),
            cargo=kwargs.get('cargo'),
            endereco=kwargs.get('endereco'),
            cidade=kwargs.get('cidade'),
            estado=kwargs.get('estado'),
            pais=kwargs.get('pais', 'Brasil'),
            cep=kwargs.get('cep'),
            cpf_cnpj=kwargs.get('cpf_cnpj'),
            nivel_acesso=kwargs.get('nivel_acesso', 'usuario'),
            observacoes=kwargs.get('observacoes')
        )
        
        if senha:
            cliente.set_senha(senha)
        
        if kwargs.get('dados_extras'):
            cliente.set_dados_extras(kwargs['dados_extras'])
        
        db.session.add(cliente)
        db.session.commit()
        
        self._log_acao(cliente.id, 'cliente_criado', f'Cliente {nome} criado')
        return cliente
    
    def obter_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Obtém cliente por ID"""
        return Cliente.query.get(cliente_id)
    
    def obter_cliente_por_email(self, email: str) -> Optional[Cliente]:
        """Obtém cliente por email"""
        return Cliente.query.filter_by(email=email).first()
    
    def listar_clientes(self, ativo: bool = None, busca: str = None, 
                        pagina: int = 1, por_pagina: int = 20) -> Dict:
        """Lista clientes com filtros e paginação"""
        query = Cliente.query
        
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        if busca:
            busca_like = f'%{busca}%'
            query = query.filter(
                or_(
                    Cliente.nome.ilike(busca_like),
                    Cliente.email.ilike(busca_like),
                    Cliente.empresa.ilike(busca_like),
                    Cliente.telefone.ilike(busca_like)
                )
            )
        
        query = query.order_by(Cliente.data_cadastro.desc())
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return {
            'clientes': [c.to_dict() for c in paginacao.items],
            'total': paginacao.total,
            'paginas': paginacao.pages,
            'pagina_atual': paginacao.page,
            'tem_proxima': paginacao.has_next,
            'tem_anterior': paginacao.has_prev
        }
    
    def atualizar_cliente(self, cliente_id: int, **kwargs) -> Optional[Cliente]:
        """Atualiza dados do cliente"""
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return None
        
        campos_atualizaveis = [
            'nome', 'telefone', 'empresa', 'cargo', 'endereco',
            'cidade', 'estado', 'pais', 'cep', 'cpf_cnpj',
            'nivel_acesso', 'observacoes', 'ativo'
        ]
        
        for campo in campos_atualizaveis:
            if campo in kwargs:
                setattr(cliente, campo, kwargs[campo])
        
        if 'senha' in kwargs and kwargs['senha']:
            cliente.set_senha(kwargs['senha'])
        
        if 'dados_extras' in kwargs:
            cliente.set_dados_extras(kwargs['dados_extras'])
        
        db.session.commit()
        self._log_acao(cliente_id, 'cliente_atualizado', f'Cliente {cliente.nome} atualizado')
        return cliente
    
    def deletar_cliente(self, cliente_id: int, soft_delete: bool = True) -> bool:
        """Deleta cliente (soft ou hard delete)"""
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return False
        
        if soft_delete:
            cliente.ativo = False
            db.session.commit()
            self._log_acao(cliente_id, 'cliente_desativado', f'Cliente {cliente.nome} desativado')
        else:
            db.session.delete(cliente)
            db.session.commit()
            self._log_acao(None, 'cliente_deletado', f'Cliente {cliente.nome} deletado permanentemente')
        
        return True
    
    def autenticar_cliente(self, email: str, senha: str) -> Optional[Cliente]:
        """Autentica cliente por email e senha"""
        print(f"[AUTH] Buscando cliente com email: {email}")
        cliente = Cliente.query.filter_by(email=email, ativo=True).first()
        
        if not cliente:
            print(f"[AUTH] Cliente não encontrado ou inativo")
            return None
        
        print(f"[AUTH] Cliente encontrado: {cliente.nome} (ID: {cliente.id})")
        print(f"[AUTH] Hash armazenado: {cliente.senha_hash[:50] if cliente.senha_hash else 'NENHUM'}...")
        
        senha_correta = cliente.verificar_senha(senha)
        print(f"[AUTH] Verificação de senha: {senha_correta}")
        
        if senha_correta:
            cliente.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            self._log_acao(cliente.id, 'login', 'Login realizado com sucesso')
            return cliente
        return None
    
    # ========================
    # OPERAÇÕES DE DISPOSITIVOS
    # ========================
    
    def registrar_dispositivo(self, system_info: Dict, cliente_id: int = None, 
                               ip_address: str = None) -> Dispositivo:
        """Registra um novo dispositivo ou atualiza existente"""
        # Buscar por hostname + MAC ou criar novo
        hostname = system_info.get('hostname', system_info.get('computador', 'desconhecido'))
        mac = system_info.get('mac_address')
        
        dispositivo = None
        if mac:
            dispositivo = Dispositivo.query.filter_by(mac_address=mac).first()
        
        if not dispositivo and hostname:
            dispositivo = Dispositivo.query.filter_by(hostname=hostname).first()
        
        if dispositivo:
            # Atualizar dispositivo existente
            dispositivo.ultimo_heartbeat = datetime.utcnow()
            dispositivo.ip_local = system_info.get('ip_local')
            dispositivo.ip_publico = ip_address or system_info.get('ip_publico')
            if cliente_id:
                dispositivo.cliente_id = cliente_id
        else:
            # Criar novo dispositivo
            dispositivo = Dispositivo(
                cliente_id=cliente_id,
                nome=system_info.get('nome', hostname),
                tipo=system_info.get('tipo', 'desktop'),
                sistema_operacional=system_info.get('sistema', system_info.get('sistema_operacional')),
                versao_so=system_info.get('versao'),
                hostname=hostname,
                ip_local=system_info.get('ip_local'),
                ip_publico=ip_address or system_info.get('ip_publico'),
                mac_address=mac,
                processador=system_info.get('processador'),
                memoria_total=system_info.get('memoria'),
                disco_total=system_info.get('disco'),
                is_virtual=system_info.get('is_virtual', False),
                virtual_type=system_info.get('virtual_type'),
                ultimo_heartbeat=datetime.utcnow()
            )
            dispositivo.set_info_extra(system_info)
            db.session.add(dispositivo)
        
        db.session.commit()
        return dispositivo
    
    def listar_dispositivos(self, cliente_id: int = None, ativo: bool = None,
                            pagina: int = 1, por_pagina: int = 50) -> Dict:
        """Lista dispositivos com filtros"""
        query = Dispositivo.query
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if ativo is not None:
            query = query.filter_by(ativo=ativo)
        
        # Filtrar dispositivos com heartbeat recente (últimos 5 minutos)
        limite = datetime.utcnow() - timedelta(minutes=5)
        
        query = query.order_by(Dispositivo.ultimo_heartbeat.desc())
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        dispositivos = []
        for d in paginacao.items:
            dados = d.to_dict()
            dados['online'] = d.ultimo_heartbeat and d.ultimo_heartbeat > limite
            dispositivos.append(dados)
        
        return {
            'dispositivos': dispositivos,
            'total': paginacao.total,
            'paginas': paginacao.pages,
            'pagina_atual': paginacao.page
        }
    
    def obter_dispositivo(self, dispositivo_id: int) -> Optional[Dispositivo]:
        """Obtém dispositivo por ID"""
        return Dispositivo.query.get(dispositivo_id)
    
    def atualizar_heartbeat(self, dispositivo_id: int) -> bool:
        """Atualiza heartbeat do dispositivo"""
        dispositivo = Dispositivo.query.get(dispositivo_id)
        if dispositivo:
            dispositivo.ultimo_heartbeat = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    # ========================
    # OPERAÇÕES DE CONEXÕES
    # ========================
    
    def registrar_conexoes(self, conexoes: List[Dict], dispositivo_id: int = None,
                           cliente_id: int = None) -> int:
        """Registra múltiplas conexões"""
        count = 0
        for conn in conexoes:
            conexao = Conexao(
                cliente_id=cliente_id,
                dispositivo_id=dispositivo_id,
                ip_origem=conn.get('ip_local', conn.get('laddr', {}).get('ip')),
                ip_destino=conn.get('ip_remoto', conn.get('raddr', {}).get('ip')),
                porta_origem=conn.get('porta_local', conn.get('laddr', {}).get('port')),
                porta_destino=conn.get('porta_remota', conn.get('raddr', {}).get('port')),
                protocolo=conn.get('type', 'TCP'),
                status=conn.get('status', 'ESTABLISHED'),
                processo=conn.get('processo', conn.get('name')),
                pid=conn.get('pid')
            )
            db.session.add(conexao)
            count += 1
        
        db.session.commit()
        return count
    
    def listar_conexoes(self, dispositivo_id: int = None, cliente_id: int = None,
                        data_inicio: datetime = None, data_fim: datetime = None,
                        pagina: int = 1, por_pagina: int = 100) -> Dict:
        """Lista conexões com filtros"""
        query = Conexao.query
        
        if dispositivo_id:
            query = query.filter_by(dispositivo_id=dispositivo_id)
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if data_inicio:
            query = query.filter(Conexao.data_hora >= data_inicio)
        
        if data_fim:
            query = query.filter(Conexao.data_hora <= data_fim)
        
        query = query.order_by(Conexao.data_hora.desc())
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return {
            'conexoes': [c.to_dict() for c in paginacao.items],
            'total': paginacao.total,
            'paginas': paginacao.pages,
            'pagina_atual': paginacao.page
        }
    
    # ========================
    # OPERAÇÕES DE CHAT
    # ========================
    
    def salvar_mensagem(self, usuario: str, mensagem: str, sala: str = 'geral',
                        cliente_id: int = None, tipo: str = 'texto') -> MensagemChat:
        """Salva uma mensagem no chat"""
        msg = MensagemChat(
            cliente_id=cliente_id,
            sala=sala,
            usuario=usuario,
            mensagem=mensagem,
            tipo=tipo
        )
        db.session.add(msg)
        db.session.commit()
        return msg
    
    def listar_mensagens(self, sala: str = 'geral', limite: int = 100,
                         antes_de: datetime = None) -> List[Dict]:
        """Lista mensagens de uma sala"""
        query = MensagemChat.query.filter_by(sala=sala, deletada=False)
        
        if antes_de:
            query = query.filter(MensagemChat.data_hora < antes_de)
        
        query = query.order_by(MensagemChat.data_hora.desc()).limit(limite)
        
        mensagens = [m.to_dict() for m in query.all()]
        mensagens.reverse()  # Ordenar do mais antigo para o mais recente
        return mensagens
    
    # ========================
    # OPERAÇÕES DE SESSÃO
    # ========================
    
    def criar_sessao(self, cliente_id: int, ip_address: str = None,
                     user_agent: str = None, duracao_horas: int = 24) -> Sessao:
        """Cria uma nova sessão"""
        token = secrets.token_urlsafe(64)
        sessao = Sessao(
            cliente_id=cliente_id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            data_expiracao=datetime.utcnow() + timedelta(hours=duracao_horas)
        )
        db.session.add(sessao)
        db.session.commit()
        return sessao
    
    def validar_sessao(self, token: str) -> Optional[Sessao]:
        """Valida uma sessão pelo token"""
        sessao = Sessao.query.filter_by(token=token, ativa=True).first()
        if sessao:
            if sessao.data_expiracao and sessao.data_expiracao < datetime.utcnow():
                sessao.ativa = False
                db.session.commit()
                return None
            
            sessao.ultima_atividade = datetime.utcnow()
            db.session.commit()
            return sessao
        return None
    
    def encerrar_sessao(self, token: str) -> bool:
        """Encerra uma sessão"""
        sessao = Sessao.query.filter_by(token=token).first()
        if sessao:
            sessao.ativa = False
            db.session.commit()
            return True
        return False
    
    # ========================
    # ESTATÍSTICAS
    # ========================
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        limite_online = datetime.utcnow() - timedelta(minutes=5)
        limite_ativo_30min = datetime.utcnow() - timedelta(minutes=30)
        
        return {
            'total_clientes': Cliente.query.count(),
            'clientes_ativos': Cliente.query.filter(
                Cliente.ultimo_acesso > limite_ativo_30min
            ).count() if hasattr(Cliente, 'ultimo_acesso') else Cliente.query.filter_by(ativo=True).count(),
            'total_dispositivos': Dispositivo.query.count(),
            'dispositivos_online': Dispositivo.query.filter(
                Dispositivo.ultimo_heartbeat > limite_online
            ).count(),
            'total_conexoes': Conexao.query.count(),
            'mensagens_hoje': MensagemChat.query.filter(
                MensagemChat.data_hora >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count(),
            'sessoes_ativas': Sessao.query.filter_by(ativa=True).count()
        }
    
    # ========================
    # LOGS DE AUDITORIA
    # ========================
    
    def _log_acao(self, cliente_id: int, acao: str, descricao: str = None,
                  ip_address: str = None, dados: Dict = None, nivel: str = 'info'):
        """Registra uma ação no log de auditoria"""
        try:
            import json
            log = LogAuditoria(
                cliente_id=cliente_id,
                acao=acao,
                descricao=descricao,
                ip_address=ip_address,
                dados=json.dumps(dados) if dados else None,
                nivel=nivel
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"[DB] Erro ao registrar log: {e}")
    
    def listar_logs(self, cliente_id: int = None, acao: str = None,
                    nivel: str = None, limite: int = 100) -> List[Dict]:
        """Lista logs de auditoria"""
        query = LogAuditoria.query
        
        if cliente_id:
            query = query.filter_by(cliente_id=cliente_id)
        
        if acao:
            query = query.filter_by(acao=acao)
        
        if nivel:
            query = query.filter_by(nivel=nivel)
        
        query = query.order_by(LogAuditoria.data_hora.desc()).limit(limite)
        return [l.to_dict() for l in query.all()]


# Instância global
db_manager = DatabaseManager()
