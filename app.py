from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète'  # Assurez-vous de définir une clé secrète

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle de données pour les incidents
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salle = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.String(10), nullable=False)  # Vous pouvez changer ça en Date
    importance = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='non résolu')

# Créer la base de données et les tables
with app.app_context():
    db.create_all()

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

# Utilisateurs pour l'authentification
users = {
    "admin": "admin123"
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
    new_incident = Incident(
        salle=salle,
        nom=nom,
        prenom=prenom,
        date_naissance=date_naissance,
        importance=importance,
        timestamp=timestamp
    )

    db.session.add(new_incident)  # Ajouter l'incident à la session
    db.session.commit()  # Enregistrer les modifications

    return jsonify({"message": "Incident signalé avec succès!", "importance": importance})

@app.route('/get_incidents')
def get_incidents():
    # Récupérer tous les incidents de la base de données
    incidents = Incident.query.all()
    incidents_trie = [
        {
            "salle": incident.salle,
            "nom": incident.nom,
            "prenom": incident.prenom,
            "date_naissance": incident.date_naissance,
            "importance": incident.importance,
            "timestamp": incident.timestamp,
            "status": incident.status
        } for incident in incidents
    ]
    return jsonify(incidents_trie)

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige vers la page de connexion si non authentifié
    incidents = Incident.query.all()  # Récupérer tous les incidents de la base de données
    return render_template('admin.html', incidents=incidents)


@app.route('/resoudre_incident', methods=['POST'])
def resoudre_incident():
    salle = request.json.get('salle')
    incident = Incident.query.filter_by(salle=salle).first()
    if incident:
        incident.status = 'en cours de résolution'
        db.session.commit()  # Enregistrer les modifications
        return jsonify({"message": f"L'admin arrive pour résoudre l'incident à {salle}"})
    return jsonify({"error": "Incident non trouvé."}), 404

@app.route('/supprimer_incident', methods=['POST'])
def supprimer_incident():
    salle = request.json.get('salle')
    incident = Incident.query.filter_by(salle=salle).first()
    if incident:
        db.session.delete(incident)  # Supprimer l'incident
        db.session.commit()  # Enregistrer les modifications
        return jsonify({"message": f"Incident à {salle} supprimé avec succès."})
    return jsonify({"error": "Incident non trouvé."}), 404

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('username', None)  # Déconnexion
        return redirect(url_for('index'))  # Redirige vers la page d'accueil
    return redirect(url_for('index'))  # Redirige par défaut

if __name__ == '__main__':
    app.run(debug=True)
