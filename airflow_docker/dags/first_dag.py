from airflow import DAG # type: ignore
from airflow.operators.bash import BashOperator # type: ignore
import datetime as dt


default_args = {
    "owner": "Joyan",
    "retries": 5,
    "retry_delay": dt.timedelta(minutes=5)
}

with DAG(
    dag_id="first_dag_v3",
    description = "This is my first DAG",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=dt.datetime(2025, 3, 14, 13)
) as dag:
    task1 = BashOperator(
        task_id = 'task1',
        bash_command = "echo Hello, I am task 1"
    )

    task2 = BashOperator(
        task_id = 'task2',
        bash_command = "echo I am task 2 I run after task 1"
    )

    task3 = BashOperator(
        task_id = 'task3',
        bash_command = "echo I am task 3 run after task 1"
    )

    # task1.set_downstream(task2)
    task1 >> task2
    task1 >> task3
