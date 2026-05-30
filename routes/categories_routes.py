from flask import request, jsonify
from database import db

def carregar_rotas_categories(app):

    # ================================== ROTAS DE CATEGORIAS (FILTRO/CLIENTE) ==================================

    @app.route('/listarCategorias', methods=['GET'])
    def listar_categorias_cliente():
        conexao = db()
        cursor = conexao.cursor()
        
        cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
        resultado = cursor.fetchall()
        
        cursor.close()
        return jsonify(resultado), 200
        
    # ================================== ROTAS DE CATEGORIAS (VENDEDOR) ==================================

    # CRIAR CATEGORIA
    @app.route('/criar_categoria/<int:id_vendedor>', methods=['POST'])
    def criar_categoria(id_vendedor):
        conexao = db()

        try:
            dados = request.get_json()
            nome = dados.get('name', '').strip()
            
            cursor = conexao.cursor()
            sql = "INSERT INTO categories (name, user_id) VALUES (%s, %s)"
            cursor.execute(sql, (nome, id_vendedor))
            conexao.commit()
            return jsonify({"sucesso": True, "mensagem": "Criada com sucesso!"}), 201
        except Exception as e:
            return jsonify({"sucesso": False, "erro": str(e)}), 400
        finally:
            cursor.close()

    # BUSCAR CATEGORIAS (Globais e as do Vendedor)
    @app.route('/buscar_categorias/<int:id_vendedor>', methods=['GET'])
    def buscar_categorias(id_vendedor):
        conexao = db()

        try:
            cursor = conexao.cursor()
            sql = "SELECT id, name, user_id FROM categories WHERE user_id IS NULL OR user_id = %s ORDER BY name ASC"
            cursor.execute(sql, (id_vendedor,))
            return jsonify(cursor.fetchall()), 200
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()

    # EDITAR CATEGORIA (Apenas se pertencer ao vendedor)
    @app.route('/editar_categoria/<int:id_categoria>/<int:id_vendedor>', methods=['PUT'])
    def editar_categoria(id_categoria, id_vendedor):
        conexao = db()
        cursor = conexao.cursor()

        try:
            dados = request.get_json()
            novo_nome = dados.get('name', '').strip()
            
            # VALIDAÇÃO: Verifica se a categoria existe E é do vendedor
            sql = "SELECT id FROM categories WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (id_categoria, id_vendedor))
            categoria_existe = cursor.fetchone()
            
            if not categoria_existe:
                return jsonify({"sucesso": False, "mensagem": "Não permitido ou não encontrado."}), 403
            
            # ALTERAÇÃO: Se passou na validação, atualiza sem medo
            sql = "UPDATE categories SET name = %s WHERE id = %s"
            cursor.execute(sql, (novo_nome, id_categoria))
            conexao.commit()
                
            return jsonify({"sucesso": True, "mensagem": "Atualizada com sucesso!"}), 200
        except Exception as e:
            return jsonify({"sucesso": False, "erro": str(e)}), 400
        finally:
            cursor.close()

    # DELETAR CATEGORIA (Apenas se pertencer ao vendedor)
    @app.route('/deletar_categoria/<int:id_categoria>/<int:id_vendedor>', methods=['DELETE'])
    def deletar_categoria(id_categoria, id_vendedor):
        conexao = db()
        cursor = None

        try:
            cursor = conexao.cursor()

            # VALIDAÇÃO: Verifica se a categoria pertence ao vendedor.
            sql_check = "SELECT id FROM categories WHERE id = %s AND user_id = %s"
            cursor.execute(sql_check, (id_categoria, id_vendedor))
            categoria_existe = cursor.fetchone()
            
            if not categoria_existe:
                return jsonify({
                    "sucesso": False, 
                    "mensagem": "Você não tem permissão para deletar esta categoria."
                }), 403
            
            # MIGRAR CASO CATEGORIA SEJA APAGADA: Move os produtos para a categoria ID 20 ("Outros")
            sql_move = "UPDATE products SET category_id = 20 WHERE category_id = %s"
            cursor.execute(sql_move, (id_categoria,))
            
            # EXCLUSÃO: Agora que os produtos foram movidos, podemos deletar a categoria
            sql_delete = "DELETE FROM categories WHERE id = %s"
            cursor.execute(sql_delete, (id_categoria,))
            
            conexao.commit()
            return jsonify({"sucesso": True, "mensagem": "Categoria deletada e produtos movidos para 'Outros'!"}), 200

        except Exception as e:
            # Em caso de qualquer erro, desfaz as alterações (rollback) para manter a integridade
            if conexao: 
                conexao.rollback()
            return jsonify({"sucesso": False, "erro": str(e)}), 500
            
        finally:
            # Fecha tudo para liberar a conexão no banco de dados
            if cursor: cursor.close()
            if conexao: conexao.close()