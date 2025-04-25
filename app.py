from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Mock database
users_db = {}
verification_codes = {}
password_reset_codes = {}

# Email configuration (example using Flask-Mail)
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
mail = Mail(app)

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in users_db:
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        # Generate verification code
        verification_code = generate_verification_code()
        verification_codes[email] = verification_code
        
        # Send verification email
        msg = Message('Verify Your Email', sender='noreply@example.com', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        mail.send(msg)
        
        # Store user data temporarily (password should be hashed in production)
        users_db[email] = {
            'password': password,
            'verified': False
        }
        
        flash('Verification code sent to your email', 'success')
        return redirect(url_for('verify_email', email=email))
    
    return render_template('signup.html'))

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    
    if request.method == 'POST':
        code = request.form['code']
        
        if email in verification_codes and verification_codes[email] == code:
            users_db[email]['verified'] = True
            del verification_codes[email]
            flash('Email verified successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code', 'error')
    
    return render_template('verify_email.html', email=email))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email not in users_db:
            flash('Invalid email or password', 'error')
        elif not users_db[email]['verified']:
            flash('Please verify your email first', 'error')
        elif users_db[email]['password'] != password:
            flash('Invalid email or password', 'error')
        else:
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('login.html'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        if email in users_db:
            # Generate reset code
            reset_code = generate_verification_code()
            password_reset_codes[email] = reset_code
            
            # Send reset email
            msg = Message('Password Reset Code', sender='noreply@example.com', recipients=[email])
            msg.body = f'Your password reset code is: {reset_code}'
            mail.send(msg)
            
            flash('Reset code sent to your email', 'success')
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Email not found', 'error')
    
    return render_template('forgot_password.html'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
        elif email in password_reset_codes and password_reset_codes[email] == code:
            users_db[email]['password'] = new_password
            del password_reset_codes[email]
            flash('Password reset successfully! You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid reset code', 'error')
    
    return render_template('reset_password.html', email=email))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', email=session['user']))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
