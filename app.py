from flask import Flask
from flask_cors import CORS
from routes.rotas import carregar_rotas

app = Flask(__name__)
CORS(app)

carregar_rotas(app)

if __name__ == '__main__':
    app.run(debug=True)