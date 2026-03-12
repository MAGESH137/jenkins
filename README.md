# 🚀 Jenkins Practice Repository — Task Manager App

A **real, working polyglot application** built specifically to practice Jenkins CI/CD pipelines.  
Includes a **Java Spring Boot API**, **React frontend**, and **Python analytics service** — designed to run in the exact parallel pipeline from your Jenkins training.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Jenkins Pipeline                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Java Backend │  │React Frontend│  │  Python Service  │  │
│  │ maven:3.9    │  │ node:20      │  │ python:3.11-slim  │  │
│  │ Spring Boot  │  │ React 18     │  │ Flask + pytest    │  │
│  │ Port: 8080   │  │ Port: 3000   │  │ Port: 5000        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│        ↑                  ↑                   ↑             │
│        └──────────────────┴───────────────────┘             │
│                    Parallel Stages                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
jenkins-practice-repo/
├── Jenkinsfile                    ← 🎯 Main pipeline (practice this!)
├── docker-compose.yml             ← Local development stack
├── docker-compose.test.yml        ← Integration test stack
│
├── backend/                       ← Java Spring Boot REST API
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/
│       ├── main/java/com/devops/practice/
│       │   ├── TaskManagerApplication.java
│       │   ├── controller/
│       │   │   ├── TaskController.java    (REST endpoints)
│       │   │   └── HealthController.java
│       │   ├── model/Task.java
│       │   └── service/TaskService.java
│       └── test/java/com/devops/practice/
│           ├── controller/TaskControllerTest.java  (8 tests)
│           └── service/TaskServiceTest.java        (10 tests)
│
├── frontend/                      ← React 18 SPA
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── App.js + App.test.js   (9 tests)
│       ├── components/
│       │   ├── TaskList.js + TaskList.test.js  (5 tests)
│       │   ├── TaskForm.js
│       │   └── StatsBar.js
│       └── services/taskService.js
│
└── python-service/                ← Flask analytics microservice
    ├── app.py
    ├── requirements.txt
    ├── pytest.ini
    ├── Dockerfile
    └── tests/
        └── test_analytics.py      (30+ tests)
```

---

## 🔧 The Pipeline You Are Practising

```groovy
pipeline {
  agent none
  stages {
    stage('Parallel Build') {
      parallel {
        stage('Java Backend') {
          agent { docker { image 'maven:3.9-eclipse-temurin-17' } }
          steps { sh 'mvn clean package' }
        }
        stage('React Frontend') {
          agent { docker { image 'node:20-alpine' } }
          steps { sh 'npm ci && npm run build' }
        }
        stage('Python Tests') {
          agent { docker { image 'python:3.11-slim' } }
          steps { sh 'pip install -r requirements.txt && pytest' }
        }
      }
    }
  }
}
```

---

## ⚡ Quick Start

### 1. Fork & Clone
```bash
# Fork this repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/jenkins-practice-repo.git
cd jenkins-practice-repo
```

### 2. Run Locally with Docker Compose
```bash
docker compose up -d
# Backend API:  http://localhost:8080
# Frontend UI:  http://localhost:3000
# Analytics:    http://localhost:5000
```

### 3. Run Tests Locally

```bash
# Java (requires Java 17 + Maven)
cd backend && mvn test

# React
cd frontend && npm ci && npm test -- --watchAll=false

# Python
cd python-service && pip install -r requirements.txt && pytest -v
```

---

## 🏗️ Setting Up Jenkins

### Step 1 — Install required plugins
- Pipeline
- Docker Pipeline
- Git Plugin
- Blue Ocean *(optional — great for visualisation)*
- JUnit Plugin

### Step 2 — Ensure Docker is available on the Jenkins agent
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
# Verify:
sudo -u jenkins docker ps
```

### Step 3 — Create the pipeline job
1. **Dashboard → New Item → Pipeline → OK**
2. Under **Pipeline**:
   - Definition: `Pipeline script from SCM`
   - SCM: `Git`
   - Repository URL: `https://github.com/YOUR_USERNAME/jenkins-practice-repo`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
3. **Save → Build Now**

### Step 4 — Watch in Blue Ocean
Go to **Open Blue Ocean** and watch the three parallel stages run simultaneously!

---

## 🔬 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks?priority=HIGH` | Filter by priority |
| GET | `/api/tasks/{id}` | Get single task |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| PATCH | `/api/tasks/{id}/toggle` | Toggle completed |
| DELETE | `/api/tasks/{id}` | Delete task |
| GET | `/api/tasks/stats` | Get counts |
| GET | `/health` | Health check |

**Example — Create a task:**
```bash
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Jenkins","priority":"HIGH"}'
```

**Analytics Service:**
```bash
curl http://localhost:5000/analytics/summary
curl http://localhost:5000/health
```

---

## 🧪 Test Coverage

| Service | Framework | Test Count | Coverage |
|---------|-----------|-----------|---------|
| Java Backend | JUnit 5 + MockMvc | 18 tests | ~85% |
| React Frontend | React Testing Library | 14 tests | ~75% |
| Python Service | pytest | 30+ tests | ≥80% (enforced) |

---

## 🎓 Pipeline Practice Exercises

Once the basic pipeline works, try these enhancements:

### Level 1 — Beginner
- [ ] Add a `Checkout` stage before the parallel block
- [ ] Archive the built JAR as a Jenkins artifact
- [ ] Publish JUnit test results from all three services
- [ ] Add `timestamps()` and `timeout(30, 'MINUTES')` options

### Level 2 — Intermediate
- [ ] Add a `when { branch 'main' }` condition to a stage
- [ ] Add a post block with `success`, `failure`, and `always` sections
- [ ] Use `withCredentials` to inject a dummy secret
- [ ] Add a manual `input` approval gate before "Deploy"

### Level 3 — Advanced
- [ ] Add SonarQube code quality stage (requires SonarQube setup)
- [ ] Build Docker images in a 4th parallel stage using `docker.build()`
- [ ] Push images to Docker Hub using `docker.withRegistry()`
- [ ] Configure GitHub webhook for instant build triggers
- [ ] Add a Multibranch Pipeline that auto-builds all branches

### Level 4 — Expert
- [ ] Extract build logic into a Jenkins Shared Library
- [ ] Add Ansible deploy stage using `ansiblePlaybook()`
- [ ] Implement canary deployment with `kubectl`
- [ ] Set up parallel matrix testing across multiple JDK versions

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker: command not found` in pipeline | Add jenkins user to docker group, restart Jenkins |
| `npm ci` fails with cache error | Remove `-v` mount arg or clear npm cache |
| Maven tests fail in Docker | Ensure `-v $HOME/.m2:/root/.m2` mount is set |
| Python `ModuleNotFoundError` | Check `pip install -r requirements.txt` ran in correct `dir()` |
| Port already in use | `docker compose down` then retry |
| Jenkins can't pull Docker image | Check internet access from Jenkins agent: `docker pull node:20-alpine` |

---

## 📄 Licence

MIT — Free to use for learning and practice.
