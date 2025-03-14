from airflow.decorators import dag, task
import datetime as dt


default_args = {
    "owner": "Joyan",
    "retries": 5,
    "retry_delay": dt.timedelta(minutes=5)
}

@dag(
    dag_id = "dag_with_taskflow_api_v3",
    description = "This is my first DAG with TaskFlow API",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=dt.datetime(2025, 3, 14, 13)
)
def greet_etl():
    
    @task(multiple_outputs=True)
    def get_name():
        return {
            "first_name":"Joyan",
            "last_name":"Bhathena"
            }
    
    @task()
    def get_age():
        return 25
    
    @task()
    def greet(first_name, last_name, age):
        print(f"Hey there, I am {first_name} {last_name} and I am {age} years old")

    
    name = get_name()
    age = get_age()
    greet(name['first_name'], name['last_name'], age)

dag = greet_etl()