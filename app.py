from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask (__name__)
app.config["SECRET"] = "ajuiahfa78fh9f78shfs768fgs7f6" # chave de seguranca, pode ser qualquer coisa, mas escolha algo dificil
app.config["DEBUG"] = True # para testarmos o código, no final tiramos
app.config["CORS_HEADERS"] = "Content-Type" # para permitir que o site seja acessado por outras máquinas
socketio = SocketIO(app, cors_allowed_origins="*") # cria a conexão entre diferentes máquinas que estão no mesmo site

@app.route("/") # cria a página do site
def home(): 
    return render_template("index.html") # essa página vai carregar esse arquivo html que está aqui

# Lista simples para armazenar as tarefas na memória (enquanto o servidor rodar)
tarefas = []

@socketio.on('nova_tarefa')
def handle_nova_tarefa(data):
    texto = data.get('conteudo')
    if texto:
        tarefas.append(texto)
        # Envia a nova tarefa para TODOS os usuários conectados
        socketio.emit('atualizar_lista', {'conteudo': texto, 'total': len(tarefas)})

if __name__ == "__main__":
    socketio.run(app, host='localhost') # define que o app vai rodar no seu servidor local, ou seja, na internet em que o seu computador tá conectado