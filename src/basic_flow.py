from prefect import flow, task, get_run_logger
from prefect.task_runners import SequentialTaskRunner

@task
def log_something():
    logger = get_run_logger()

    logger.info("this is a log")

@flow(task_runner=SequentialTaskRunner())
def basic_flow():
    log_something.submit()

if __name__ == "__main__":
    basic_flow()
