# Standard library modules
import os
import time

# Third party modules
import requests
from dagster import MetadataValue, OpExecutionContext, asset

SCHEDULE_NAME = "daily run"

safe_schedule_name = SCHEDULE_NAME.replace(" ", "_")
url = os.getenv("URL")
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": os.getenv("X-API-KEY"),
    "X-API-SECRET": os.getenv("X-API-SECRET"),
}


def _extract_gql_response(request: requests.Response, query_name: str, field: str) -> str:
    response_json = request.json()
    if "errors" in response_json:
        raise Exception(f"{response_json['errors']}")

    try:
        return response_json["data"][query_name][field]
    except (TypeError, KeyError) as e:
        raise ValueError(f"{e}: {response_json}")


def get_run_status(run_id: int):
    query = """
    query Status($runId: Int!) {
      boltRunStatus(runId: $runId) {
        state
      }
    }
    """
    response = requests.post(
        url, json={"query": query, "variables": {"runId": int(run_id)}}, headers=headers
    )
    state = _extract_gql_response(response, "boltRunStatus", "state")
    print(state)

    if state == "FAILED":
        raise Exception(f"Run {run_id} failed")
    elif state == "ERROR":
        raise Exception(f"Run {run_id} has error(s)")

    return state != "RUNNING"


@asset(group_name="paradime", compute_kind="Bolt API")
def bolt_schedule_run_id() -> bool:
    """
    Trigger a Bolt Schedule run

    API Docs: https://app.paradime.io/help/bolt-api
    """
    query = """
    mutation trigger($scheduleName: String!) {
      triggerBoltRun(scheduleName: $scheduleName){
        runId
      }
    }
    """
    response = requests.post(
        url,
        json={"query": query, "variables": {"scheduleName": safe_schedule_name}},
        headers=headers,
    )
    run_id = _extract_gql_response(response, "triggerBoltRun", "runId")
    while True:
        run_status = get_run_status(run_id=run_id)
        if run_status:
            break
        time.sleep(30)

    return run_status
