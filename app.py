from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Change this to a strong random key in a real application!

# Dummy user data for demonstration
USERS = {
    "admin": "password123",
    "user": "flaskpass"
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            flash(f'Login successful for {username}!', 'success')
            return redirect(url_for('home', username=username))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/home/<username>')
def home(username):
    return render_template('home.html', username=username)

@app.route('/logout')
def logout():
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # Flask's default port is 5000
