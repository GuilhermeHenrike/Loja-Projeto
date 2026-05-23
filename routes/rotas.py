import email

from flask import app, request, jsonify
from services.user_service import registro_user, logar_user
from services.product_services import cadastrar_produto, editar_produto, excluir_produto, listar_produtos
from flask_mail import Mail, Message
import random
from database import db
def carregar_rotas(app, mail):

    # 1. rota de registro
    @app.route('/registro', methods=['POST'])
    def registro():
        data = request.get_json() or {} # Recebe os dados do usuário
        
        # Pega os dados e limpa os espaços em branco com .strip()
        nome = data.get('nome')
        email = data.get('email')
        password = data.get('password')

        # Se qualquer um deles não existir, for None ou for só espaços em branco aparece esse erro
        if not nome or not email or not password or not nome.strip() or not email.strip() or not password.strip():
            return jsonify({'message': 'Erro ao cadastrar. Todos os campos (nome, email e senha) são obrigatórios!'}), 400

        sucesso = registro_user(nome.strip(), email.strip(), password)
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
            return jsonify({'message': 'E-mail ou senha incorretos'}), 401
        # se o user_info der erro é pq não achou um usuario com as informações e da essa mensagem acima

        
        # retorna o objeto criado no service com uma mensagem de sucesso
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'user': user_info.to_dict()
        }), 200
    
    # ================================== ROTAS DE PRODUTOS ==================================

    # 3. Rota para cadastrar itens
    @app.route('/cadastrarItem', methods=['POST'])
    def cadastrar_item_rota():
        dados = request.get_json() or {}
        
        user_id = dados.get('fkUser')
        nome = dados.get('nomeProduto')
        descricao = dados.get('descProd')
        preco = dados.get('precoProd')

        # validação de segurança igual a de registro
        if not user_id or not nome or not descricao or not preco:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

        # passa os dados limpos para o service fazer o INSERT
        sucesso = cadastrar_produto(user_id, nome.strip(), descricao.strip(), preco)

        if not sucesso:
            return jsonify({'erro': 'Erro ao cadastrar produto.'}), 500
        # entra aqui em qualquer erro do metodo

        return jsonify({'mensagem': 'Cadastro realizado com sucesso'}), 201
        # retorna mensagem de sucesso


    # 4. Rota para editar itens
    @app.route('/editarItem', methods=['PUT'])
    def editar_item_rota():
        dados = request.get_json() or {}
        
        produto_id = dados.get('id')
        novo_nome = dados.get('nomeProduto')

        if not produto_id or not novo_nome or not novo_nome.strip():
            return jsonify({'erro': 'ID e nome são obrigatórios'}), 400

        # Chama o service para fazer o UPDATE
        sucesso = editar_produto(produto_id, novo_nome.strip())

        if not sucesso:
            return jsonify({'erro': 'Erro ao atualizar o item.'}), 500

        return jsonify({'mensagem': 'Item atualizado com sucesso'}), 200


    # 5. Rota para excluir itens
    @app.route('/excluirItens', methods=['DELETE'])
    def excluir_item_rota():
        dados = request.get_json() or {}
        produto_id = dados.get('id')

        if not produto_id:
            return jsonify({'erro': 'ID é obrigatório'}), 400

        # Chama o service para fazer o DELETE
        sucesso = excluir_produto(produto_id)

        if not sucesso:
            return jsonify({'erro': 'Erro ao deletar o item.'}), 500

        return jsonify({'mensagem': 'Item deletado com sucesso'}), 200
    
    @app.route('/produtos', methods=['GET'])
    def listar_produtos_rota():
        produtos_objetos = listar_produtos()
        
        # se deu erro na execução do banco
        if produtos_objetos is None:
            return jsonify({'erro': 'Não foi possível carregar os produtos. Falha interna no servidor.'}), 500
            
        # Se o banco funcionou, mas a tabela ta vazia
        if len(produtos_objetos) == 0:
            return jsonify({'mensagem': 'Nenhum produto cadastrado ainda.'}), 200

        # s deu tudo certo e tem produtos, converte e envia a lista
        produtos_json = [p.to_dict() for p in produtos_objetos]
        return jsonify(produtos_json), 200
    
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