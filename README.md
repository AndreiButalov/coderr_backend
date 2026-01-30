# Coderr Backend API

Ein **Django + Django REST Framework** Backend für eine Plattform mit **User-Profilen (Customer / Business)**, **Angeboten (Offers)**, **Offer-Details**, **Bestellungen (Orders)** und **Bewertungen (Reviews)**.

Das Projekt unterstützt **Image-Uploads**, **rollenbasierte Profile** und eine saubere REST-API-Struktur.

---

## 🚀 Features

* Benutzerverwaltung (Django `User`)
* Erweiterte Profile (Customer / Business)
* Profilbilder & Offer-Bilder (`ImageField`)
* Angebote mit 3 Detail-Paketen (Basic / Standard / Premium)
* Bestellungen zwischen Customer & Business
* Bewertungen (Reviews)
* REST API mit Django REST Framework

---

## 🛠 Tech Stack

* Python 3.10+
* Django
* Django REST Framework
* SQLite (DEV)
* Pillow (für Image Uploads)


## 🧪 Testing (Postman / Frontend)

* Authentifizierte Requests erforderlich
* File Upload nur mit `multipart/form-data`

---

## 📌 ToDo / Erweiterungen

* JWT Authentication
* Permissions (Customer vs Business)
* Pagination & Filters
* API Documentation (Swagger / Redoc)

---

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
