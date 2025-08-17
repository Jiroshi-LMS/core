# Jiroshi Scope Document

## Project Goal
Jiroshi is a headless Learning Management System (LMS) designed as a **polyglot monorepo project**.  
The primary goal is **deep learning of backend engineering concepts** (scalability, clean code, distributed systems, best practices) while also building a **functional full-stack application**.

---

## Key Objectives
1. Learn advanced backend design patterns and practices by building a real-world system.
2. Explore **polyglot backend development** using Django (Python), Node.js, and Go.
3. Implement **scalable architecture principles** with clear separation of concerns.
4. Gain experience with **monorepo to microservices migration**.
5. Practice with **infrastructure tooling** like Docker, Redis, Postgres, MinIO, Kubernetes.

---

## System Scope

### Core Features
#### Phase 1 (MVP – Monorepo)
- **User Authentication (Django)**  
  - User registration & login  
  - JWT-based authentication  
  - Roles: Admin, Instructor, Student  

- **Course Management (Node.js)**  
  - Create, read, update, delete courses  
  - Associate lessons, quizzes, and notes with courses  
  - Assign instructors to courses  

- **Media Handling (Go)**  
  - Upload & store course media (videos, PDFs, images) in MinIO  
  - Provide signed URLs for secure access  
  - Support video streaming  

- **Frontend (Next.js)**  
  - Basic dashboard for students & instructors  
  - Course browsing, enrollment, and viewing  
  - Auth integration with backend  

- **Infrastructure**  
  - Local development with Docker Compose  
  - Postgres for relational data  
  - Redis for caching & sessions  
  - MinIO (S3-compatible) for media storage  

---

#### Phase 2 (Scalability & Microservices)
- Split services into independent deployable units  
- gRPC between Node ↔ Go for streaming use cases  
- Add rate-limiting & API gateway (Kong/Traefik)  
- Implement background jobs (Celery/Redis Queue/Go workers)  
- Introduce logging & monitoring (ELK, Prometheus, Grafana)  

---

#### Phase 3 (Production Readiness)
- Kubernetes-based deployment  
- CI/CD pipeline (GitHub Actions/GitLab CI)  
- Observability (tracing, logging, metrics)  
- Role-based access with fine-grained permissions  
- Payment & subscription system (Stripe/Razorpay integration)  

---

## Out of Scope (For Now)
- Mobile applications  
- AI/ML-powered personalization or recommendations  
- Multi-tenant SaaS setup  
- Marketplace features (course sales, creator economy)  

These can be explored in **future iterations** after core system stability.

---

## Learning Goals
- **System Design:** Clean modular boundaries, service decomposition, scalability principles.  
- **Databases:** Postgres schema design, migrations, optimization, caching strategies.  
- **Polyglot Programming:** Understand trade-offs of Django, Node.js, and Go in real use.  
- **Service Communication:** REST, gRPC, and message queues.  
- **Infra & DevOps:** Docker, Kubernetes, CI/CD, monitoring & logging.  

---

## Deliverables
1. **Working Monorepo (Phase 1)** with Django, Node.js, Go, Postgres, Redis, MinIO.  
2. **Documentation** (Architecture.md, Scope.md, ADRs).  
3. **Frontend (Next.js)** integrated with backend APIs.  
4. Migration plan to **microservices architecture**.  
5. Deployment scripts (Docker Compose → Kubernetes).  

---

## Timeline (Rough)
- **Month 1:** Monorepo MVP (Auth + Courses + Media + Frontend + Infra basics).  
- **Month 2:** Refactor for scalability, introduce gRPC, caching, and queues.  
- **Month 3:** Production readiness — monitoring, CI/CD, Kubernetes.  

---

## Success Criteria
- The system runs locally with all services communicating.  
- Each service is **cleanly separated** with its own responsibilities.  
- The repo contains **documentation, infra setup, and clean code practices**.  
- Migration from monorepo → microservices is possible without rewriting everything.  

---

