from flask import request, jsonify
from database import db

def carregar_rotas_carrinho(app):

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