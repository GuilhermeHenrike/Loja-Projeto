from database import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

# função de registro de usuario que recebe "name", "email", "password" e "user_type"
def registro_user(name, email, password, user_type='cliente'): 
    if not name or not email or not password: # se qualquer um não existir ele retorna nada e para
        return None
        
    conexao = db() # conecta com o banco de dados
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,)) # executa o comando
            if cursor.fetchone(): # procura um resultado
                return None # não retorna nada, só checa se existe o resultado
            
            # Criptografa a senha antes de salvar no banco
            criptografador = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)",
                (name, email, criptografador, user_type)
            )
            
        conexao.commit() # aqui commita e envia pro banco
        return True 
    finally:
        conexao.close() # fechando a conexao


def logar_user(email, password): # função de login de usuario que recebe "email", "password"
    if not email or not password: # se qualquer um não existir ele retorna nada e para
        return None

    conexao = db() # conecta com o banco de dados
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, name, email, password_hash, user_type FROM users WHERE email = %s", (email,)) 
            user_data = cursor.fetchone() # traz o resultado do usuário

            if user_data and check_password_hash(user_data['password_hash'], password): 
                return User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    user_type=user_data['user_type'] # Passa o tipo encontrado para a instância
                )
        return None
    finally:
        conexao.close() # fechando a conexao

def verificar_cliente(user_id):
    # vê se o usuário existe e é do tipo cliente
    if not user_id:
        return False
    conexao = db()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT user_type FROM users WHERE id = %s", (user_id,))
            resultado = cursor.fetchone()
            return resultado and resultado['user_type'] == 'cliente'
    except Exception:
        return False
    finally:
        conexao.close()

def verificar_vendedor(user_id):
    if not user_id:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            # busca o usuario pelo id dele no banco de dados
            cursor.execute("SELECT user_type FROM users WHERE id = %s", (user_id,))
            resultado = cursor.fetchone()
            
            # Se achou o usuário e o tipo dele for exatamente 'vendedor', retorna True
            if resultado and resultado['user_type'] == 'vendedor':
                return True
                
        return False # Se não for vendedor ou não achar o usuário, retorna False
    except Exception as e:
        print(f"Erro ao verificar permissão: {e}")
        return False
    finally:
        conexao.close()

def excluir_usuario(id_usuario, senha_atual):
    if not id_usuario or not senha_atual:
        return {"sucesso": False, "mensagem": "ID do usuário e senha são obrigatórios."}

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            # 1. Busca a senha criptografada do usuário
            cursor.execute("SELECT password_hash FROM users WHERE id = %s", (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                return {"sucesso": False, "mensagem": "Usuário não encontrado."}

            # Acessa direto como dicionário, igual ao seu método 'comprar'
            senha_hash_banco = usuario['password_hash']

            # 2. Verifica a senha
            if not check_password_hash(senha_hash_banco, senha_atual):
                return {"sucesso": False, "mensagem": "Senha incorreta! Não foi possível deletar a conta."}

            # 3. Deleta o usuário do banco
            cursor.execute("DELETE FROM users WHERE id = %s", (id_usuario,))
        
        conexao.commit()
        return {"sucesso": True, "mensagem": "Sua conta foi excluída com sucesso."}

    except Exception as e:
        print(f"Erro ao deletar conta no service: {e}")
        return {"sucesso": False, "mensagem": "Erro interno ao processar a exclusão."}
    finally:
        conexao.close()