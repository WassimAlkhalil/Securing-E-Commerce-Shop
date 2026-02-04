# Securing E-Commerce Shop

## 🛍️ Project Overview

A fully functional **Flask-based e-commerce platform** designed to demonstrate real-world security vulnerabilities and best practices in web application development. This project serves as an educational tool for learning about common security threats (CSRF, XSS, SQL Injection, IDOR) and how to properly secure web applications.

## 📋 Project Description

**Securing E-Commerce Shop** is a comprehensive e-commerce application that combines practical functionality with security assessments. The platform includes:

### Core Features
- **Product Management**: Browse, search, and manage product catalogs with filtering and categorization
- **User Accounts**: Registration, authentication, and profile management with secure password handling
- **Shopping Cart & Checkout**: Complete checkout flow with order management
- **Order Management**: Order history, tracking, and refund/return processes
- **Payment Processing**: Integration with PayPal and Alipay payment gateways
- **Dashboard**: Admin interface for managing products, orders, and users
- **Search Functionality**: Elasticsearch-powered product search capabilities
- **Plugin System**: Extensible architecture allowing custom plugin development

### Security Focus
The application includes intentional security demonstrations and assessments:
- **CSRF (Cross-Site Request Forgery)** vulnerability examples and mitigations
- **XSS (Cross-Site Scripting)** attack vectors and prevention techniques
- **SQL Injection** vulnerabilities and secure query practices
- **IDOR (Insecure Direct Object References)** demonstrations
- **Dockerfile Security** best practices
- **Dependency Analysis** and vulnerability scanning
- **Security Assessments** and recommendations

### Tech Stack
- **Backend**: Python 3.12, Flask, SQLAlchemy ORM, Flask-Babel (i18n)
- **Frontend**: JavaScript, Webpack, SCSS, Bootstrap
- **Database**: MySQL
- **Caching**: Redis
- **Search**: Elasticsearch
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Containerization**: Docker & Docker Compose
- **Security Tools**: Bandit, Dependency-Check

## 🚀 How to Run the Project

### Prerequisites
- Docker and Docker Compose
- OR Python 3.12+ and Pipenv locally
- MySQL database
- Redis server

### Option 1: Using Docker Compose

1. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - Web Application: `http://localhost:5000`
   - Dashboard: `http://localhost:5000/dashboard`

3. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Option 2: Local Development Setup

1. **Install dependencies**:
   ```bash
   pipenv install
   ```

2. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```

3. **Set up environment variables**:
   - Configure database URL, secret key, and API credentials

4. **Initialize the database**:
   ```bash
   flask db upgrade
   ```

5. **Load sample data** (optional):
   ```bash
   flask create-db
   ```

6. **Run the development server**:
   ```bash
   flask run
   ```
   The application will be available at `http://localhost:5000`

### Option 3: With Hot Reload

For development with auto-reloading:

```bash
./dev_reload.sh
```

## 📝 Additional Commands

- **Generate security reports**:
  ```bash
  bandit -r flaskshop/ -f html -o bandit_report.html
  ```

- **Database migrations**:
  ```bash
  flask db migrate -m "message"
  flask db upgrade
  ```
