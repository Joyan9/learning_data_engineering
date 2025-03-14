# Technical Details

## Task Lifecycle
The diagram below illustrates the different statuses a task can have
It starts with no status and once it is submitted to the Scheduler it can have either of these 4 status values
- `Scheduled` - scheduled for running
- `Removed` - removed from DAG
- `Skipped` - skipped
- `Upstream Failed` - upstream task before it failed

After being `Scheduled`, a task is submitted to the Executor which assigns it the `queued` status and followed by `running`

Post run, the task could either have
- `Success` - task ran successfully
- `Failed` - task failed
- `Shutdown` - task was not allowed to run / cancelled manualy

Both failed and shutdown tasks can be assigned `up for retry` status if it has not exceeded the max retry limit.

Note that a running task could also have `up for reschedule` status if it needs to run after every certain interval.

![alt text](image-1.png)

## Operators

### Bash Operator

```python
import datetime

from airflow.operators.bash import BashOperator
from airflow import DAG

# You can define the default aruguements for a DAG as a dict
default_args = {
    'owner' : 'joyan',
    'retries' : 5,
    'retry_delay' : datetime.timedelta(minutes=2)
}

with DAG(
    dag_id = 'first_dag',
    default_args = default_args,
    descriptiom = 'This is my first DAG',
    start_date = datetime.datetime(2025, 3, 31, 12),
    schedule_interval = '@daily'
) as dag:
    task1 = BashOperator(
        task_id = 'task_1',
        bash_command = 'echo hello world'
    )

```

## XComs
- Stands for cross-communications between tasks
- An XCom is identified by
    - it's name
    - task_id
    - dag_id
- Designed to pass small values of data (not large dataframes)
- You can either push or pull XCom values

**Push XCom**
```python
task_instance.xcom_push(key = "identifier", value = any_serializable_value)
```

**Pull XCom**

```python
task_instance.xcom_pull(key = "identifier", task_ids = "task1")
```

- XComs are a relative of Variables, with the main difference being that XComs are per-task-instance and designed for communication within a DAG run, while Variables are global and designed for overall configuration and value sharing.