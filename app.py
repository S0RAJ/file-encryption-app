from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
from cryptography.fernet import Fernet
import os
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENCRYPTED_FOLDER'] = 'encrypted'
app.config['DECRYPTED_FOLDER'] = 'decrypted'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary folders
for folder in [app.config['UPLOAD_FOLDER'], app.config['ENCRYPTED_FOLDER'], app.config['DECRYPTED_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

def generate_key():
    """Generate a new Fernet key"""
    return Fernet.generate_key()

def load_or_create_key():
    """Load existing key or create a new one"""
    key_file = 'secret.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_file(file_path, output_path, key):
    """Encrypt a file"""
    cipher = Fernet(key)
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)

def decrypt_file(file_path, output_path, key):
    """Decrypt a file"""
    cipher = Fernet(key)
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Encrypt the file
        key = load_or_create_key()
        encrypted_filename = f"encrypted_{filename}.enc"
        encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
        
        try:
            encrypt_file(upload_path, encrypted_path, key)
            flash('File encrypted successfully!', 'success')
            
            # Clean up uploaded file
            os.remove(upload_path)
            
            return send_file(encrypted_path, as_attachment=True, download_name=encrypted_filename)
        except Exception as e:
            flash(f'Encryption failed: {str(e)}', 'error')
            return redirect(url_for('index'))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Decrypt the file
        key = load_or_create_key()
        
        # Remove .enc extension if present
        if filename.endswith('.enc'):
            original_filename = filename[:-4]
            if original_filename.startswith('encrypted_'):
                original_filename = original_filename[10:]  # Remove 'encrypted_' prefix
        else:
            original_filename = f"decrypted_{filename}"
        
        decrypted_path = os.path.join(app.config['DECRYPTED_FOLDER'], original_filename)
        
        try:
            success = decrypt_file(upload_path, decrypted_path, key)
            if success:
                flash('File decrypted successfully!', 'success')
                
                # Clean up uploaded file
                os.remove(upload_path)
                
                return send_file(decrypted_path, as_attachment=True, download_name=original_filename)
            else:
                flash('Decryption failed. Make sure you\'re using the correct key and encrypted file.', 'error')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Decryption failed: {str(e)}', 'error')
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
