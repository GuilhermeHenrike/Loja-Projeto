import os
from flask import request, jsonify
from services.user_service import registro_user, logar_user, verificar_vendedor
from services.product_service import cadastrar_produto, editar_produto, excluir_produto, listar_produtos

UPLOAD_FOLDER = 'static/uploads'

def carregar_rotas(app):

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
    
    # ================================== ROTAS DE PRODUTOS ==================================

    # 3. Rota para cadastrar itens
    @app.route('/cadastrarItem', methods=['POST'])
    def cadastrar_item_rota():
        # pega os dados via form
        user_id = request.form.get('fkUser')
        category_id = request.form.get('category_id')
        nome = request.form.get('nomeProduto')
        descricao = request.form.get('descProd')
        preco = request.form.get('precoProd')
        estoque = request.form.get('estoqueProd')

        # Validação de segurança
        if not user_id or not nome or not descricao or not preco or not estoque or not category_id or not nome.strip() or not descricao.strip() if 'description' in locals() else not descricao.strip() or not str(category_id).strip():
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

        if not verificar_vendedor(user_id):
            return jsonify({'erro': 'Apenas usuários do tipo vendedor podem cadastrar produtos.'}), 403

        image_url = None

        if 'image' in request.files:
            arquivo = request.files['image']
            if arquivo.filename != '':
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
                arquivo.save(caminho)
                image_url = f"{request.url_root}{UPLOAD_FOLDER}/{arquivo.filename}"

        # chama o service atualizado usando os argumentos nomeados
        sucesso = cadastrar_produto(
            user_id=user_id,
            category_id=category_id.strip(),
            nome=nome.strip(),
            descricao=descricao.strip(),
            preco=preco,
            estoque=estoque,
            image_url=image_url
        )

        if not sucesso:
            return jsonify({'erro': 'Erro ao cadastrar produto.'}), 500

        return jsonify({'mensagem': 'Cadastro realizado com sucesso'}), 201

    # 4. Rota para editar itens
    @app.route('/editarItem', methods=['POST'])  
    def editar_item_rota():
        # pega os dados via form
        user_id = request.form.get('fkUser')
        product_id = request.form.get('id')
        category_id = request.form.get('category_id')
        name = request.form.get('nomeProduto')
        description = request.form.get('descProd')
        price = request.form.get('precoProd')
        stock = request.form.get('estoqueProd')

        # validação de segurança
        if not product_id or not category_id or not name or not description or not price or not stock or not name.strip() or not description.strip() or not str(category_id).strip():
            return jsonify({'erro': 'Todos os campos são obrigatórios para a edição'}), 400

        if not verificar_vendedor(user_id):
            return jsonify({'erro': 'Apenas usuários do tipo vendedor podem editar produtos.'}), 403

        image_url = None

        # Se o usuário escolheu uma NOVA imagem no flutter
        if 'image' in request.files:
            arquivo = request.files['image']
            if arquivo.filename != '':
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
                arquivo.save(caminho)
                image_url = f"{request.url_root}{UPLOAD_FOLDER}/{arquivo.filename}"

        # chama o service atualizado usando os argumentos nomeados
        sucesso = editar_produto(
            produto_id=product_id,
            category_id=category_id.strip(),
            nome=name.strip(),
            descricao=description.strip(),
            preco=price,
            estoque=stock,
            image_url=image_url
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