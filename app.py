from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy


app = Flask (__name__)
# CONFIGURAÇÕES DO BANCO DE DADOS
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///tarefas.db' #
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # para não mostrar um aviso de que o código tá desatualizado, mas não tem problema, pode deixar como está

db = SQLAlchemy(app) # cria o banco de dados, para que o código funcione, tem que estar conectado
socketio = SocketIO(app) # cria a conexão entre o servidor e o cliente, para que o código funcione, tem que estar conectado

class Tarefa(db.Model):
    __tabela_name__ = 'tarefas' # nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True) # id da tarefa, é a chave primária, ou seja, é o identificador
    conteudo = db.Column(db.String(200), nullable=False) # conteúdo da tarefa, é uma string de no máximo 200 caracteres, e não pode ser nula


app.config["SECRET"] = "ajuiahfa78fh9f78shfs768fgs7f6" # chave de seguranca, pode ser qualquer coisa, mas escolha algo dificil
app.config["DEBUG"] = True # para testarmos o código, no final tiramos
app.config["CORS_HEADERS"] = "Content-Type" # para permitir que o site seja acessado por outras máquinas
socketio = SocketIO(app, cors_allowed_origins="*") # cria a conexão entre diferentes máquinas que estão no mesmo site

# Rota principal do site.
@app.route("/") # cria a página do site
def home(): 
    todas_tarefas = Tarefa.query.order_by(Tarefa.id.desc()).all() # consulta todas as tarefas do banco de dados, ordenando por id em ordem decrescente
    total = len(todas_tarefas) # conta o total de tarefas
    return render_template("index.html", tarefas=todas_tarefas, total=total) # essa página vai carregar esse arquivo html que está aqui

# Lista simples para armazenar as tarefas na memória (enquanto o servidor rodar)
tarefas = []

# No topo, mantenha uma lista ou conte o banco de dados
tarefas_memoria = [] 

@socketio.on('nova_tarefa')
def handle_nova_tarefa(data):
    conteudo = data.get('conteudo')
    if conteudo:
        # Salvar no banco de dados
        nova_tarefa = Tarefa(conteudo=conteudo)
        db.session.add(nova_tarefa)
        db.session.commit()

        # Adicionar à lista de tarefas na memória
        total_tarefas = Tarefa.query.count() # conta o total de tarefas no banco de dados

        # Envia de volta para o cliente a nova tarefa e o total atualizado
        emit('atualizar_front',{
            'conteudo': conteudo,
            'total': total_tarefas
        }, broadcast=True) # broadcast=True para enviar para todos os clientes conectados) 


@socketio.on('excluir_tarefa')
def handle_excluir_tarefa(data):
    tarefa_id = data.get('id')
    # Busca no SQLite pelo ID
    tarefa = Tarefa.query.get(tarefa_id)
    
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
        
        novo_total = Tarefa.query.count()
        # Avisa todos os clientes para removerem o item da tela
        socketio.emit('remover_da_tela', {'id': tarefa_id, 'total': novo_total})
if __name__ == "__main__":
    # Garante que o banco de dados e a tabela existam
    with app.app_context():
        db.create_all() # cria o banco de dados e a tabela, se não existirem
    socketio.run(app, host='localhost') # define que o app vai rodar no seu servidor local, ou seja, na internet em que o seu computador tá conectado