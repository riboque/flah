# Sistema de Monitoramento - Versão com Banco de Dados Online

## 📋 Visão Geral

Esta versão do sistema de monitoramento foi adaptada para suportar **banco de dados online**, permitindo armazenar dados de clientes, dispositivos, conexões e mensagens em bancos de dados como:

- **PostgreSQL** (recomendado para produção)
- **MySQL** / **MariaDB**
- **SQLite** (padrão para desenvolvimento)
- Provedores Cloud: ElephantSQL, Neon, Supabase, PlanetScale, Railway, etc.

---

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

Edite o `.env` com a URL do seu banco de dados:

```env
# SQLite local (padrão)
DATABASE_URL=sqlite:///data/clientes.db

# PostgreSQL
DATABASE_URL=postgresql://usuario:senha@host:5432/database

# MySQL
DATABASE_URL=mysql://usuario:senha@host:3306/database
```

### 3. Configurar o Banco

Execute o script de configuração:

```bash
python setup_database.py
```

### 4. Iniciar o Servidor

```bash
python run.py
```

Acesse: `http://localhost:5000`

---

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

| Tabela | Descrição |
|--------|-----------|
| `clientes` | Dados dos clientes (nome, email, empresa, etc.) |
| `dispositivos` | Dispositivos registrados (hostname, IP, SO, etc.) |
| `conexoes` | Histórico de conexões de rede |
| `mensagens_chat` | Mensagens do chat |
| `sessoes` | Sessões ativas de usuários |
| `logs_auditoria` | Logs de auditoria do sistema |

### Modelo de Cliente

```python
Cliente:
- id: Integer (PK)
- nome: String(100)
- email: String(120) - único
- senha_hash: String(256)
- telefone: String(20)
- empresa: String(100)
- cargo: String(50)
- endereco: Text
- cidade, estado, pais, cep
- cpf_cnpj: String(20)
- ativo: Boolean
- nivel_acesso: String(20) - admin/moderador/usuario
- data_cadastro: DateTime
- ultimo_acesso: DateTime
- observacoes: Text
- dados_extras: Text (JSON)
```

---

## 🔌 API REST

### Endpoints de Clientes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/db/clientes` | Listar clientes (paginado) |
| GET | `/api/db/clientes/{id}` | Obter cliente |
| POST | `/api/db/clientes` | Criar cliente |
| PUT | `/api/db/clientes/{id}` | Atualizar cliente |
| DELETE | `/api/db/clientes/{id}` | Deletar cliente |

### Endpoints de Dispositivos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/db/dispositivos` | Listar dispositivos |
| GET | `/api/db/dispositivos/{id}` | Obter dispositivo |
| POST | `/api/db/dispositivos/registrar` | Registrar dispositivo |
| POST | `/api/db/dispositivos/{id}/heartbeat` | Atualizar heartbeat |

### Endpoints de Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/db/auth/login` | Login (retorna token) |
| POST | `/api/db/auth/logout` | Logout |
| GET | `/api/db/auth/validar` | Validar sessão |

### Endpoints Adicionais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/db/estatisticas` | Estatísticas do sistema |
| GET | `/api/db/logs` | Logs de auditoria |
| GET | `/api/db/conexoes` | Listar conexões |
| POST | `/api/db/conexoes/registrar` | Registrar conexões |
| GET | `/api/db/chat/mensagens` | Listar mensagens |
| POST | `/api/db/chat/mensagens` | Enviar mensagem |

---

## 🖥️ Interface Web

### Página de Gerenciamento de Clientes

Acesse: `http://localhost:5000/clientes`

Funcionalidades:
- ✅ Listar clientes com busca e filtros
- ✅ Criar novos clientes
- ✅ Editar clientes existentes
- ✅ Ver detalhes do cliente
- ✅ Desativar/excluir clientes
- ✅ Paginação automática
- ✅ Estatísticas em tempo real

---

## ☁️ Provedores de Banco Online (Gratuitos)

### ElephantSQL (PostgreSQL)
- **Site:** https://www.elephantsql.com
- **Gratuito:** 20MB
- **URL:** `postgresql://usuario:senha@tiny.db.elephantsql.com/database`

### Neon (PostgreSQL Serverless)
- **Site:** https://neon.tech
- **Gratuito:** 512MB + 3GB de branching
- **URL:** `postgresql://usuario:senha@ep-xxx.us-east-1.aws.neon.tech/database?sslmode=require`

### Supabase (PostgreSQL)
- **Site:** https://supabase.com
- **Gratuito:** 500MB + muitos recursos
- **URL:** `postgresql://postgres:senha@db.xxx.supabase.co:5432/postgres`

### PlanetScale (MySQL Serverless)
- **Site:** https://planetscale.com
- **Gratuito:** 5GB + branching
- **URL:** `mysql://usuario:senha@aws.connect.psdb.cloud/database?ssl=true`

### Railway
- **Site:** https://railway.app
- **Gratuito:** $5 de créditos/mês
- **URL:** `postgresql://postgres:senha@containers-xxx.railway.app:5432/railway`

---

## 📁 Estrutura de Arquivos

```
flask_app copy/
├── app.py                 # Aplicação principal
├── run.py                 # Script de inicialização
├── setup_database.py      # Script de configuração do BD
├── requirements.txt       # Dependências
├── .env                   # Configurações (não commitar!)
├── .env.example           # Exemplo de configuração
│
├── database/              # Módulo de banco de dados
│   ├── __init__.py
│   ├── models.py          # Modelos SQLAlchemy (ORM)
│   ├── db_manager.py      # Gerenciador de operações
│   └── db_config.py       # Configurações do banco
│
├── routes/
│   ├── db_routes.py       # Rotas da API de banco de dados
│   └── ...                # Outras rotas
│
├── templates/
│   ├── clientes.html      # Página de gerenciamento de clientes
│   └── ...                # Outros templates
│
└── data/                  # Dados locais (SQLite)
    └── clientes.db        # Banco SQLite (se usar)
```

---

## 🔐 Segurança

- Senhas são armazenadas com hash (Werkzeug)
- Suporte a SSL para bancos cloud
- Logs de auditoria de todas as ações
- Sessões com token seguro e expiração
- Validação de entrada em todas as APIs

---

## 📝 Exemplos de Uso da API

### Criar Cliente

```bash
curl -X POST http://localhost:5000/api/db/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@empresa.com",
    "telefone": "(11) 99999-9999",
    "empresa": "Empresa XYZ",
    "senha": "senha123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/db/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@empresa.com",
    "senha": "senha123"
  }'
```

### Listar Clientes

```bash
curl http://localhost:5000/api/db/clientes?pagina=1&busca=joao
```

### Registrar Dispositivo

```bash
curl -X POST http://localhost:5000/api/db/dispositivos/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "system_info": {
      "hostname": "PC-ESCRITORIO",
      "sistema": "Windows 11",
      "ip_local": "192.168.1.100",
      "processador": "Intel Core i7"
    },
    "cliente_id": 1
  }'
```

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique a URL do banco de dados no `.env`
2. Execute `python setup_database.py` para diagnóstico
3. Verifique os logs no console do servidor
4. Teste a conexão com o banco diretamente

---

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.
