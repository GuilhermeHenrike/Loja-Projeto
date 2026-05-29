
import email

from flask_mail import Mail, Message
import random
from database import db
import os
from flask import app, request, jsonify
from services.user_service import registro_user, logar_user, verificar_vendedor
from services.product_service import cadastrar_produto, editar_produto, excluir_produto, listar_produtos, comprar, verificar_cliente, buscar_todas_categorias
from werkzeug.security import generate_password_hash

UPLOAD_FOLDER = 'static/uploads'

def carregar_rotas(app, mail):


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
    
    # ================================== ROTAS DE VENDEDOR ==================================


     # 8. Rota para listar produtos de um vendedor específico
    @app.route('/listarProdutosVendedor', methods=['GET'])
    def listar_produtos_vendedor_rota():
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({'erro': 'ID do vendedor não fornecido'}), 400

        produtos_objetos = listar_produtos()
        
        # filtro para pegar os produtos só do usuario logado pelo ID dele
        produtos_do_vendedor = [p.to_dict() for p in produtos_objetos if str(p.user_id) == str(user_id)]
        
        return jsonify(produtos_do_vendedor), 200


    # ================================== ROTAS DE PRODUTOS ==================================

    # 3. Rota para cadastrar itens
    @app.route('/cadastrarItem', methods=['POST'])
    def cadastrar_item_rota():
        data = request.get_json() or {}
        print(f"DEBUG RECEBIDO: {data}")
        
        user_id = data.get('fkUser')
        category_id = data.get('category_id')
        nome = data.get('nome')          
        descricao = data.get('descricao')
        preco = data.get('preco')        
        estoque = data.get('estoque')  

        # Validação segura
        if not all([user_id, nome, descricao, preco, estoque, category_id]):
            print(f"DEBUG: Falha. Dados: {user_id}, {nome}, {descricao}, {preco}, {estoque}, {category_id}")
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

        if not verificar_vendedor(user_id):
            return jsonify({'erro': 'Apenas vendedores podem cadastrar.'}), 403

        # Chamada ao Service
        sucesso = cadastrar_produto(
            user_id=str(user_id),
            category_id=str(category_id).strip(),
            nome=str(nome).strip(),
            descricao=str(descricao).strip(),
            preco=str(preco),
            estoque=str(estoque),
            image_url=None
        )

        if not sucesso:
            return jsonify({'erro': 'Erro ao cadastrar produto.'}), 500
        return jsonify({'mensagem': 'Cadastro realizado com sucesso'}), 201

    # 4. Rota para editar itens
    @app.route('/editarItem', methods=['POST'])  
    def editar_item_rota():
        data = request.get_json() or {}
        user_id = data.get('fkUser')
        product_id = data.get('id')
        category_id = data.get('category_id')
        name = data.get('nomeProduto')
        description = data.get('descProd')
        price = data.get('precoProd')
        stock = data.get('estoqueProd')

        if not all([product_id, category_id, name, description, price, stock]):
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

        if not verificar_vendedor(user_id):
            return jsonify({'erro': 'Apenas vendedores podem editar.'}), 403

        sucesso = editar_produto(
            produto_id=product_id,
            category_id=str(category_id).strip(),
            nome=str(name).strip(),
            descricao=str(description).strip(),
            preco=str(price),
            estoque=str(stock),
            image_url=None
        )

        if not sucesso:
            return jsonify({'erro': 'Erro ao atualizar o item.'}), 500
        return jsonify({'mensagem': 'Item atualizado com sucesso'}), 200


    # 5. Rota para excluir itens
    @app.route('/excluirItem', methods=['DELETE'])
    def excluir_item_rota():
        dados = request.get_json() or {}
        user_id = dados.get('fkUser') 
        produto_id = dados.get('id')

        if not verificar_vendedor(user_id):
            return jsonify({'erro': 'Apenas usuários do tipo vendedor podem excluir produtos.'}), 403

        # Chama o service para fazer o DELETE pelo id do produto
        sucesso = excluir_produto(produto_id)
        
        if not sucesso:
            return jsonify({'erro': 'Erro ao deletar o item.'}), 500

        return jsonify({'mensagem': 'Item deletado com sucesso'}), 200
    
    # 6. Rota para listar itens
    @app.route('/listarProdutos', methods=['GET'])
    def listar_produtos_rota():
        produtos_objetos = listar_produtos()
          
        if produtos_objetos is None:
            return jsonify({'erro': 'Erro interno ao carregar os produtos do banco.'}), 500

        # Se o banco funcionou, mas a tabela ta vazia
        if len(produtos_objetos) == 0:
            return jsonify({'mensagem': 'Nenhum produto cadastrado ainda.'}), 200

        # se deu tudo certo e tem produtos, converte usando o to_dict() e envia a lista
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




          
    # ================================== ROTAS DE CLIENTES ==================================

    # 7. Rota para o cliente comprar um produto (Diminuir estoque)
    @app.route('/comprarItem', methods=['POST'])
    def comprar_item_rota():
        dados = request.get_json() or {}
        user_id = dados.get('fkUser')
        product_id = dados.get('id')
        quantidade = int(dados.get('quantidade', 1))

        # só pode comprar se for cliente
        if not verificar_cliente(user_id):
            return jsonify({'erro': 'Apenas usuários do tipo cliente podem comprar produtos.'}), 403

        if quantidade < 0:
            resultado = comprar(
                product_id=product_id,
                quantidade_comprada=quantidade  # negativo
            )

            if not resultado['sucesso']:
                return jsonify({'erro': resultado['erro']}), 400

            return jsonify({'mensagem': 'Item removido do carrinho!'}), 200

        resultado = comprar(
            product_id=product_id,
            quantidade_comprada=quantidade
        )

        if not resultado['sucesso']:
            return jsonify({'erro': resultado['erro']}), 400

        return jsonify({'mensagem': 'Compra realizada com sucesso!'}), 200
    
    # ================================== ROTAS DE CATEGORIAS ==================================


    @app.route('/listarCategorias', methods=['GET'])
    def listar_categorias_rota():
        try:
            categories = buscar_todas_categorias()
            return jsonify(categories), 200
        except Exception as e:
            return jsonify({'erro': str(e)}), 500
        

   # ================= CARRINHO =================

    @app.route('/carrinho/adicionar', methods=['POST'])
    def adicionar_carrinho():
        data = request.get_json()

        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantidade = data.get('quantidade')

        if not user_id or not product_id or not quantidade:
            return jsonify({"erro": "dados incompletos"}), 400

        banco = None
        cursor = None

        try:
            banco = db()
            cursor = banco.cursor()

            cursor.execute("""
                INSERT INTO cart_items (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (user_id, product_id, quantidade))

            banco.commit()

            return jsonify({"msg": "Item adicionado"}), 200

        except Exception as e:
            return jsonify({"erro": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if banco:
                banco.close()

    @app.route('/carrinho/listar', methods=['GET'])
    def listar_carrinho():
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"erro": "user_id não enviado"}), 400

        try:
            user_id = int(user_id)
        except:
            return jsonify({"erro": "user_id inválido"}), 400

        banco = None
        cursor = None

        try:
            banco = db()
            cursor = banco.cursor()

            cursor.execute("""
                SELECT c.id, p.name, p.price, c.quantity
                FROM cart_items c
                JOIN products p ON p.id = c.product_id
                WHERE c.user_id = %s
            """, (user_id,))

            rows = cursor.fetchall()

            print("ROWS:", rows)  # 🔥 DEBUG

            resultado = []

            for row in rows:
                # 🔥 AGORA USANDO COMO DICIONÁRIO
                resultado.append({
                    "id": int(row["id"]),
                    "name": str(row["name"]),
                    "price": float(row["price"]),
                    "quantity": int(row["quantity"])
                })

            return jsonify(resultado), 200

        except Exception as e:
            print("ERRO REAL:", repr(e))
            return jsonify({"erro": repr(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if banco:
                banco.close()
    @app.route('/carrinho/remover', methods=['DELETE'])
    def remover_carrinho():
        data = request.get_json()
        item_id = data.get('id')

        if not item_id:
            return jsonify({"erro": "id não enviado"}), 400

        banco = None
        cursor = None

        try:
            banco = db()
            cursor = banco.cursor()

            cursor.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
            banco.commit()

            return jsonify({"msg": "Item removido"}), 200

        except Exception as e:
            return jsonify({"erro": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if banco:
                banco.close()