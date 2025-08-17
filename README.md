# 🐉 Jiroshi – Polyglot Headless LMS

Jiroshi is a **headless Learning Management System (LMS)** designed as a **polyglot monorepo** project.  
It combines the strengths of **Django (Python)**, **Node.js**, and **Go** to handle different parts of the system while following **scalable backend architecture principles**.

This project is primarily for **learning advanced backend development**, but is also being built as a **real functional full-stack LMS**.

---

## 🚀 Features (Phase 1 – MVP)
- 🔑 **Authentication (Django)** – User registration, login, JWT auth  
- 📚 **Course Management (Node.js)** – CRUD for courses, lessons, notes, quizzes  
- 🎥 **Media Service (Go)** – Video/PDF upload & streaming (via MinIO)  
- 💻 **Frontend (Next.js)** – Dashboard for students & instructors  
- 🗄️ **Infrastructure** – Postgres (DB), Redis (cache), MinIO (storage)  

---

## 🏗️ Architecture (Polyglot Monorepo)
- **Django (Python)** → Auth, roles, permissions  
- **Node.js (Express/Fastify)** → Course & content management  
- **Go** → Media streaming & file storage  
- **Next.js** → Frontend UI  
- **Postgres** → Relational data storage  
- **Redis** → Caching & background jobs  
- **MinIO (S3)** → File and media storage  

> In future phases: services will evolve into **microservices** connected via **gRPC** and API Gateway.

---

## ⚙️ Tech Stack
- **Backend**: Django (Python), Node.js, Go  
- **Frontend**: Next.js (React + Tailwind)  
- **Database**: PostgreSQL  
- **Cache/Queue**: Redis  
- **Object Storage**: MinIO (S3-compatible)  
- **DevOps**: Docker, Kubernetes (future), GitHub Actions (CI/CD)  

---

