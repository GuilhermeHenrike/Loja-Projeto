import email

from flask_mail import Mail, Message
import random
from database import db
from flask import request, jsonify
from services.user_service import registro_user, logar_user
from werkzeug.security import generate_password_hash

def carregar_rotas_usuario(app, mail):

    # ================================== ROTAS DE USUARIOS ==================================

    # 1. rota de registro
    @app.route('/registro', methods=['POST'])
    def registro():
        data = request.get_json() or {} # da request do json para pegar as variaveis abaixo
        nome = data.get('nome')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type', 'cliente')

        # Se qualquer um deles não existir, for None ou for só espaços em branco aparece esse erro
        if not nome or not email or not password or not nome.strip() or not email.strip() or not password.strip():
            return jsonify({'message': 'Erro ao cadastrar, todos os campos são obrigatórios!'}), 400

        if user_type not in ['vendedor', 'cliente']:
            return jsonify({'message': 'Erro ao cadastrar, tipo de usuário inválido!'}), 400
        
        sucesso = registro_user(nome.strip(), email.strip(), password, user_type)
        # Se passou pela validação acima, aí entra aqui e registro_user recebe essas informações

        if not sucesso:
            return jsonify({'message': 'Erro ao cadastrar, email já registrado'}), 400
        # se chegou aqui é pq o metodo registro_user barrou pq o email já ta registrado no banco

        return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201
        # sucesso deu sucesso e o metodo registro_user salva o usuario no banco

    # 2. rota de login
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json() or {} # receber os dados vindo do usuario
        

        user_info = logar_user(data.get('email'), data.get('password'))
        # chama o metodo logar_user e adiciona os parametros "email" e "password" nele e o user_info recebe o usuario que o logar_user retorna 


        if not user_info:
            return jsonify({'message': 'Email ou senha incorretos'}), 401
        # se o user_info der erro é pq não achou um usuario com as informações e da essa mensagem acima

        
        # retorna o objeto criado no service com uma mensagem de sucesso
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'user': user_info.to_dict()
        }), 200

    @app.route('/recuperarSenha', methods=['POST'])
    def recuperarSenha():

        global codigo_recuperacao

        dadosRecebidos = request.get_json() or {}
        email = dadosRecebidos.get('email')

        if not email or not email.strip():
            return jsonify({'mensagem': 'Email é obrigatório'}), 400

        banco = db()
        cursor = banco.cursor()

        try:
            cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (email,))
            resultado = cursor.fetchone()

            if resultado:
                codigo_recuperacao = random.randint(100000, 999999)

                msg = Message(
                    subject='Recuperação de senha',
                    sender="nyedsomwander@gmail.com",
                    recipients=[email]
                )

                msg.body = f'Seu código de recuperação de senha é: {codigo_recuperacao}'

                
                mail.send(msg)

                return jsonify({'mensagem': 'Email enviado com sucesso!'})

            else:
                return jsonify({'mensagem': 'Email não encontrado.'})

        except Exception as e:
            return jsonify({
                'mensagem': 'Erro ao enviar email de recuperação.',
                'erro': str(e)  
            })

        finally:
            banco.close()


    @app.route('/verificarCodigo', methods=['POST'])
    def verificar_codigo():
        global codigo_recuperacao

        dados = request.get_json()
        codigo = dados.get("codigo")

        print("Código recebido:", codigo)
        print("Código correto:", codigo_recuperacao)

        if str(codigo) == str(codigo_recuperacao):
            return jsonify({"valido": True}), 200
        else:
            return jsonify({"valido": False}), 200
        


    @app.route('/redefinirSenha', methods = ['POST'])
    def redefinir_senha():
        dados = request.get_json()

        email = dados.get('email')
        nova_senha = dados.get('senha')

        if not email or not nova_senha:
            return jsonify({'mensagem' : 'o email e senha são campos obrigatórios'}), 400

    
        senha_hash = generate_password_hash(nova_senha)

        banco = db()
        cursor = banco.cursor()

        try:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (senha_hash, email)
            )
            banco.commit()

            return jsonify({'mensagem': 'Senha redefinida com sucesso!'})

        except Exception as e:
            return jsonify({ "erro" : str(e)})

        finally:
            banco.close()