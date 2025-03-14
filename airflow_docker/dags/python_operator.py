from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
import datetime as dt


def get_name():
    return "Some Random Guy"

def greet(age, ti):
    name = ti.xcom_pull(task_ids='get_name')
    print(f"Hello, I am {name} and I am {age} years old")

default_args = {
    "owner": "Joyan",
    "retries": 5,
    "retry_delay": dt.timedelta(minutes=5)
}

with DAG(
    default_args=default_args,
    dag_id="python_operator_v3",
    description = "This is my first Python Operator DAG",
    schedule_interval="@daily",
    start_date=dt.datetime(2025, 3, 14, 12)
) as dag:
    task1 = PythonOperator(
        task_id = 'task1',
        python_callable = greet,
        op_kwargs = {
            'age': 25
        }
    )

    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable = get_name
    )



    task2 >> task1