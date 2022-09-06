from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator


from af_utils import set_af_variables, get_af_variable, set_xcom, get_xcom, get_all_xcoms, border_decorator

default_args = {
    'owner': 'JAMWINE',
    'start_date': datetime(2021, 1, 1),
    'retries': 1, 
    'max_active_runs': 3
}

af_variables = {"threshold": 100, "directory_1": "/bin", "directory_2":"/etc"}

border = "printf '=%.0s' {1..50};"

macros_commands=border + """echo '\nCurrent execution date: {{ ds }}';
            echo 'Previous execution date : {{ yesterday_ds_nodash }}';
            echo 'Day after the execution date: {{ tomorrow_ds }}';
            echo 'Current date can be modified by macros.ds_add to add 2 days : {{ macros.ds_add(ds, 2) }}'
""" + border

    
@border_decorator
def print_message_from_params(*args,**kwargs):
    logging.info("Task using PythonOperator")
    for i, key in enumerate(args,start=1):
        message = kwargs.get(key, "KeyError, not found.!!")
        logging.info(f"{i}. Custom Value of {key}: {message}")


@border_decorator
def agg_and_compare_files(**context):
    logging.info("Task for aggregating files")
    files_count = int(get_xcom('return_value','get_total_files', **context))+ int(get_xcom('return_value','get_total_files2', **context))
    logging.info(f"Total files in both the directories are {files_count}")
    set_xcom(('actual_file_count',files_count), **context)
    expected_file_count = int(get_xcom('expected_file_count', **context))
    threshold = int(get_af_variable('threshold', default_val=50))
    if abs(files_count - expected_file_count) < threshold:
        set_xcom(("status","Active"), **context)
    else:
        set_xcom(("status","Inactive"), **context) 
    
    
with DAG(
        "Example_2_Airflow_Concepts",
        description="Airflow Concepts",
        start_date=datetime.now() - timedelta(days=70),
        schedule_interval="@weekly",
        default_args=default_args,
        catchup=False
) as dag:

    # task to setup Airflow variables using PythonOperator
    set_af_variables_task = PythonOperator(
        task_id="set_af_variables_task",
        python_callable=set_af_variables,
        op_kwargs={"af_variables":af_variables},
        dag=dag
    )

    # task to execute Bash commands within BashOperator
    bash_set_variable_task = BashOperator(
        task_id="bash_set_variable_task",
        bash_command=border + 'echo "\nTask for setting variable using BashOperator"; airflow variables set AF_user JAMWINE;' + border,
        do_xcom_push=False,
        dag=dag
    )

    # task to demonstrate use of args and kwargs within PythonOperator
    python_print_task = PythonOperator(
        task_id="python_print_task",
        python_callable=print_message_from_params,
        op_args=["message_key","bad_key"],
        op_kwargs={"message_key":"This is the message received using kwargs"},
        dag=dag
    )

    # task to demonstrate use of date-related macros within BashOperator
    bash_print_task = BashOperator(
        task_id="bash_print_task",
        bash_command=border + 'echo "\nTask using BashOperator in {{ dag.dag_id }}" && echo {{ execution_date }}\n' + border,
        do_xcom_push=False,
        dag=dag
    )

    # task to demonstrate use of macros within BashOperator
    macros_task = BashOperator(
        task_id="macros_task",
        bash_command=macros_commands,
        do_xcom_push=False,
        dag=dag
    )

    # task to count files in directory_1, the value `/bin` is retrieved from the macro
    get_total_files = BashOperator(
        task_id='get_total_files',
        bash_command="ls {{ var.value.directory_1 }} | wc -l;",
        dag=dag)
        
    # task to count files in the directory_2, the value `/etc` is retrieved from the params
    get_total_files2 = BashOperator(
        task_id='get_total_files2',
        bash_command="ls {{ params.DIR }} | wc -l;",
        params={'DIR':'/etc'},
        dag=dag)
        
    # task to set the xcom value in Airflow
    set_xcom_task = PythonOperator(
        task_id="set_xcom_task",
        python_callable=set_xcom,
        op_args=[('expected_file_count',100)],
        dag=dag
    )

    # task to demonstrate utilization of values from xcom and variables
    agg_and_compare_files_task = PythonOperator(
        task_id="agg_and_compare_files_task",
        python_callable=agg_and_compare_files,
        dag=dag
    )

    # task to fetch xcom values using PythonOperator
    get_all_xcoms_task = PythonOperator(
        task_id='get_all_xcoms_task',
        python_callable= get_all_xcoms,
        op_args=[('return_value','get_total_files'), 
                ('return_value','get_total_files2'),
                ('actual_file_count',None),
                ('expected_file_count',None),            
                ('af_xcom_bad_key',None),
                ('status',None)],
        dag=dag
    )
        
    # task to fetch xcom value using BashOperator
    status_update_task = BashOperator(
        task_id='status_update_task',
        bash_command=border+"echo '\nXCom fetched, \'Status\': {{ ti.xcom_pull(key=\'status\') }}';"+border,
        do_xcom_push=False,
        dag=dag)


set_af_variables_task >> [bash_print_task, python_print_task]
python_print_task >> set_xcom_task >> agg_and_compare_files_task 
bash_set_variable_task >> bash_print_task >> macros_task >> [get_total_files, get_total_files2]
[get_total_files, get_total_files2] >> agg_and_compare_files_task
agg_and_compare_files_task >> get_all_xcoms_task >> status_update_task