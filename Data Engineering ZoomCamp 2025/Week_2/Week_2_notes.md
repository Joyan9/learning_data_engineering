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

Open the URL http://localhost:8080 in your browser to launch the UI.

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


### Basics of Kestra

#### Flows
In Kestra you can create **Flows** to create a sequence of tasks

Flows define tasks, the execution order of tasks, as well as flow inputs, variables, labels, triggers, and more.

Flows are defined in YAML to keep the code portable and language-agnostic.

**Required Properties**
1. `id` - This ID must be unique within a namespace and is immutable (you cannot rename the flow ID later, but you can recreate it with a new name).
2. `namespace` - Each flow lives in one namespace. Namespaces are used to group flows and provide structure. Once the flow is created, you cannot change the namespace
3. `tasks` - The list of tasks to be executed. Tasks are atomic actions in your flows. By default, they will run sequentially one after the other.

#### Tasks
Tasks are atomic actions in your flows.

**Required Properties**
1. `id` - A unique identifier for the task
2. `type` - A full Java class name that represents the type of task

#### Inputs
Inputs allow you to make your flows more dynamic and reusable.

Instead of hardcoding values in your flow, you can use inputs to make your workflows more adaptable to change.

**Required Properties**
1. `name`
2. `type`

Reference inputs using `{{ inputs.input_name }}`


  ```yaml
  id: inputs_demo
  namespace: company.team

  inputs:
    - id: user
      type: STRING
      defaults: Rick Astley

  tasks:
    - id: hello
      type: io.kestra.plugin.core.log.Log
      message: Hey there, {{ inputs.user }}
  ```

#### Outputs
Outputs allow you to pass data between tasks and flows.

Use the syntax `{{ outputs.['task_id'].output_property }}` to retrieve a specific output value of a task.


#### Triggers

Triggers automatically start your flow based on events.

A trigger can be a scheduled date, a new file arrival, a new message in a queue, or the end of another flow's execution.

**Required Properties**
1. `id` 
2. `type` 


    ```yaml
    triggers:
      - id: schedule_trigger
        type: io.kestra.plugin.core.trigger.Schedule
        cron: 0 10 * * *
    ```

#### Adding Conditional Logic to Tasks
We use the `if task` from `io.kestra.plugin.core.flow.If` to create conditional logic - run specific tasks only if certain conditions are met

```yaml
tasks:
  - id: if
    type: io.kestra.plugin.core.flow.If
    condition: "{{inputs.block=='True'}}"
    then:
      - id: when_true
        type: io.kestra.plugin.core.log.Log
        message: "The True condition task ran"
    else:
      - id: when_false
        type: io.kestra.plugin.core.log.Log
        message: "The False condition task ran"
```

#### Adding Loops to Tasks
In Kestra - the `ForEach` flowable task executes a group of tasks for each value in the list.

`type: "io.kestra.plugin.core.flow.ForEach"`


You can control how many task groups are executed concurrently by setting the `concurrencyLimit` property.

- `concurrencyLimit: 0`: Kestra will execute all task groups concurrently for all values.
- `concurrencyLimit: 1`: Kestra will execute each task group one after the other starting with the task group for the first value in the list. This is also the default behaviour.

The `values` should be defined as a JSON string or an array, e.g. a list of string values `["value1", "value2"]` or a list of key-value pairs `[{"key": "value1"}, {"key": "value2"}]`.

**Variables to Access Loop Values**
- `{{ taskrun.value }}` - Access the current iteration value
- `{{ parent.taskrun.value }}` - To access the current iteration value if you are in a nested child task. 
- `{{ taskrun.iteration }}` - Access the batch or iteration number


```yaml
 - id: for_each
    type: io.kestra.plugin.core.flow.ForEach
    values: ["John", "Jane", "Janet"]
    tasks:
  
      - id: print
        type: io.kestra.plugin.core.log.Log
        message: "Iteration Value: {{taskrun.value}}"
```

