from datetime import timedelta
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

log = logging.getLogger(__name__)

# default list of arguments that can be passed to any of the tasks
default_args = {
    'owner': 'JAMWINE',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['dagjoins@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),

    # Other Parameters that can be specified (if desired)
    # 'max_active_runs': 3
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

DAG_ID = "Example_1_First_Dag"

DATA_PATH = "/opt/airflow/data/"
DEMO_FILE = DATA_PATH+f'{DAG_ID}/demo.txt'

# Creating a DAG instance
dag = DAG(
        dag_id=DAG_ID,
        description="Example DAG 1 using BashOperator and PythonOperator",
        default_args=default_args,
        schedule_interval="@once",
      # start_date=datetime.now(),
)

# task to create an empty file with the bash command `touch`
create_file = BashOperator(
    task_id='create_file',
    bash_command=f'touch {DEMO_FILE}',
    dag=dag,)


# task to write to file using the bash operator
write_to_file = BashOperator(
    task_id='write_to_file',
    bash_command=f'echo "Hello World !" > {DEMO_FILE}',
    dag=dag,)


# task to read the file using the `cat` bash command
read_from_file = BashOperator(
    task_id='read_from_file',
    bash_command=f'cat {DEMO_FILE}',
    dag=dag,)


def message():
    log.info("Airflow is awesome!")
    log.info("Airflow uses DAGs...")
    log.info(f"This DAG has created a file: {DEMO_FILE}")

message_task = PythonOperator(
    task_id="message_task",
    python_callable=message,
    dag=dag,)


# Specify the order fo the tasks
create_file >> write_to_file >> read_from_file >> message_task