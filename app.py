from flask import Flask
from routes.rotas import carregar_rotas

app = Flask(__name__)

carregar_rotas(app)

if __name__ == '__main__':
    app.run(debug=True)