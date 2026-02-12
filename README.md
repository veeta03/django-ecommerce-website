🛒 Full Stack Django E-Commerce Website

A fully functional E-Commerce web application built using Django, MySQL, Bootstrap, and Razorpay Payment Integration.

🚀 Features

User Registration & Login

Product Categories & Filtering

Product Detail Page

Add to Cart System

Cart Quantity Management

Checkout System

Razorpay Payment Integration

Payment Verification & Order Status

Order History Page

Admin Dashboard Management

Professional UI using Bootstrap

🛠 Tech Stack

Backend: Django (Python)

Database: MySQL

Frontend: HTML, CSS, Bootstrap

Payment Gateway: Razorpay

Version Control: Git & GitHub

📂 Project Structure
ecommerce_project/
│
├── ecommerce/        # Main project settings
├── store/            # App containing models, views, templates
├── templates/        # Base and shared templates
├── static/           # Static files (CSS, images)
├── media/            # Product images
├── manage.py
└── requirements.txt

⚙️ Installation Guide

Clone the repository:

git clone https://github.com/yourusername/django-ecommerce-website.git


Create virtual environment:

python -m venv venv


Activate environment:

Windows:

venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Configure Database in settings.py

Update MySQL credentials:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


Run migrations:

python manage.py makemigrations
python manage.py migrate


Create superuser:

python manage.py createsuperuser


Run server:

python manage.py runserver

💳 Payment Integration

This project uses Razorpay Test Mode.

To configure:

Add your Razorpay keys in settings.py:

RAZORPAY_KEY_ID = 'your_key_id'
RAZORPAY_KEY_SECRET = 'your_key_secret'

📌 Future Improvements

Product reviews & ratings

Wishlist feature

Discount coupons

Email order confirmation

Deployment on AWS / Render