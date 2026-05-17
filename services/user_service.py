from database import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

# função de registro de usuario que recebe "name", "email", "password"
def registro_user(name, email, password): 
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

            # aqui insere o usuario
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, criptografador)
            )
            
        conexao.commit() # aqui commita e envia pro banco
        return True 
    finally:
        conexao.close() # fechando a conexao

def logar_user(email, password): # função de registro de usuario que recebe "email", "password"
    if not email or not password: # se qualquer um não existir ele retorna nada e para
        return None

    conexao = db() # conecta com o banco de dados
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,)) # Executa o comando sql
            user_data = cursor.fetchone() # só checa se existe o resultado

            if user_data and check_password_hash(user_data['password_hash'], password): # checa se a senha do usuario bate com a senha no banco e se bater retorna o user
                return User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash']
                )
        return None
    finally:
        conexao.close() # fechando a conexao