# 🔗 URL Shortener - Microservices Edition

## A modern, production-ready URL shortener built with microservices architecture, complete with monitoring, alerting, and a beautiful web interface.

## 🌟 What's This?
Transform long, ugly URLs into short, memorable links with this enterprise-grade URL shortener. Built with a modern microservices architecture, it's not just a URL shortener - it's a full-stack monitoring platform!

<img width="1899" height="871" alt="image" src="https://github.com/user-attachments/assets/bd9d4f93-deb2-4cb9-8da1-e12015cb4fb8" />


## 🎯 Perfect For:
**Developers** learning microservices

**Startups** needing a scalable URL shortener

**DevOps** teams practicing containerization

**Anyone** tired of long URLs!


## 📊 Features

### 🔗 Core Functionality

| Feature          | Description                                      | Status |
|------------------|--------------------------------------------------|--------|
| **URL Shortening** | Create short URLs with auto-generated or custom codes | ✅ Live |
| **Click Tracking** | Monitor how many times each link is clicked        | ✅ Live |
| **Expiration**     | Set automatic expiration dates for links          | ✅ Live |
| **Web Dashboard**  | Beautiful, responsive interface                   | ✅ Live |

---

## 🛠️ Tech Stack

| Layer      | Technology                 | Purpose                   |
|------------|-----------------------------|---------------------------|
| **Frontend**  | Nginx + HTML/Tailwind        | User interface            |
| **Backend**   | Python Flask + SQLite        | API & business logic      |
| **Monitoring**| Prometheus + Grafana         | Metrics & visualization   |
| **Alerting**  | AlertManager + Slack         | Notifications             |
| **Container** | Docker + Docker Compose      | Deployment                |

---
## 📈 Monitoring & Analytics

- **Real-time metrics** – Track URL creations and redirects  
- **Performance monitoring** – 95th percentile response times  
- **Error tracking** – Automatic alerting for issues  
- **Beautiful dashboards** – Pre-configured Grafana views  

---
## 🗂️ System Architecture

```mermaid
graph TB
    subgraph "User Facing"
        A[🌐 Users] --> B[Frontend<br/>Nginx:80]
    end
    
    subgraph "Application Layer"
        B --> C[Backend API<br/>Flask:5000]
        C --> D[(SQLite<br/>Database)]
    end
    
    subgraph "Monitoring Stack"
        C --> E[📊 Prometheus<br/>:9090]
        E --> F[📈 Grafana<br/>:3001]
        E --> G[🚨 AlertManager<br/>:9093]
        G --> H[💬 Slack]
    end
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#e0f2f1
    style G fill:#ffebee
```
---
🚀 Quick Start (3-Step Deployment)

 ```bash
# 1. Clone & setup
git clone <your-repo>
cd url-shortener-microservices

# 2. Deploy everything (it's magic! ✨)
docker-compose up -d

# 3. Celebrate! 🎉
echo "Your URL shortener is LIVE at http://localhost:80"
 ```

 ---
## 📸 Screenshots

### 🎨 Web Interface
<img width="1136" height="786" alt="Screenshot 2025-11-25 073145" src="https://github.com/user-attachments/assets/f0fd8fb6-6cfa-4eec-9a17-0e5c5d5a01d7" />
<img width="1919" height="759" alt="Screenshot 2025-11-26 115601" src="https://github.com/user-attachments/assets/c5dbb68e-9b5a-4879-a4a8-111f1a7e0246" />

### Docker & Docker-Compose
<img width="1519" height="1002" alt="Screenshot 2025-11-26 171213" src="https://github.com/user-attachments/assets/bd1a2120-64cd-4393-8978-5ed4224e3eba" />

<img width="1519" height="397" alt="Screenshot 2025-11-26 172650" src="https://github.com/user-attachments/assets/204a3118-a26f-447b-8932-d6517c1efe75" />

<img width="1410" height="607" alt="Screenshot 2025-11-26 173418" src="https://github.com/user-attachments/assets/c21466d8-38cd-4484-a73f-54d31ff3b721" />

<img width="1900" height="860" alt="Screenshot 2025-11-26 174852" src="https://github.com/user-attachments/assets/dae1557f-7fed-4304-8375-ae99e86858b8" />


### 📊 Prometheus
<img width="1917" height="667" alt="Screenshot 2025-11-25 074632" src="https://github.com/user-attachments/assets/48949b28-c09d-4420-997d-bba0b238f024" />

<img width="1919" height="637" alt="Screenshot 2025-11-25 074749" src="https://github.com/user-attachments/assets/0bf809ce-a521-40a3-9491-0c247089ef21" />

<img width="1919" height="637" alt="Screenshot 2025-11-25 074749" src="https://github.com/user-attachments/assets/e7c073ef-415b-4aad-991b-1b6f0334156c" />


### Metrics
<img width="1583" height="937" alt="Screenshot 2025-11-24 210310" src="https://github.com/user-attachments/assets/3522cf9e-406e-4cd3-b343-149940133eb2" />


### 🚨 AlertManager	
<img width="1919" height="834" alt="Screenshot 2025-11-26 113623" src="https://github.com/user-attachments/assets/9d5d438d-a252-4d0f-821e-138373626fd6" />

<img width="1919" height="802" alt="Screenshot 2025-11-26 113527" src="https://github.com/user-attachments/assets/c4642bbd-ec2c-4273-83b0-ca9bcf9660c9" />


### 💬 slack
<img width="1400" height="481" alt="Screenshot 2025-11-26 124816" src="https://github.com/user-attachments/assets/8f87ef46-b7d2-4a3d-ba34-b715d4597b96" />

<img width="1400" height="473" alt="Screenshot 2025-11-26 124757" src="https://github.com/user-attachments/assets/239eb3b7-e341-4e31-9e43-34392ff82a0b" />

<img width="1377" height="444" alt="Screenshot 2025-11-26 124834" src="https://github.com/user-attachments/assets/31f653c3-af96-46f4-855e-1fcc6df9798f" />

### 📈 Grafana
<img width="1919" height="871" alt="Screenshot 2025-11-28 112404" src="https://github.com/user-attachments/assets/d9e6f9b9-b5bc-4fa7-bc4e-05fe053f56a5" />

<img width="1899" height="867" alt="Screenshot 2025-11-28 114053" src="https://github.com/user-attachments/assets/f94a1e19-e6f1-4df8-81d6-d0dc321a8d03" />

---
## videos 📽️

https://github.com/user-attachments/assets/5da1a69f-8261-42f0-b2a0-ddce584aa4f9

https://github.com/user-attachments/assets/ca21ed63-54e5-4a80-9a44-0461067935bf

https://github.com/user-attachments/assets/a6eb292d-1c09-4d8a-890f-90b2e128577f


## 🤝 Contributers
Hesham mohamed Elngar
Shady
Waleed 
Mostafa Saad

 

