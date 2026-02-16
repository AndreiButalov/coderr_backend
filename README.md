# Coderr Backend API

Ein **Django + Django REST Framework** Backend für eine Plattform mit **User-Profilen (Customer / Business)**, **Angeboten (Offers)**, **Offer-Details**, **Bestellungen (Orders)** und **Bewertungen (Reviews)**.

Das Projekt unterstützt **Image-Uploads**, **rollenbasierte Profile** und eine saubere REST-API-Struktur.

---


# Coderr Platform API

Dies ist die Backend-API für die **Coderr Plattform**, entwickelt mit **Django** und **Django REST Framework (DRF)**.  
Die Plattform ermöglicht:
- Benutzerregistrierung und Login (Kunden und Business User)
- Management von Profilen
- Verwaltung von Angeboten (Offers) und Angebotsdetails
- Bestellungen (Orders) zwischen Kunden und Business
- Bewertungen (Reviews) für Business User
- Basisstatistiken der Plattform


## 🚀 Features

- **Benutzerrollen**: `customer` oder `business` über Profile
- **Authentifizierung**: Token-basiert mit DRF `TokenAuthentication`
- **Profilverwaltung**: CRUD für eigene Profile
- **Offers & Details**: Angebote mit Basic/Standard/Premium Details
- **Orders**: Kunden können Bestellungen aus Offers erstellen
- **Reviews**: Kunden können Business User bewerten
- **Filterung & Pagination** für Offers und Reviews
- **Basisinformationen API** für Gesamtstatistiken

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
