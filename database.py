import pymysql

# as configurações do banco

def db():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',         
        password='', # troca pra senha real do teu banco quando for testar, apanhei pra descobrir
        database='database_projeto', 
        cursorclass=pymysql.cursors.DictCursor 
    )