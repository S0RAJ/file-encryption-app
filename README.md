# File Encryption & Decryption Web App 🔐

A user-friendly web application for encrypting and decrypting files using military-grade encryption (Fernet/AES-128).

## Features ✨

- **Simple Interface**: Drag-and-drop file upload
- **Secure Encryption**: Uses Fernet (AES-128 in CBC mode)
- **Automatic Key Management**: Keys are generated and stored securely
- **Privacy-Focused**: Files are deleted after processing
- **No Technical Knowledge Required**: Anyone can use it!

## Local Setup 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download this project**
   ```bash
   cd file-encryption-app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## Deployment Options 🌐

### Option 1: Render (Recommended - Free & Easy)

1. **Create a Render account**: Go to [render.com](https://render.com) and sign up

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or upload files)
   - Settings:
     - **Name**: file-encryptor (or your choice)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

3. **Deploy**: Click "Create Web Service"

4. **Access**: Your app will be live at `https://your-app-name.onrender.com`

**Note**: The free tier sleeps after inactivity, so the first request may take 30-60 seconds.

---

### Option 2: PythonAnywhere (Free Tier Available)

1. **Sign up**: Go to [pythonanywhere.com](https://www.pythonanywhere.com) and create a free account

2. **Upload your files**:
   - Go to "Files" tab
   - Upload all project files

3. **Install dependencies**:
   - Go to "Consoles" tab → Start a Bash console
   ```bash
   pip3 install --user -r requirements.txt
   ```

4. **Configure Web App**:
   - Go to "Web" tab → "Add a new web app"
   - Choose "Flask" and Python 3.x
   - Set source code directory to your project folder
   - Set working directory to your project folder

5. **Reload**: Click "Reload" and your app is live!

---

### Option 3: Railway (Easy & Fast)

1. **Sign up**: Go to [railway.app](https://railway.app)

2. **Deploy**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Railway will auto-detect Flask and deploy
   - Or use: "Deploy from Template" if you upload to GitHub

3. **Access**: Your app will be live at a Railway domain

---

### Option 4: Heroku (Classic Option)

1. **Install Heroku CLI**: Download from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create a Procfile** (already included in advanced setup):
   ```
   web: gunicorn app:app
   ```

3. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

---

## How It Works 🔧

1. **Encryption**: 
   - Upload any file
   - File is encrypted using Fernet (AES-128 CBC mode)
   - Download the encrypted `.enc` file

2. **Decryption**:
   - Upload the encrypted `.enc` file
   - File is decrypted using the stored key
   - Download your original file

## Security Notes 🔒

- The encryption key is stored in `secret.key` on the server
- All users of the same deployment share the same key
- For production use, consider implementing user-specific keys
- Files are automatically deleted after processing
- Maximum file size: 16MB

## File Structure 📁

```
file-encryption-app/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
├── uploads/             # Temporary upload folder (auto-created)
├── encrypted/           # Temporary encrypted files (auto-created)
├── decrypted/           # Temporary decrypted files (auto-created)
└── secret.key          # Encryption key (auto-generated)
```

## Customization 💡

### Change Maximum File Size
Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### Change Color Scheme
Edit `templates/index.html` CSS section to customize colors

### Add User Authentication
Consider adding Flask-Login for user-specific encryption keys

## Troubleshooting 🔍

**Issue**: "Module not found" error
- **Solution**: Make sure you've activated your virtual environment and installed requirements

**Issue**: Files not uploading
- **Solution**: Check file size limit (default 16MB)

**Issue**: Decryption fails
- **Solution**: Ensure you're using the same key that was used for encryption

## Contributing 🤝

Feel free to fork this project and add your own features!

## License 📄

This project is open source and available under the MIT License.

## Support 💬

If you encounter any issues, please create an issue on GitHub or contact the developer.

---

**Happy Encrypting! 🎉**
