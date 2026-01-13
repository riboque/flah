"""
Rotas de API para gerenciamento de clientes no banco de dados
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from functools import wraps

# Blueprint
db_routes_bp = Blueprint('db_routes', __name__, url_prefix='/api/db')

# Referência ao gerenciador de banco
db_manager = None


def init_db_routes(manager):
    """Inicializa com o gerenciador de banco de dados"""
    global db_manager
    db_manager = manager


def require_api_key(f):
    """Decorator para exigir API key nas requisições"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        # Em produção, validar a API key contra o banco
        # Por enquanto, aceitar qualquer requisição autenticada
        return f(*args, **kwargs)
    return decorated


# ========================
# ROTAS DE CLIENTES
# ========================

@db_routes_bp.route('/clientes', methods=['GET'])
@require_api_key
def listar_clientes():
    """Lista todos os clientes com paginação e filtros"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 20, type=int)
        busca = request.args.get('busca')
        ativo = request.args.get('ativo')
        
        if ativo is not None:
            ativo = ativo.lower() == 'true'
        
        resultado = db_manager.listar_clientes(
            ativo=ativo,
            busca=busca,
            pagina=pagina,
            por_pagina=min(por_pagina, 100)  # Limitar a 100 por página
        )
        
        return jsonify({
            'success': True,
            **resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
@require_api_key
def obter_cliente(cliente_id):
    """Obtém detalhes de um cliente específico"""
    try:
        cliente = db_manager.obter_cliente(cliente_id)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'cliente': cliente.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/clientes', methods=['POST'])
@require_api_key
def criar_cliente():
    """Cria um novo cliente"""
    try:
        data = request.get_json() or {}
        
        # Validar campos obrigatórios
        if not data.get('nome'):
            return jsonify({'success': False, 'error': 'Nome é obrigatório'}), 400
        if not data.get('email'):
            return jsonify({'success': False, 'error': 'Email é obrigatório'}), 400
        
        # Verificar se email já existe
        existente = db_manager.obter_cliente_por_email(data['email'])
        if existente:
            return jsonify({'success': False, 'error': 'Email já cadastrado'}), 409
        
        cliente = db_manager.criar_cliente(
            nome=data['nome'],
            email=data['email'],
            senha=data.get('senha'),
            telefone=data.get('telefone'),
            empresa=data.get('empresa'),
            cargo=data.get('cargo'),
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            pais=data.get('pais'),
            cep=data.get('cep'),
            cpf_cnpj=data.get('cpf_cnpj'),
            nivel_acesso=data.get('nivel_acesso'),
            observacoes=data.get('observacoes'),
            dados_extras=data.get('dados_extras')
        )
        
        return jsonify({
            'success': True,
            'message': 'Cliente criado com sucesso',
            'cliente': cliente.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/clientes/<int:cliente_id>', methods=['PUT', 'PATCH'])
@require_api_key
def atualizar_cliente(cliente_id):
    """Atualiza dados de um cliente"""
    try:
        data = request.get_json() or {}
        
        cliente = db_manager.atualizar_cliente(cliente_id, **data)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Cliente atualizado com sucesso',
            'cliente': cliente.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
@require_api_key
def deletar_cliente(cliente_id):
    """Deleta um cliente (soft delete por padrão)"""
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'
        
        sucesso = db_manager.deletar_cliente(cliente_id, soft_delete=not hard_delete)
        if not sucesso:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Cliente deletado com sucesso'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# ROTAS DE DISPOSITIVOS
# ========================

@db_routes_bp.route('/dispositivos', methods=['GET'])
@require_api_key
def listar_dispositivos():
    """Lista todos os dispositivos"""
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        
        resultado = db_manager.listar_dispositivos(
            cliente_id=cliente_id,
            pagina=pagina,
            por_pagina=min(por_pagina, 100)
        )
        
        return jsonify({
            'success': True,
            **resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/dispositivos/<int:dispositivo_id>', methods=['GET'])
@require_api_key
def obter_dispositivo(dispositivo_id):
    """Obtém detalhes de um dispositivo"""
    try:
        dispositivo = db_manager.obter_dispositivo(dispositivo_id)
        if not dispositivo:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'dispositivo': dispositivo.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/dispositivos/registrar', methods=['POST'])
def registrar_dispositivo():
    """Registra ou atualiza um dispositivo"""
    try:
        data = request.get_json() or {}
        system_info = data.get('system_info', data)
        cliente_id = data.get('cliente_id')
        
        dispositivo = db_manager.registrar_dispositivo(
            system_info=system_info,
            cliente_id=cliente_id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': 'Dispositivo registrado',
            'dispositivo_id': dispositivo.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/dispositivos/<int:dispositivo_id>/heartbeat', methods=['POST'])
def heartbeat_dispositivo(dispositivo_id):
    """Atualiza heartbeat do dispositivo"""
    try:
        sucesso = db_manager.atualizar_heartbeat(dispositivo_id)
        if not sucesso:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# ROTAS DE CONEXÕES
# ========================

@db_routes_bp.route('/conexoes', methods=['GET'])
@require_api_key
def listar_conexoes():
    """Lista conexões com filtros"""
    try:
        dispositivo_id = request.args.get('dispositivo_id', type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        pagina = request.args.get('pagina', 1, type=int)
        
        resultado = db_manager.listar_conexoes(
            dispositivo_id=dispositivo_id,
            cliente_id=cliente_id,
            pagina=pagina
        )
        
        return jsonify({
            'success': True,
            **resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/conexoes/registrar', methods=['POST'])
def registrar_conexoes():
    """Registra múltiplas conexões"""
    try:
        data = request.get_json() or {}
        conexoes = data.get('conexoes', [])
        dispositivo_id = data.get('dispositivo_id')
        cliente_id = data.get('cliente_id')
        
        count = db_manager.registrar_conexoes(
            conexoes=conexoes,
            dispositivo_id=dispositivo_id,
            cliente_id=cliente_id
        )
        
        return jsonify({
            'success': True,
            'registradas': count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# ROTAS DE AUTENTICAÇÃO
# ========================

@db_routes_bp.route('/auth/login', methods=['POST'])
def login():
    """Autentica um cliente"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        senha = data.get('senha')
        
        print(f"[LOGIN] Tentativa de login para: {email}")
        
        if not email or not senha:
            print(f"[LOGIN] Email ou senha não fornecidos")
            return jsonify({'success': False, 'error': 'Email e senha são obrigatórios'}), 400
        
        if db_manager is None:
            print(f"[LOGIN] ERRO: db_manager não inicializado!")
            return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500
        
        cliente = db_manager.autenticar_cliente(email, senha)
        print(f"[LOGIN] Resultado autenticação: {cliente is not None}")
        
        if not cliente:
            return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
        
        # Criar sessão
        sessao = db_manager.criar_sessao(
            cliente_id=cliente.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        print(f"[LOGIN] Login bem-sucedido para: {cliente.nome}")
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'token': sessao.token,
            'cliente': cliente.to_dict()
        })
    except Exception as e:
        print(f"[LOGIN] Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Encerra a sessão"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.get_json().get('token') if request.is_json else None
        
        if token:
            db_manager.encerrar_sessao(token)
        
        return jsonify({
            'success': True,
            'message': 'Logout realizado'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/auth/validar', methods=['GET'])
def validar_sessao():
    """Valida uma sessão existente"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token não fornecido'}), 401
        
        sessao = db_manager.validar_sessao(token)
        if not sessao:
            return jsonify({'success': False, 'error': 'Sessão inválida ou expirada'}), 401
        
        cliente = db_manager.obter_cliente(sessao.cliente_id)
        
        return jsonify({
            'success': True,
            'valido': True,
            'cliente': cliente.to_dict() if cliente else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# ROTAS DE ESTATÍSTICAS
# ========================

@db_routes_bp.route('/estatisticas', methods=['GET'])
@require_api_key
def obter_estatisticas():
    """Retorna estatísticas do sistema"""
    try:
        stats = db_manager.obter_estatisticas()
        return jsonify({
            'success': True,
            'estatisticas': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/logs', methods=['GET'])
@require_api_key
def listar_logs():
    """Lista logs de auditoria"""
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        acao = request.args.get('acao')
        nivel = request.args.get('nivel')
        limite = request.args.get('limite', 100, type=int)
        
        logs = db_manager.listar_logs(
            cliente_id=cliente_id,
            acao=acao,
            nivel=nivel,
            limite=min(limite, 500)
        )
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================
# MENSAGENS DO CHAT
# ========================

@db_routes_bp.route('/chat/mensagens', methods=['GET'])
def listar_mensagens_chat():
    """Lista mensagens do chat"""
    try:
        sala = request.args.get('sala', 'geral')
        limite = request.args.get('limite', 100, type=int)
        
        mensagens = db_manager.listar_mensagens(
            sala=sala,
            limite=min(limite, 500)
        )
        
        return jsonify({
            'success': True,
            'mensagens': mensagens
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@db_routes_bp.route('/chat/mensagens', methods=['POST'])
def enviar_mensagem_chat():
    """Envia uma mensagem no chat"""
    try:
        data = request.get_json() or {}
        
        usuario = data.get('usuario', 'Anônimo')
        mensagem = data.get('mensagem')
        sala = data.get('sala', 'geral')
        cliente_id = data.get('cliente_id')
        
        if not mensagem:
            return jsonify({'success': False, 'error': 'Mensagem é obrigatória'}), 400
        
        msg = db_manager.salvar_mensagem(
            usuario=usuario,
            mensagem=mensagem,
            sala=sala,
            cliente_id=cliente_id
        )
        
        return jsonify({
            'success': True,
            'mensagem': msg.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
