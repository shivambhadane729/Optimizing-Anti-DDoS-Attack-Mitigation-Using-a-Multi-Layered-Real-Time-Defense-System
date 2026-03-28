# Optimizing Anti-DDoS Attack Mitigation Using a Multi-Layered Real-Time Defense System 🛡️☁️

## 📖 Project Overview
This project implements a comprehensive, cloud-native defense architecture designed to intelligently detect, mitigate, and divert Distributed Denial-of-Service (DDoS) attacks in real-time. 

Traditional single-layer defenses collapse under sudden, multi-vector DDoS attacks. This system prevents service downtime by employing proactive **Machine Learning** (to detect anomalies instantly), dynamic load balancing (to absorb traffic spikes), and intelligent rate throttling and IP blacklisting—ensuring legitimate users always maintain high service availability even during severe attacks.

## 🚀 Cloud-Native Architecture & Tech Stack

The entire system has been migrated from a local monolithic application to a highly scalable **Microservice Architecture** deployed on **Google Cloud Platform (GCP)**.

### 🛠️ Core Services
* **Frontend Dashboard**: React.js (Material-UI, Chart.js)
* **API Backend**: FastAPI (Python, Uvicorn, SQLAlchemy)
* **ML Detection Service**: Python (Scikit-learn, Pandas, Joblib) - *Standalone microservice running Random Forest & Isolation Forest on UNSW-NB15 datasets.*
* **Database**: Google Cloud SQL (PostgreSQL)

### ☁️ Google Cloud Platform Capabilities Used
* **Container Orchestration**: **Google Kubernetes Engine (GKE)** to orchestrate and automatically scale our dockerized microservices.
* **Security & Edge Filtering (WAF)**: **Google Cloud Armor** to automatically block malicious source IPs at the highest network edge before they impact backend pods.
* **Load Balancing**: **Cloud Load Balancing (Ingress)** to distribute incoming public internet traffic evenly across GKE pods.
* **Container Storage**: **Google Artifact Registry** as the private repository for storing the Docker images.

## ⚙️ Automated CI/CD Pipeline
The project utilizes a hands-free continuous deployment workflow implemented via **GitHub Actions** and **Kustomize**.
1. **Push**: Code is pushed to the `main` branch.
2. **Build**: GitHub Actions builds the `frontend`, `backend`, and `ml-service` Docker images.
3. **Artifact Registry**: Images are securely pushed to GCP Artifact Registry.
4. **Deploy**: Kustomize dynamically injects the new image tags into our Kubernetes manifests (`k8s/`).
5. **Rollout**: A rolling update is triggered on the GKE Cluster in `asia-south1`, replacing the old pods with zero downtime.

## 🧠 Multi-Layered Defense Execution Flow

1. **Layer 1: Edge Security (WAF)**
   Google Cloud Armor intercepts traffic, matching it against known bad IP lists and immediately dropping severe volumetric attacks.
2. **Layer 2: Load Balancing & Rate Limiting**
   Surviving traffic hits the GKE Load Balancer and FastAPI `slowapi` rate limiters. Traffic surges are throttled and cleanly distributed across available nodes to prevent CPU exhaustion.
3. **Layer 3: Real-Time Machine Learning Inspection**
   Connections are forwarded via internal HTTP to the isolated `ml-service` pod. The traffic profile is queried against the Random Forest ML model to detect subtle low-and-slow Layer 7 attacks that bypassed standard thresholds.
4. **Layer 4: Reactive Blacklisting & Honeypot Diversion**
   If the ML engine classifies an IP as malicious, the backend communicates with the host firewalls/OS to permanently drop the IP, while simultaneously diverting the bad connection into isolated Honeypots for threat analysis.

## 📊 Live Monitoring
Administrators can log into the React dashboard to view live charts detailing clean requests vs. malicious requests, CPU/RAM stabilization during mitigation, and lists of actively blocked IPs.
