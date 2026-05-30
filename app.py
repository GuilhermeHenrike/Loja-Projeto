from flask import Flask
from flask_cors import CORS
from routes.product_routes import carregar_rotas_produto
from routes.user_routes import carregar_rotas_usuario
from routes.cart_routes import carregar_rotas_carrinho
from routes.categories_routes import carregar_rotas_categories
from flask_cors import CORS
from flask_mail import Mail

app = Flask(__name__)
CORS(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nyedsomwander@gmail.com'
app.config['MAIL_PASSWORD'] = 'kjes ebpr hoxp ertu'

mail = Mail(app)

carregar_rotas_usuario(app, mail)
carregar_rotas_produto(app)
carregar_rotas_carrinho(app)
carregar_rotas_categories(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)