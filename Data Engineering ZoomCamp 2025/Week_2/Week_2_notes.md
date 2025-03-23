# **Week 2 - Workflow Orchestration**

## What is an Orchestrator?
It is a tool that used to automate, manage and coordinates various workflows (a series of tasks) across different services, systems or applications.

Think of it like a conductor of an orchestra, making sure all components perform in harmony, following a predefined sequence or set of rules. Whether you're dealing with data pipelines, microservices, or CI/CD systems, an orchestrator ensures everything runs reliably without manual intervention.

![Automation versus Orchestration](image.png)
Source: https://kestra.io/blogs/2024-09-18-what-is-an-orchestrator

### Why Use an Orchestrator?
1. Orchestrators allows you to manage multiple workflows, without an orchestrator it would very difficult to manage different task flows and workflows. For instance, when you have 3 scripts, you can use the Cron tab to schedule jobs but as you scale and need more fine-tuned workflows you would need an orchestrator.

2. Orchestrators can help manage failures - if a task fails, the orchestrator can automatically retry it, send alerts, or trigger a recovery process

3. Most orchestrators provide monitoring tools which can be used to identify bottlenecks, check each task's status, check overall performance and so on.

### Orchestrator Use Cases
- In Data engineering
    - Create workflows to automate extract - load - transform
- In CI/CD
    - Orchestration involves tasks like compiling code, running tests, deploying to a staging environment, and triggering manual approval for production deployment. 


## Kestra - Open-Source Orchestrator

### **Installing Kestra on Windows with Docker-Compose**
Download the Docker Compose file - it contain Kestra and Postgres for data persistence

```bash
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kestra-io/kestra/develop/docker-compose.yml" -OutFile "docker-compose.yml"
```

#### **Instructions to Change PostgreSQL Volume Path or Store Data Locally**  

These steps will guide you on how to **change the PostgreSQL volume path** in Docker Compose, allowing you to store database data in a specific folder so that progress is not lost when containers are restarted.


**Option 1: Store Data Locally (Change Volume Path)**
To store PostgreSQL data in a specific folder on your **Windows machine**, follow these steps:

**1️⃣ Update `docker-compose.yml`**
Modify the `postgres` service to mount a local folder:

```yaml
services:
  postgres:
    image: postgres
    volumes:
      - "C:/Users/HP/OneDrive/Desktop/Data Engg/Data Engineering ZoomCamp 2025/Week_2/postgres-kestra-data:/var/lib/postgresql/data"
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4
```

**2️⃣ Create the Local Folder**
Manually create the directory to ensure Docker can access it:
1. Open **File Explorer**.
2. Navigate to:  
   `C:\Users\HP\OneDrive\Desktop\Data Engg\Data Engineering ZoomCamp 2025\Week_2`
3. Create a folder named **postgres-kestra-data**.

**3️⃣ Restart Docker Compose**
Run the following in **PowerShell or Command Prompt**:

```sh
docker-compose down  # Stop the existing container
docker-compose up -d  # Restart with the new volume
```

Now, PostgreSQL will store all data inside your specified folder!

**Option 2: Use Docker’s Named Volume (Default)**
If you want to use Docker's built-in storage (instead of a specific folder), use a **named volume**:

**1️⃣ Update `docker-compose.yml`**
Modify the `postgres` service:

```yaml
services:
  postgres:
    image: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4

volumes:
  postgres-data:
    driver: local
```

**2️⃣ Restart Docker Compose**
Run:

```sh
docker-compose down  # Stop containers
docker-compose up -d  # Restart with the named volume
```

If you've stored data locally (Option 1) or used a named volume (Option 2), your database **persists** even after restarting:

