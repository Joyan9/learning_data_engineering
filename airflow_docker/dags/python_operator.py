from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
import datetime as dt


def get_name(ti):
    first_name = ti.xcom_push(key='first_name', value='Joyan')
    last_name = ti.xcom_push(key='last_name', value='Bhathena')

def get_age(ti):
    age = ti.xcom_push(key='age', value=25)

def greet(ti):
    first_name = ti.xcom_pull(key='first_name', task_ids='get_name')
    last_name = ti.xcom_pull(key='last_name', task_ids='get_name')
    age = ti.xcom_pull(key='age', task_ids='get_age')
    print(f"Hello, I am {first_name}-{last_name} and I am {age} years old")

default_args = {
    "owner": "Joyan",
    "retries": 5,
    "retry_delay": dt.timedelta(minutes=5)
}

with DAG(
    default_args=default_args,
    dag_id="python_operator_v5",
    description = "This is my first Python Operator DAG",
    schedule_interval="@daily",
    start_date=dt.datetime(2025, 3, 14, 12)
) as dag:
    task1 = PythonOperator(
        task_id = 'greet_after_getting_name_and_age',
        python_callable = greet
    )

    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable = get_name
    )

    task3 = PythonOperator(
        task_id = 'get_age',
        python_callable = get_age
    )



    task2 >> task1
    task3 >> task1