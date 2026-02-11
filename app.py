from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
DATABASE = 'messages.db'

def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Création de la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Retourne une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Page principale du client web"""
    return render_template('index.html')

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Récupère tous les messages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer les 50 derniers messages
    cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 50')
    messages = cursor.fetchall()
    
    conn.close()
    
    # Convertir les messages en dictionnaires
    messages_list = [
        {
            'id': msg['id'],
            'username': msg['username'],
            'content': msg['content'],
            'timestamp': msg['timestamp']
        }
        for msg in messages
    ]
    
    return jsonify(messages_list)

@app.route('/api/messages', methods=['POST'])
def send_message():
    """Envoie un nouveau message"""
    data = request.get_json()
    
    # Validation des données
    if not data or 'username' not in data or 'content' not in data:
        return jsonify({'error': 'Données invalides'}), 400
    
    username = data['username'].strip()
    content = data['content'].strip()
    
    # Validation supplémentaire
    if not username or not content:
        return jsonify({'error': 'Nom d\'utilisateur et contenu requis'}), 400
    
    if len(username) > 20:
        return jsonify({'error': 'Nom d\'utilisateur trop long'}), 400
    
    if len(content) > 500:
        return jsonify({'error': 'Message trop long'}), 400
    
    # Créer le message
    timestamp = datetime.now().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO messages (username, content, timestamp) VALUES (?, ?, ?)',
        (username, content, timestamp)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'timestamp': timestamp}), 201

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Supprime un message (optionnel)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True}), 200

if __name__ == '__main__':
    # Initialiser la base de données au démarrage
    if not os.path.exists(DATABASE):
        init_db()
    
    # Démarrer le serveur
    app.run(debug=True, host='0.0.0.0', port=5000)