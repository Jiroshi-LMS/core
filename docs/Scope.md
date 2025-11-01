# Jiroshi — MVP Scope Document  
**Date:** 2025-11-01  
**Target MVP Release:** 2026-01-01  
**Stage:** Alpha / Private Preview

---

## 🎯 Project Goal
**Jiroshi** is a **Headless Learning Management System (LMS)** — a Platform-as-a-Service (PaaS) that enables instructors and institutions to launch their own branded LMS without managing backend infrastructure.  

**MVP objective:** deliver a minimal, secure, and extensible platform that lets instructors manage courses & lessons via a dashboard and exposes headless APIs for frontends to consume.

---

## 🧩 System Scope (Alpha Phase)

### 1. Instructor Dashboard (Backend: Django / Frontend: Next.js)
The dashboard is the control center for instructors to manage their LMS.

#### 🔐 Authentication & Authorization
- Instructor registration & login (JWT-based).
- Basic password reset & profile update.

#### 📚 Course & Lesson Management
- CRUD for Courses and Lessons.
- Associate resources (video links, PDFs, PPTs, GIFs, external URLs) with lessons.
- Course visibility flags: `Public`, `Private`, `Paid` *(Paid as a placeholder for Phase 1)*.
- Soft-delete with delayed purge (15–30 days).
- (Optional stretch) Course duplication / cloning.

#### 🗂️ Media & File Handling
- File uploads to S3-compatible storage (metadata tracked in DB).
- Secure access via signed URLs.
- Track S3 object keys and statuses in a metadata table.
- Simple file listing UI in the dashboard (read-only in alpha).
- Ensure deletion workflow revokes signed URLs and marks files for purge.

#### 🔑 API Key Management
- Generate and revoke **Public (GET)** and **Private (WRITE)** API keys for each instructor account.
- Keys scoped to instructor and purpose (read-only vs write).
- Basic usage tracking (placeholder).

#### 📈 Student & Enrollment Tracking
- Store minimal enrolled-user records (UUID, email, course_id).
- Basic enrollment list and counts for the dashboard.

---

### 2. Headless APIs (Backend: Node.js + TypeScript)
Public API layer for instructor frontends (web / mobile).

#### 🧾 Authentication APIs (for instructor's users)
- JWT-based signup & login for learners.
- User profile fetch & update.

#### 🎓 Course & Lesson APIs
- Video/Document (PPTX/PDF/...) based Course & Lesson Creation Flow
- List published courses (read-only public endpoint).
- Fetch course details and lesson lists.
- Fetch lesson resources (authenticated where required).
- Enrollment endpoint (protected — requires appropriate token).
- Ensure APIs check ownership and enforce basic RLS/selector filters.

**Security notes:**  
- Private endpoints require instructor Private API key or authenticated context.  
- Public endpoints limited to safe read-only data.

---

### 3. Demo Frontend (Next.js)
Lightweight demo to showcase the headless integration.

#### Key Pages
- Home — list of courses.
- Course details — description + enroll button.
- Lessons list.
- Lesson viewer — handles doc (PDF/PPT/GIF) and video link rendering.

---

## 🧱 Post-Alpha Roadmap

- **Payments:** Razorpay integration for paid courses.
- **Advanced Permissions:** Fine-grained ACL and team roles.
- **Quizzes & Labs:** Interactive assessments, auto-grading (Phase 2).
- **SDK's for multiple programming langs:** Software dev kits for implementing API calls instead of manully writing calls.
- **Code Snippets and Embeds:** Code embeds for implementing features like video player or pptx viewer with ease.
- **Team Collaboration Support**: Create an organization on dashboard, add other instructors to contribute to course creation and maintainance.
- **Export & Data Portability:** Manifest-based exports / ZIP export (deferred).
- **Streaming Optimization:** Adaptive streaming (HLS) for video.
- **Auth Enhancements:** SSO / OAuth integrations.
- **Observability & Performance:** Logging, caching, rate limiting, DB optimizations.
- **Go Migration (optional):** Rewriting high-throughput services for scale.

---

## 🌍 Long-Term Vision
- DRM for digital content protection.
- Live streaming & webinars.
- Advanced analytics and learning pipelines (ClickHouse / CDC).
- Drag and Drop Based LMS Frontend Creation Tool
- Marketplace for templates, plugins, and instructor tools.


---

## 💡 Notes for Partners / Pilot Institutions
- MVP focuses on **core functionality**, not completeness or final UI polish.
- Early collaborators will shape Phase 1 / Phase 2 priorities.
- Feature requests are categorized as:
  - **Core Fit:** benefits all users — prioritized.
  - **Custom Extension:** partner-specific — considered as paid customization or Phase 2 work.