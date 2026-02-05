from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
from werkzeug.utils import secure_filename
import secrets
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENCRYPTED_FOLDER'] = 'encrypted'
app.config['DECRYPTED_FOLDER'] = 'decrypted'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary folders
for folder in [app.config['UPLOAD_FOLDER'], app.config['ENCRYPTED_FOLDER'], app.config['DECRYPTED_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

def generate_key_from_password(password, salt):
    """
    Generate a Fernet key from a password using PBKDF2.
    This ensures each password creates a unique encryption key.
    """
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path, output_path, password):
    """
    Encrypt a file using password-based encryption.
    Returns the salt used (needed for decryption).
    """
    # Generate a random salt
    salt = os.urandom(16)
    
    # Generate key from password
    key = generate_key_from_password(password, salt)
    cipher = Fernet(key)
    
    # Read the file data
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Encrypt the data
    encrypted_data = cipher.encrypt(data)
    
    # Save salt + encrypted data
    # Format: [16 bytes salt][encrypted data]
    with open(output_path, 'wb') as f:
        f.write(salt + encrypted_data)
    
    return salt

def decrypt_file(file_path, output_path, password):
    """
    Decrypt a file using password-based encryption.
    Returns True if successful, False otherwise.
    """
    try:
        # Read the encrypted file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Extract salt and encrypted data
        salt = file_data[:16]
        encrypted_data = file_data[16:]
        
        # Generate key from password
        key = generate_key_from_password(password, salt)
        cipher = Fernet(key)
        
        # Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Save the decrypted data
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
    password = request.form.get('password', '').strip()
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not password:
        flash('Password is required for encryption', 'error')
        return redirect(url_for('index'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Encrypt the file
        encrypted_filename = f"encrypted_{filename}.enc"
        encrypted_path = os.path.join(app.config['ENCRYPTED_FOLDER'], encrypted_filename)
        
        try:
            encrypt_file(upload_path, encrypted_path, password)
            flash('File encrypted successfully! Keep your password safe - you\'ll need it to decrypt.', 'success')
            
            # Clean up uploaded file
            os.remove(upload_path)
            
            return send_file(encrypted_path, as_attachment=True, download_name=encrypted_filename)
        except Exception as e:
            flash(f'Encryption failed: {str(e)}', 'error')
            if os.path.exists(upload_path):
                os.remove(upload_path)
            return redirect(url_for('index'))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    password = request.form.get('password', '').strip()
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not password:
        flash('Password is required for decryption', 'error')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Determine output filename
        if filename.endswith('.enc'):
            original_filename = filename[:-4]
            if original_filename.startswith('encrypted_'):
                original_filename = original_filename[10:]
        else:
            original_filename = f"decrypted_{filename}"
        
        decrypted_path = os.path.join(app.config['DECRYPTED_FOLDER'], original_filename)
        
        try:
            success = decrypt_file(upload_path, decrypted_path, password)
            if success:
                flash('File decrypted successfully!', 'success')
                
                # Clean up uploaded file
                os.remove(upload_path)
                
                return send_file(decrypted_path, as_attachment=True, download_name=original_filename)
            else:
                flash('Decryption failed. Wrong password or corrupted file.', 'error')
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Decryption failed: {str(e)}', 'error')
            if os.path.exists(upload_path):
                os.remove(upload_path)
            return redirect(url_for('index'))

# Clean up old files on startup
@app.before_request
def cleanup_old_files():
    """Remove old temporary files"""
    import time
    current_time = time.time()
    
    for folder in [app.config['UPLOAD_FOLDER'], app.config['ENCRYPTED_FOLDER'], app.config['DECRYPTED_FOLDER']]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                # Delete files older than 1 hour
                if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > 3600:
                    try:
                        os.remove(file_path)
                    except:
                        pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
