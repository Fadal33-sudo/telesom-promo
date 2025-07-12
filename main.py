
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'somali_website_2024_secret_key'

# File-ga users-ka ku kaydin doonno
USERS_FILE = 'users.json'

# Load users ama samee file cusub
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save users
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Password encryption
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check haddii user uu admin yahay
def is_admin():
    return session.get('role') == 'admin'

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username in users and users[username]['password'] == hash_password(password):
            session['username'] = username
            session['role'] = users[username]['role']
            session['logged_in'] = True
            flash('Si guul leh ayaad u soo gashay!', 'success')
            
            if users[username]['role'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Username ama password qaldan!', 'error')
    
    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords-ku ma isku mid aha!', 'error')
            return render_template('register.html')
        
        users = load_users()
        
        if username in users:
            flash('Username-kan horay loo isticmaalay!', 'error')
            return render_template('register.html')
        
        # Kan kowaad wuxuu noqon doonaa admin
        role = 'admin' if len(users) == 0 else 'user'
        
        users[username] = {
            'password': hash_password(password),
            'email': email,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        save_users(users)
        flash('Si guul leh ayaad u diiwaangashay!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Dashboard - user dalka gudihiisa
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash('Fadlan soo gal si aad u arkto boggan!', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

# Admin panel
@app.route('/admin')
def admin():
    if not session.get('logged_in') or not is_admin():
        flash('Ma leh fasax inaad arkto boggan!', 'error')
        return redirect(url_for('login'))
    
    users = load_users()
    return render_template('admin.html', users=users)

# Delete user (admin kaliya)
@app.route('/admin/delete_user/<username>')
def delete_user(username):
    if not session.get('logged_in') or not is_admin():
        flash('Ma leh fasax!', 'error')
        return redirect(url_for('login'))
    
    users = load_users()
    if username in users and username != session.get('username'):
        del users[username]
        save_users(users)
        flash(f'User {username} waa la tirtiray!', 'success')
    
    return redirect(url_for('admin'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Si guul leh ayaad uga baxday!', 'info')
    return redirect(url_for('home'))

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
