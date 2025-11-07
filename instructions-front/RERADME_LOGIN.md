# 🔐 Angular Login Component — API Contract Documentation

**Purpose:**  
This document defines the communication contract between the Angular frontend and the Flask backend  
for the **Login** functionality in the application.

---

## 1. Overview

The Angular application handles user authentication via an HTTP `POST` request  
to the Flask backend at the endpoint `/login`.

This document describes what data the frontend sends,  
what it expects to receive, and how to properly configure the backend to support it.

---

## 2. Endpoint Specification

| Method | URL | Description |
|:-------|:----|:-------------|
| `POST` | `/login` | Authenticates a user and returns a token + user details. |

---

## 3. Request Format (Frontend → Backend)

### **Headers**
```http
Content-Type: application/json
Authorization: Bearer <token>
```

### Body
```
{
  "email": "string",       // Required — user's registered email
  "password": "string"     // Required — user's password
} 
```
### Example Request
```
{
  "email": "user@example.com",
  "password": "MySecret123!"
}
```

## 4. Response Format (Backend → Frontend)
✅ Success (200 OK)

```
{
  "message": "Login successful",
  "email": "user@example.com",
  "role": "user",                // or "admin"
  "token": "jwt-abcdef123456"    // Session or JWT token
}
```
❌ Failure (401 Unauthorized / 403 Forbidden / 400 Bad Request)

```
{
  "error": "Invalid credentials"
}
```
or
```
{
  "error": "Account inactive"
}
```