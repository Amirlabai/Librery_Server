# 🧾 Angular Register Component — API Contract Documentation

**Purpose:**  
Defines the communication contract between the **Angular frontend** and the **Flask backend**  
for the **User Registration** (`/register`) functionality.

---

## 1. Overview

The Angular application allows new users to register by sending an HTTP `POST` request  
to the Flask backend endpoint `/register`.

This document details:
- What the frontend sends  
- What the backend must return  
- Required validation rules and expected behavior

---

## 2. Endpoint Specification

| Method | URL | Description |
|:-------|:----|:-------------|
| `POST` | `/register` | Creates a new user account and returns confirmation or error message. |

---

## 3. Request Format (Frontend → Backend)

### **Headers**
```http
Content-Type: application/json
```

### Body
```
{
  "email": "string",       // Required — user's email (must be unique)
  "password": "string"     // Required — must meet password policy
}
```
### Example Request
```
{
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}
```

## 4. Response Format (Backend → Frontend)
✅ Success (200 OK)

```
{
  "message": "User created successfully",
  "email": "newuser@example.com"
}
```
❌ Failure (401 Unauthorized / 403 Forbidden / 400 Bad Request)

```
{
  "error": "Email already registered"
}
```
or
```
{
  "error": "Invalid input data"
}
```
