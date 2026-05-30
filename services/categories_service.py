from database import db

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