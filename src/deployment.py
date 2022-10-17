from deployments2 import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from alpha_vantage_flow import alpha_vantage_etl
from prefect.filesystems import GitHub
from prefect.filesystems import Azure
from prefect.infrastructure.docker import DockerContainer
from prefect.flows import load_flow_from_script, load_flow_from_text

cr = CronSchedule(cron="0 12 * * *", timezone="America/Chicago")
dp = Deployment.build_from_flow(flow=alpha_vantage_etl, name="alpha_vantage_etl", schedule=cr)
dp.apply()

gh = GitHub.load("prefect-training-gh")
dp = Deployment.build_from_flow(flow=alpha_vantage_etl, name="alpha_vantage_etl_gh", storage=gh)
dp.apply()

az = Azure.load("prefecttraining-az")
dp = Deployment.build_from_flow(flow=alpha_vantage_etl, name="alpha_vantage_etl_az", storage=az)
dp.apply()

dc = DockerContainer.load("docker")
dp = Deployment.build_from_flow(flow=alpha_vantage_etl, name="alpha_vantage_etl_dc", infrastructure=dc)
dp.apply()