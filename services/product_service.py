from database import db
from models.product import Product

def cadastrar_produto(user_id, category_id, nome, descricao, preco, estoque, image_url = None):
    # todos os atributos precisam existir
    if not user_id or not category_id or not nome or not descricao or not preco or not estoque:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = """
            INSERT INTO products (user_id, category_id, name, description, price, stock, image_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW());
            """
            cursor.execute(sql, (user_id, category_id, nome, descricao, preco, estoque, image_url))
        conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return False
    finally:
        conexao.close()


def editar_produto(produto_id, category_id, nome, descricao, preco, estoque, image_url=None):
    # todos os atributos precisam existir
    if not produto_id or not category_id or not nome or not descricao or not preco or not estoque:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            # Se uma nova imagem foi enviada, atualiza tudo incluindo a imagem
            if image_url:
                sql = """
                UPDATE products 
                SET category_id = %s, name = %s, description = %s, price = %s, stock = %s, image_url = %s
                WHERE id = %s;
                """
                cursor.execute(sql, (category_id, nome, descricao, preco, estoque, image_url, produto_id))
            else:
                # Se não mandou imagem, atualiza os dados e mantém a imagem antiga
                sql = """
                UPDATE products 
                SET category_id = %s, name = %s, description = %s, price = %s, stock = %s
                WHERE id = %s;
                """
                cursor.execute(sql, (category_id, nome, descricao, preco, estoque, produto_id))
                
        conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao editar: {e}")
        return False
    finally:
        conexao.close()

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

def comprar(product_id, quantidade_comprada=1):
    conexao = db()
    try:
        with conexao.cursor() as cursor:
            # Busca produto
            cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
            produto = cursor.fetchone()

            if not produto:
                return {"sucesso": False, "erro": "Produto não encontrado."}

            estoque_atual = int(produto['stock'])
            quantidade = int(quantidade_comprada)

            # 🔥 COMPRA NORMAL
            if quantidade > 0:
                if estoque_atual < quantidade:
                    return {"sucesso": False, "erro": "Desculpe, este produto acabou de esgotar!"}

            # 🔥 CANCELAMENTO (quantidade negativa)
            # aqui NÃO precisa validar estoque

            # 🔥 ATUALIZA ESTOQUE (funciona pros dois casos)
            novo_estoque = estoque_atual - quantidade

            cursor.execute(
                "UPDATE products SET stock = %s WHERE id = %s",
                (novo_estoque, product_id)
            )

        conexao.commit()
        return {"sucesso": True}

    except Exception as e:
        print(f"Erro ao atualizar estoque na compra: {e}")
        return {"sucesso": False, "erro": "Erro interno ao processar a compra."}

    finally:
        conexao.close()


def excluir_produto(produto_id):
    # se não tiver Id ele retorna nada
    if not produto_id:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = "DELETE FROM products WHERE id = %s;"
            cursor.execute(sql, (produto_id,))
        conexao.commit()
        return True
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        return False
    finally:
        conexao.close()

def listar_produtos():
    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = """
            SELECT p.id, p.user_id, p.category_id, p.name, p.description, 
                   p.price, p.stock, p.image_url, p.created_at, c.name as category_name
            FROM products p
            INNER JOIN categories c ON p.category_id = c.id
            WHERE p.stock > 0;
            """
            cursor.execute(sql) # roda o comando sql acima
            linhas = cursor.fetchall()
            
            produtos = []
            if linhas: # só faz o loop se o banco trouxe alguma linha
                for linha in linhas:
                    prod = Product(
                        id=linha['id'],
                        user_id=linha['user_id'],
                        name=linha['name'],
                        description=linha['description'],
                        price=linha['price'],
                        category_id=linha['category_id'],
                        category_name=linha['category_name'],
                        stock=linha['stock'],
                        image_url=linha['image_url'],
                        created_at=linha['created_at']
                    )
                    produtos.append(prod)
                
            return produtos # retorna a lista (mesmo que esteja vazia de produtos)
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        return None
    finally:
        conexao.close()

def buscar_todas_categorias():
    conexao = db()
    try:
        with conexao.cursor() as cursor:
            
            print("DEBUG: Executando SELECT id, name FROM categories")
            cursor.execute("SELECT id, name FROM categories")
            resultados = cursor.fetchall()
            
            return [{'id': r['id'], 'name': r['name']} for r in resultados]
    except Exception as e:
        # Mostra o erro
        print(f"ERRO NO BACKEND: {str(e)}")
        return []
    finally:
        conexao.close()