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
            SELECT id, user_id, category_id, name, description, price, stock, image_url, created_at 
            FROM products 
            WHERE stock > 0;
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
                        category_name=str(linha['category_id']),
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