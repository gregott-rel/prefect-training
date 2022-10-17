from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from prefect.filesystems import GitHub
from prefect.filesystems import Azure
from prefect.infrastructure.kubernetes import KubernetesJob
from prefect.flows import load_flow_from_script, load_flow_from_text

# things that would get passed in
extra_pip_packages = "yfinance"
description = "some description"
script_path = "src/basic_flow.py"
flow_function_name = "basic_flow"
version = 1

#things that can be automatically detected
repo_name = "https://github.com/gregott-rel/prefect-training"
repo_branch = "main"

gh = GitHub(repository=repo_name, reference=repo_branch)
block_name = f"{repo_name}:{repo_branch}"\
    .replace("/","")\
    .replace(".","")\
    .replace(":","")
gh.save(name=block_name, overwrite=True)

kj = KubernetesJob()
kj.save(name="k8s", overwrite=True)

fl = load_flow_from_script(script_path)
dp = Deployment.build_from_flow(
    flow=fl, 
    name=flow_function_name, 
    entrypoint=f"{script_path}:{flow_function_name}",
    description=description,
    storage=gh,
    version=version,
    infrastructure=kj,
    infra_overrides={
        "env.EXTRA_PIP_PACKAGES": extra_pip_packages,
        "image": "r1k8sacrdev.azurecr.io/r1/prefect/prefect-flow:v0.0.3",
        "namespace": "r1-prefect",
        "service_account_name": "prefect-2-agent-svc",
        "image_pull_policy": "Always"
    })
dp.apply()