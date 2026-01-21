## ⚙️ Setup-Anleitung

1. **Projekt klonen**
  ```bash
  git clone https://github.com/AndreiButalov/coderr_backend.git
  python -m venv env
  "env/Scripts/activate"
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver
