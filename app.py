import secrets
from flaskext.mysql import MySQL
from flask import Flask, redirect, render_template, request, session, url_for
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'example'
app.config['MYSQL_DATABASE_DB'] = 'intradys'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3307

mysql = MySQL(app)


# Générez une clé secrète aléatoire de 24 octets (192 bits)
app.secret_key = secrets.token_hex(24)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form['username']
        password = request.form['password']

        # Connexion à la base de données
        conn = mysql.connect()
        cursor = conn.cursor()

        # Exécuter la requête SQL pour vérifier les informations d'identification
        cursor.execute(
            "SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user_data = cursor.fetchone()

        # Fermer les connexions à la base de données
        cursor.close()
        conn.close()

        # Vérifier si les informations d'identification sont valides
        if user_data:
            # Authentification réussie, rediriger vers la route du tableau de bord
            return redirect(url_for('dashboard'))
        else:
            # Authentification échouée, afficher un message d'erreur
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)

    # Si la méthode est GET, simplement afficher la page de connexion
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


def get_user_name_from_database(user_id):
    try:

        # Créez un curseur
        cursor = mysql.cursor()

        # Exécutez la requête SQL pour récupérer le nom de l'utilisateur par ID
        cursor.execute("SELECT username FROM user WHERE id = %s", (user_id,))
        user_name = cursor.fetchone()[0] if cursor.rowcount > 0 else None

        # Fermez le curseur
        cursor.close()

        return user_name

    except Exception as e:
        # Gérez les erreurs, par exemple, en journalisant l'erreur
        app.logger.error(f"Error fetching user name: {str(e)}")
        return None


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/labelling')
def labelling():
    return render_template('labelling.html')


@app.route('/logs')
def logs():
    try:
        # Récupérer le numéro de page depuis les paramètres de requête, ou utilisez la page 1 par défaut
        page = request.args.get('page', default=1, type=int)

        # Nombre d'éléments à afficher par page
        items_par_page = 10

        # Création d'une connexion à la base de données
        conn = mysql.connect()
        cursor = conn.cursor()

        # Compter le nombre total d'enregistrements dans la table "labeling"
        cursor.execute("SELECT COUNT(*) FROM labeling")
        total_entries = cursor.fetchone()[0]

        # Calculer le nombre total de pages nécessaires pour afficher tous les enregistrements
        total_pages = (total_entries + items_par_page - 1) // items_par_page

        # Calculer l'offset pour récupérer les enregistrements de la page actuelle
        offset = (page - 1) * items_par_page

        # Exécution de la requête SQL pour récupérer les enregistrements paginés
        cursor.execute("SELECT * FROM labeling LIMIT %s, %s",
                       (offset, items_par_page))

        # Initialisation de la liste pour stocker les résultats
        labeling_data = []

        # Parcours des résultats de la requête et création des dictionnaires
        for enregistrement in cursor:
            entry = {
                'id': enregistrement[0],
                'image_name': enregistrement[1],
                'action': enregistrement[2],
                'date': enregistrement[3],
                'user_id': enregistrement[4]
            }
            labeling_data.append(entry)

        # Fermeture des connexions
        cursor.close()
        conn.close()

        # Rendre le modèle avec les données récupérées
        return render_template('logs.html', labeling_data=labeling_data, total_pages=total_pages, current_page=page)

    except Exception as e:
        return str(e)


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/logout')
def logout():
    # Effacez les données de session pour déconnecter l'utilisateur
    session.clear()
    # Redirigez l'utilisateur vers la page de connexion
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
