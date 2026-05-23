from flask import Flask
from flask_cors import CORS
from routes.rotas import carregar_rotas
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

carregar_rotas(app, mail)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)