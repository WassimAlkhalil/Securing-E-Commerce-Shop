# Securing E-Commerce Shop

A Flask-based e-commerce application with integrated security assessments and vulnerability demonstrations for educational purposes. This project is designed to help developers and security professionals understand common web application vulnerabilities in a hands-on, practical environment.

[![Flask](https://img.shields.io/badge/Flask-2.x-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Security Vulnerabilities Demonstrated](#security-vulnerabilities-demonstrated)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Standard Setup](#standard-setup)
  - [Docker Setup](#docker-setup)
- [Usage](#usage)
- [Security Tasks](#security-tasks)
- [Project Structure](#project-structure)
- [Educational Objectives](#educational-objectives)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

## 🎯 Overview

This project implements a basic e-commerce platform with intentional security vulnerabilities for educational purposes. It demonstrates real-world security issues that developers should be aware of and know how to prevent.

**⚠️ WARNING:** This application contains intentional security vulnerabilities. DO NOT deploy this application in a production environment or expose it to the internet.

## ✨ Features

- **Product Catalog**: Browse and search products
- **Shopping Cart**: Add/remove items from cart
- **User Authentication**: Login and registration system
- **Order Management**: Place and track orders
- **Admin Panel**: Manage products and view orders
- **User Profiles**: View and edit user information

## 🔓 Security Vulnerabilities Demonstrated

This application intentionally includes the following security vulnerabilities for educational purposes:

### 1. **Cross-Site Request Forgery (CSRF)**
- **Location**: Forms throughout the application
- **Description**: Missing or improperly implemented CSRF tokens allow attackers to perform unauthorized actions on behalf of authenticated users
- **Learning Goal**: Understand how CSRF attacks work and how to implement proper token-based protection

### 2. **Cross-Site Scripting (XSS)**
- **Location**: User input fields (product reviews, comments, profile information)
- **Description**: Unescaped user input is rendered in HTML, allowing injection of malicious scripts
- **Types Demonstrated**:
  - Stored XSS: Malicious scripts stored in database
  - Reflected XSS: Scripts reflected in immediate response
- **Learning Goal**: Learn input validation, output encoding, and Content Security Policy (CSP)

### 3. **SQL Injection (SQLi)**
- **Location**: Search functionality, login forms, product queries
- **Description**: User input is directly concatenated into SQL queries without proper sanitization
- **Learning Goal**: Understand parameterized queries and ORM usage to prevent SQL injection

### 4. **Insecure Direct Object References (IDOR)**
- **Location**: Order viewing, profile access, product management
- **Description**: Lack of proper authorization checks allows users to access resources by manipulating IDs
- **Learning Goal**: Implement proper authorization and access control mechanisms

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package installer (usually included with Python)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Docker** (optional): [Download Docker](https://www.docker.com/get-started)
- **Docker Compose** (optional): Usually included with Docker Desktop

## 🚀 Installation

### Standard Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/WassimAlkhalil/Securing-E-Commerce-Shop.git
   cd Securing-E-Commerce-Shop
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file
   cp .env.example .env
   
   # Edit .env and configure:
   # - SECRET_KEY: Random secret key for Flask
   # - DATABASE_URL: Database connection string
   # - FLASK_ENV: development
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Seed the database (optional)**
   ```bash
   python seed.py
   ```

7. **Run the application**
   ```bash
   flask run
   # Or
   python app.py
   ```

8. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

### Docker Setup

Using Docker simplifies the setup process and ensures consistency across different environments.

1. **Clone the repository**
   ```bash
   git clone https://github.com/WassimAlkhalil/Securing-E-Commerce-Shop.git
   cd Securing-E-Commerce-Shop
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

4. **Stop the application**
   ```bash
   docker-compose down
   ```

#### Docker Configuration

**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
```

**docker-compose.yml Example (SQLite - Simpler Setup):**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=sqlite:///ecommerce.db
    volumes:
      - .:/app
      - sqlite_data:/app/instance
    
volumes:
  sqlite_data:
```

**docker-compose.yml Example (PostgreSQL - Production-like Setup):**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://ecommerce:ecommerce@db:5432/ecommerce_db
    volumes:
      - .:/app
    depends_on:
      - db
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=ecommerce
      - POSTGRES_PASSWORD=ecommerce
      - POSTGRES_DB=ecommerce_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 💻 Usage

### Regular User Flow

1. **Register a new account** at `/register`
2. **Login** with your credentials at `/login`
3. **Browse products** on the homepage
4. **Add items to cart** and proceed to checkout
5. **View your orders** in the user dashboard
6. **Update your profile** in account settings

### Admin User Flow

1. **Login with admin credentials**
   - ⚠️ **CRITICAL SECURITY WARNING**: Default credentials (admin/admin) are for initial setup ONLY
   - IMMEDIATELY change these credentials after first login
   - NEVER use default credentials in any real scenario
2. **Access admin panel** at `/admin`
3. **Manage products**: Add, edit, or delete products
4. **View all orders**: Monitor customer orders
5. **Manage users**: View user accounts

## 🎓 Security Tasks

This application is designed for educational security testing. Below are suggested tasks to explore each vulnerability:

### Task 1: Exploit CSRF Vulnerability
**Objective**: Execute unauthorized actions on behalf of an authenticated user

**Steps**:
1. Login as a regular user
2. Create a malicious HTML page with a form that submits to the change password endpoint
3. Trick the authenticated user into visiting your malicious page
4. Observe the password change without the user's consent

**Mitigation**: Implement Flask-WTF CSRF protection

### Task 2: Exploit XSS Vulnerability
**Objective**: Inject malicious JavaScript into the application

**Steps**:
1. Find an input field (e.g., product review, comment section)
2. Submit a payload like: `<script>alert('XSS')</script>`
3. Observe the script execution when the page is rendered
4. Try more advanced payloads to steal cookies or redirect users

**Mitigation**: Use proper output encoding and Content Security Policy

### Task 3: Exploit SQL Injection
**Objective**: Extract sensitive data from the database

**Steps**:
1. Navigate to the search functionality
2. Try payloads like: `' OR '1'='1` or `'; DROP TABLE users; --`
3. Observe database errors or unauthorized data access
4. Use SQLMap or manual techniques to extract data

**Mitigation**: Use parameterized queries or ORM methods

### Task 4: Exploit IDOR Vulnerability
**Objective**: Access resources belonging to other users

**Steps**:
1. Login as User A and note your order ID (e.g., `/orders/5`)
2. Manually change the URL to another ID (e.g., `/orders/6`)
3. Observe if you can access another user's order details
4. Try the same with profile pages and other resources

**Mitigation**: Implement proper authorization checks

## 📁 Project Structure

```
Securing-E-Commerce-Shop/
│
├── app.py                  # Main application file
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore rules
│
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   └── order.py
│
├── routes/               # Application routes
│   ├── __init__.py
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   └── admin.py
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── products.html
│   ├── cart.html
│   └── admin/
│
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── migrations/           # Database migrations
│
└── tests/               # Test files
    ├── test_auth.py
    ├── test_products.py
    └── test_security.py
```

## 🎯 Educational Objectives

By working with this application, you will learn:

1. **How to identify** common web application vulnerabilities
2. **How to exploit** these vulnerabilities in a safe, controlled environment
3. **How to remediate** security issues using industry best practices
4. **Security testing methodologies** including:
   - Manual testing techniques
   - Using security tools (Burp Suite, OWASP ZAP, SQLMap)
   - Code review for security issues
5. **Secure coding practices** for Flask applications:
   - Input validation and sanitization
   - Output encoding
   - Parameterized queries
   - Session management
   - Access control

## 🤝 Contributing

Contributions are welcome! If you'd like to add new vulnerabilities, improve documentation, or fix issues:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-vulnerability`)
3. Commit your changes (`git commit -m 'Add new vulnerability demo'`)
4. Push to the branch (`git push origin feature/new-vulnerability`)
5. Open a Pull Request

**Guidelines**:
- Ensure any new vulnerabilities are well-documented
- Include educational context for each vulnerability
- Add mitigation steps in comments or separate documentation
- Follow the existing code style

## ⚠️ Disclaimer

**IMPORTANT: Educational Use Only**

This application is created solely for educational and training purposes. It contains intentional security vulnerabilities and should NEVER be used in a production environment or deployed on any public-facing server.

The developers and contributors are NOT responsible for any misuse of this code. By using this application, you agree to:

- Use it only in isolated, controlled environments
- Not use it for malicious purposes
- Not deploy it on production systems
- Take responsibility for securing your test environment
- Comply with all applicable laws and regulations

This project is designed to help developers and security professionals learn about web security vulnerabilities. Always obtain proper authorization before testing security on any system.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.0.x/security/)
- [Web Security Academy](https://portswigger.net/web-security)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/)

## 📞 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Remember**: Security is not a feature, it's a requirement. Learn from these vulnerabilities and build secure applications!
