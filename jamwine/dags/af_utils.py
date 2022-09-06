import logging
from airflow.models import Variable


def border_decorator(f_py=None, border='=', length=60):
    assert callable(f_py) or f_py is None
    def _decorator(func):
        def function_wrapper(*args,**kwargs):
            logging.info(border*length)
            res = func(*args,**kwargs)
            logging.info(border*length)
            return res
        return function_wrapper
    return _decorator(f_py) if callable(f_py) else _decorator


@border_decorator    
def set_af_variables(**kwargs):
    logging.info("Task for setting AF Variables")
    variables = kwargs.get("af_variables")
    for key, val in variables.items():
        if val is not None:
            Variable.set(key, val)
            logging.info(f"AF Variable ->  {key} -> has value -> {val}")
        else:
            logging.info(f"AF Variable ->  {key} -> has a missing value")


@border_decorator(border='-')
def get_af_variable(key, default_val):
    logging.info(f"Task to get a variable: {key}")
    af_variable = Variable.get(key, default_var = default_val)
    logging.info(f"AF Variable {key} is: {af_variable}")
    return af_variable


@border_decorator(border='-')
def set_xcom(*args, **context):
    for key, val in args:
        logging.info(f"Setting xcom value for key: {key}")
        context['ti'].xcom_push(key=key, value = val)
        logging.info(f"Value for {key} is set to: {val}")


@border_decorator(border='-')
def get_xcom(key, task_id = None, **context):
    if task_id is not None:
        logging.info(f"Getting xcom value for key: {key} having task_id: {task_id}")
        xcom_val = context['ti'].xcom_pull(key=key, task_ids=task_id)
    else:
        logging.info(f"Getting xcom value for key: {key}")
        xcom_val = context['ti'].xcom_pull(key=key)
    logging.info(f"xcom value of {key}: {xcom_val}")
    return xcom_val


@border_decorator
def get_all_xcoms(*args, **context):
    logging.info("Task for fetching xcom value")
    for key,task_id in args:
        _ = get_xcom(key, task_id, **context)