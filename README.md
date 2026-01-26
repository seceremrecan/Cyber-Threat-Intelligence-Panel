# 🛡️ Cyber Threat Intelligence Panel  
### LLM-Integrated OSINT Platform for Phishing, Stealer and Data Leak Detection

> Thesis Project – Sakarya University  
> Computer Engineering Department  
> **Emre Can Seçer · Muhammet Eren Akdağ · Ekrem Selçuk Çelik**  
> Supervisor: Dr. Musa Balta  

---

## 📌 Overview

This project is a **modular OSINT-based Cyber Threat Intelligence (CTI) platform** designed to detect and analyze:

- Phishing URLs  
- Data breaches & leaks  
- Stealer malware logs  
- Malicious IPs, domains, and emails  

It combines **traditional OSINT analysis** with a **local LLM (Ollama)** to provide contextual, human-readable security insights.

**Tech Stack**
- Backend: Python (Flask)  
- Frontend: React  
- Database: PostgreSQL  
- AI Layer: Ollama (LLM)  
- Orchestration: Docker & Docker Compose  

---

## 🎯 Project Goals

- Centralize OSINT-based cyber threat detection  
- Correlate IP, domain, URL, email, and stealer data  
- Normalize and classify threats  
- Provide AI-based contextual explanations  
- Run fully **offline & self-hosted** (LLM is local; some OSINT modules may require external API keys if enabled)

---

## 🧱 System Architecture

The system has three main layers:

1. **Database Layer (PostgreSQL)**  
   Stores OSINT datasets, stealer logs, breach data.

2. **Backend / API Layer (Flask)**  
   Validates input, routes requests, runs analysis modules, and returns JSON results.

3. **Frontend Layer (React)**  
   User interface that sends IoCs to backend and displays results.

All services run in isolated containers using **Docker Compose**.

---

## 🔍 Supported Input Types

| Type   | Example                         |
|--------|---------------------------------|
| Domain | example.com                     |
| IP     | 8.8.8.8                         |
| Email  | user@example.com                |
| URL    | https://phishing.site/login     |

Regex validation is applied in both frontend and backend.

---

## 🧩 Core Modules

| Module | Description |
|--------|-------------|
| Input Analysis | Detects IoC type and routes to correct module |
| DNS / IP Analysis | WHOIS, DNS records, geo location |
| Phishing Detection | Blacklist & pattern-based checks |
| Data Breach | Email/domain leak search |
| Stealer Log Analysis | Regex-based credential scanning |
| HTTP Security | CSP, HSTS, headers |
| Robots.txt | Disallow parsing |
| Location Detail | IP geo lookup |
| LLM Integration | AI-based contextual explanation |

---

## 🤖 AI Integration (Ollama)

The system uses **local LLMs via Ollama**.

The model:
1. Receives technical JSON output  
2. Interprets security risks  
3. Returns human-readable explanations

Example questions:
- “Is this domain dangerous?”  
- “What is the most critical issue?”  
- “What should I do next?”

---

## 🐳 Running the Project with Docker

### ✅ Requirements (Install First)

- Git → https://git-scm.com/downloads  
- Docker Desktop → https://www.docker.com/products/docker-desktop  

Verify installation:

```bash
git --version
docker --version
docker compose version


# 1) Clone the repository
git clone https://github.com/seceremrecan/Cyber-Threat-Intelligence-Panel.git
cd Cyber-Threat-Intelligence-Panel

# 2) Create .env file in the project root (same folder as docker-compose.yml)
#    (Create a file named ".env" and paste your configuration into it)

# Example .env template:
# ===== Database =====
# HOST=localhost
# USER=postgres
# PASSWORD=CHANGE_ME
# DATABASE=cti_panel
# DATABASE_URL=postgresql://postgres:CHANGE_ME@localhost:5432/cti_panel
#
# ===== Optional: Local LLM (Ollama) =====
# OLLAMA_HOST=http://localhost:11434
# (If ollama runs as a docker service you may use: http://ollama:11434)
#
# ===== OSINT API Keys (Optional) =====
# OTX_API_KEY=
# DNSDUMPSTER_API_KEY=
# WHOIS_API_KEY=

# 3) Build containers (first run)
docker compose build

# (Optional) Clean rebuild (after major updates)
docker compose build --no-cache

# 4) Start the system (run in background)
docker compose up -d

# 5) Check status (see running containers)
docker compose ps

# 6) View logs (if something goes wrong)
docker compose logs -f

# 7) Stop the system
docker compose down

# 8) Full reset (⚠️ removes volumes / database data)
docker compose down -v
docker system prune -f

---

## 🌐 Access the Project (After Running)

After you run the containers with Docker, you can access the project from your browser:

- **Frontend (Web Panel):** http://localhost:3000  
- **Backend API:** http://localhost:5000/api  

> **Note:** `localhost` means the project runs on **your own computer**.  
> If you want to access it from another device on the same network, you must expose ports and use your computer’s local IP address (advanced setup).

---

## 📩 Configuration / .env Request

This project requires environment configuration (`.env`) for database settings and optional OSINT/LLM integrations.

✅ **Recommended (Safe) Approach:**  
Users should create their own `.env` file using the provided template and add their **own API keys**.

📌 **If you want to run the project with the original configuration used in the graduation setup:**  
You can contact me to request the original `.env` configuration and setup details.

> ⚠️ **Security Notice:** The original `.env` may include sensitive keys and should never be shared publicly or committed to GitHub.  
> It will only be shared privately for academic/demo purposes.

