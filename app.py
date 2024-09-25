from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'  # Assurez-vous de définir une clé secrète

# Dictionnaire pour stocker les incidents
incidents = {}

# Dictionnaire des positions des salles
salles_positions = {
    "Amphi 1": (506, 88),
    "Amphi 2": (497, 154),
    "Accueil": (430, 107),
    "Peda": (382, 155),
    "Halle des salles des cours": (226, 175),
    "Salle 1": (221, 102),
    "Salle 2": (218, 246),
    "Salle 3": (149, 174),
}

# Met à jour le mot de passe pour correspondre à celui de la page HTML
users = {
    "admin": "admin123"  # Changer password123 par admin123
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('admin'))  # Redirige vers la page admin
        else:
            return "Nom d'utilisateur ou mot de passe incorrect"
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html', salles_positions=salles_positions)

@app.route('/signaler_incident', methods=['POST'])
def signaler_incident():
    data = request.json
    salle = data.get('salle')
    nom = data.get('nom')
    prenom = data.get('prenom')
    date_naissance = data.get('date_naissance')
    importance = data.get('importance')
    
    # Enregistrer l'incident avec l'heure actuelle
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    incidents[salle] = {
        "nom": nom,
        "prenom": prenom,
        "date_naissance": date_naissance,
        "importance": importance,
        "timestamp": timestamp
    }
    
    return jsonify({"message": "Incident signalé avec succès!", "importance": importance})

@app.route('/get_incidents')
def get_incidents():
    return jsonify(incidents)

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige vers la page de connexion si non authentifié
    return render_template('admin.html', incidents=incidents)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Déconnexion
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
