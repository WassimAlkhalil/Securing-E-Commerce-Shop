# Secure Shop Project – README

##  Project Setup Guide

Follow the steps below to set up and run the Secure Shop application using Docker.

---

##  Requirements

* Docker
* Docker Compose
* Git

---

##  Installation & Setup

### 1. Clone the Repository

```bash
git clone https://collaborating.tuhh.de/e22/teaching-courses/lectures/master/wise25_26_secure_software_application_project/group_3.git
cd softsec-shop
```

### 2. Start Docker Containers

```bash
docker compose up --build
```

Wait **1 minute** for services to initialize.

### 3. Initialize Database

Enter the web container:

```bash
docker compose exec web sh
```

Run initialization commands:

```bash
flask createdb
flask seed
```

Exit the container:

```bash
exit
```

### 4. Open the Webshop

Navigate to:

```
https://localhost
```

Login with admin credentials:

```
username: admin
password: admin
```

---

##  PayPal & Stripe Credentials

>  **Do NOT use real credentials in development. Use sandbox/test keys only.**

###  PayPal Sandbox Credentials (Example Template)

```
PAYPAL_CLIENT_ID = "AV3v_6oPD6yU2M1STFjXksGYyd99lkO9EicnS8Rwlrscw6twgM4lwnqZGpHoIoUfHrQQWpwunaxdolNV"
PAYPAL_CLIENT_SECRET = "EK2Ew3Zs7lVb1Y0DGOWWqWDKkaHPeZN5JmpLIfFZMgYf5J4bLzL2-c2Iwyi7x5LEtgXqFr5WYJZAGRXG"
PAYPAL_MODE="sandbox"
```

### Business PayPal Account (Sandbox)[Receive money]

```
Email: sb-eygbd47509610@business.example.com
Password: cBCt#7{n
```

### Personal PayPal Account (Sandbox)[Send money]

```
Email: sb-543rb547589594@personal.example.com
Password: kI2%.DUt
```


## Testing Payments

###  PayPal

* Add products to cart
* Proceed to checkout
* Select **PayPal** as payment method
* Pay using sandbox personal account

### Expected Behavior

* Payment should redirect to PayPal
* After approval, return to `/orders/payment_success`
* Order status updates to **fulfilled**

---


##  Troubleshooting

###  Alembic "No changes detected"

This means your models and DB schema match. Ensure you:

1. Added new columns in models
2. Ran `flask db migrate`
3. Ran `flask db upgrade`

###  MySQL Duplicate Entries

If seeds already ran:

```bash
flask resetdb
flask seed
```


---

##  License

This project is for academic purposes under TUHH Secure Software Application Project 2025.
*Created by Swarup Bharat Phatangare*
