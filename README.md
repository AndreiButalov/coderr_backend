# Coderr Backend API

A Django + Django REST Framework backend for a platform with User Profiles (Customer / Business), Offers, Offer Details, Orders, and Reviews.

The project supports image uploads, role-based profiles, and a clean REST API structure.

---


# Coderr Platform API

- This is the backend API for the Coderr Platform, built with Django and Django REST Framework (DRF).

- The platform provides:

- User registration and login (Customer & Business users)

- Profile management

- Offer management (Offers and Offer Details)

- Orders between Customers and Business users

- Reviews for Business users

- Basic platform statistics


# 🚀 Features

- User Roles: customer or business via profile model

- Authentication: Token-based authentication using DRF TokenAuthentication

- Profile Management: CRUD operations for own profile

- Offers & Details: Offers with Basic / Standard / Premium options

- Orders: Customers can create orders from offers

- Reviews: Customers can review Business users

- Filtering & Pagination for Offers and Reviews

- Basic Info API for overall platform statistics

---

## 🛠 Tech Stack

* Python 3.10+
* Django
* Django REST Framework
* SQLite (DEV)
* Pillow (for image uploads)


## 🧪 Testing (Postman / Frontend)

- Authenticated requests are required for protected endpoints

- File uploads must use multipart/form-data

---

## 📌 ToDo / Future Improvements

* JWT Authentication
* Permissions (Customer vs Business)
* Pagination & Filters
* API Documentation (Swagger / Redoc)

---

## ⚙️ Setup-Anleitung

1. **Projekt klonen**
  ```bash

  # Frontend
  https://andrei-butalov.de/coderr/index.html


  # Backend
  git clone https://github.com/AndreiButalov/coderr_backend.git  

# 🖥 Setup on Windows
  python -m venv env
  "env/Scripts/activate"
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver


# 🍎 Setup on macOS

  python3 -m venv env
  source env/bin/activate
  pip3 install -r requirements.txt
  python3 manage.py makemigrations
  python3 manage.py migrate
  python3 manage.py runserver
  http://127.0.0.1:8000/