from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from alpha_vantage_flow import alpha_vantage_etl

cr = CronSchedule(cron="0 12 * * *", timezone="America/Chicago")
dp = Deployment.build_from_flow(flow=alpha_vantage_etl, name="alpha_vantage_etl", schedule=cr)
dp.apply()