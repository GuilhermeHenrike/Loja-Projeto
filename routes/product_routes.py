from flask import request, jsonify
from services.user_service import verificar_vendedor, verificar_cliente
from services.product_service import cadastrar_produto, editar_produto, excluir_produto, listar_produtos, comprar

def carregar_rotas_produto(app):
    
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
        )

        if not sucesso:
            return jsonify({'erro': 'Erro ao cadastrar produto.'}), 500
        return jsonify({'mensagem': 'Cadastro realizado com sucesso'}), 201

    # 4. Rota para editar itens
    @app.route('/editarItem', methods=['PUT'])  
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
        produtos_objetos = listar_produtos() # Agora traz tudo, inclusive estoque 0
          
        if produtos_objetos is None:
            return jsonify({'erro': 'Erro interno ao carregar os produtos do banco.'}), 500

        # FILTRO: Apenas produtos com estoque > 0 para o cliente
        produtos_disponiveis = [p.to_dict() for p in produtos_objetos if p.stock > 0]

        if len(produtos_disponiveis) == 0:
            return jsonify({'mensagem': 'Nenhum produto disponível no momento.'}), 200

        # Envia apenas a lista filtrada
        return jsonify(produtos_disponiveis), 200

    # ================================== ROTAS DE CLIENTES ==================================

    # 7. Rota para o cliente comprar um produto (Diminuir estoque)
    @app.route('/comprarItem', methods=['POST'])
    def comprar_item_rota():
        dados = request.get_json() or {}
        user_id = dados.get('fkUser')
        product_id = dados.get('id')
        quantidade = dados.get('quantidade', 1) # assume que o usuario ta comprando um, até pq n da pra comprar 0

        # só pode comprar se for do tipo cliente
        if not verificar_cliente(user_id):
            return jsonify({'erro': 'Apenas usuários do tipo cliente podem comprar produtos.'}), 403

        # manda o id do produto que ta sendo comprado e a quantidade pra o metodo comprar
        resultado = comprar(product_id=product_id, quantidade_comprada=quantidade)

        # se der algum erro, retorna essa mensagem de erro
        if not resultado['sucesso']:
            return jsonify({'erro': resultado['erro']}), 400

        # se deu tudo certo, responde com sucesso para o flutter
        return jsonify({'mensagem': 'Compra realizada com sucesso!'}), 200