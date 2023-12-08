from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/labelling')
def labelling():
    return render_template('labelling.html')


@app.route('/logs')
def logs():
    return render_template('logs.html')


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/logout')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)
