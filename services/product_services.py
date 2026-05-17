from database import db
from models.product import Product

def cadastrar_produto(user_id, nome, descricao, preco):
    if not user_id or not nome or not descricao or not preco:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = """
            INSERT INTO products (user_id, name, description, price, created_at)
            VALUES (%s, %s, %s, %s, NOW());
            """
            cursor.execute(sql, (user_id, nome, descricao, preco))
        conexao.commit()
        return True
    except:
        return False
    finally:
        conexao.close()


def editar_produto(produto_id, novo_nome):
    if not produto_id or not novo_nome:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = "UPDATE products SET name = %s WHERE id = %s;"
            cursor.execute(sql, (novo_nome, produto_id))
        conexao.commit()
        return True
    except:
        return False
    finally:
        conexao.close()


def excluir_produto(produto_id):
    if not produto_id:
        return False

    conexao = db()
    try:
        with conexao.cursor() as cursor:
            sql = "DELETE FROM products WHERE id = %s;"
            cursor.execute(sql, (produto_id,))
        conexao.commit()
        return True
    except:
        return False
    finally:
        conexao.close()

def listar_produtos():
    conexao = db()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, user_id, name, description, price, created_at FROM products")
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
                        created_at=linha['created_at']
                    )
                    produtos.append(prod)
                
            return produtos # retorna a lista (mesmo que esteja vazia de produtos)
    except:
        return None # retorna nada se deu algum erro
    finally:
        conexao.close()