from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
# Utilisez une clé secrète forte, par exemple via une variable d'environnement
# Pour un développement local simple, vous pouvez la définir ici,
# mais pour une application en production, utilisez os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = 'une_cle_secrete_tres_forte_et_unique_pour_votre_app'
socketio = SocketIO(app)

# Dictionnaire pour stocker les scores de tous les joueurs connectés
# La clé sera l'ID de session SocketIO (unique par connexion)
# La valeur sera le score du joueur
players_scores = {}

@app.route('/')
def index():
    """Route principale qui sert la page HTML du jeu."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Gère la connexion d'un nouveau client (joueur)."""
    player_id = request.sid # L'ID de session SocketIO du joueur
    print(f"DEBUG: Nouveau client connecté avec l'ID: {player_id}")

    # Initialise le score du nouveau joueur à 0
    players_scores[player_id] = 0

    # Envoie les scores actuels de TOUS les joueurs à TOUS les clients connectés
    # Cela permet aux nouveaux joueurs de voir les scores existants
    emit('current_scores', players_scores, broadcast=True)
    print(f"DEBUG: Scores actuels envoyés à tous: {players_scores}")

@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion d'un client (joueur)."""
    player_id = request.sid
    if player_id in players_scores:
        del players_scores[player_id] # Supprime le joueur déconnecté
        print(f"DEBUG: Client déconnecté: {player_id}. Scores restants: {players_scores}")
        # Met à jour les scores pour tous les clients après la déconnexion
        emit('current_scores', players_scores, broadcast=True)

@socketio.on('click_event')
def handle_click():
    """Gère l'événement de clic envoyé par un joueur."""
    player_id = request.sid # L'ID du joueur qui a cliqué
    if player_id in players_scores:
        players_scores[player_id] += 1 # Incrémente le score du joueur
        print(f"DEBUG: Joueur {player_id} a cliqué. Nouveau score: {players_scores[player_id]}")

        # Envoie l'événement de mise à jour de score à TOUS les clients
        # pour que tout le monde voie le score mis à jour en temps réel
        emit('update_score', {'player_id': player_id, 'score': players_scores[player_id]}, broadcast=True)

if __name__ == '__main__':
    print("Démarrage du serveur Flask-SocketIO...")
    print("Accessible sur http://0.0.0.0:5000 (ou votre IP locale:5000)")
    # 'host='0.0.0.0'' permet d'accéder au serveur depuis d'autres appareils sur le réseau local (Wi-Fi)
    # 'port=5000' est le port par défaut de Flask
    # 'debug=True' est utile pour le développement (rechargement automatique)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
