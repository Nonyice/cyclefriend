# 🌸 Cycle Tracker – Flask Menstrual Cycle App

A simple, secure, and educational **menstrual cycle tracking web application** built with **Flask** and **PostgreSQL**.  
Users can register, log in, and calculate estimated **fertile windows**, **ovulation peaks**, and **next period dates**.

> ⚠️ Disclaimer:  
> This application provides **general cycle estimates** for educational purposes only and **is not medical advice**.

---

## 🚀 Features

- User registration & login (secure authentication)
- Menstrual cycle calculation
- Fertile window estimation
- Ovulation peak highlighting
- Clean UI with header & footer
- PostgreSQL database
- Production-ready (Gunicorn + Railway)
- Environment-variable based configuration

---

## 🛠️ Tech Stack

- **Backend:** Flask
- **Auth:** Flask-Login
- **Database:** PostgreSQL
- **ORM:** Raw SQL (psycopg2)
- **Frontend:** HTML + CSS
- **Server:** Gunicorn
- **Hosting:** Railway

---

## 📁 Project Structure

cycle_tracker/
│
├── app.py
├── auth.py
├── models.sql
├── requirements.txt
├── Procfile
├── runtime.txt
│
├── templates/
│ ├── base.html
│ ├── register.html
│ ├── login.html
│ ├── dashboard.html
│
├── static/
│ └── style.css

👨‍💻 Author

PlimsolTech Group
Building reliable web solutions with Python & Flask.

📜 License

This project is licensed for educational and demonstration purposes.
