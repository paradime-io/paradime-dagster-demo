from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_package_module,
)

from . import assets

SCHEDULE_INTERVAL = "@daily"

bolt_schedule = ScheduleDefinition(
    job=define_asset_job(name="bolt_assets_job"), cron_schedule=SCHEDULE_INTERVAL
)

defs = Definitions(
    assets=load_assets_from_package_module(assets), schedules=[bolt_schedule]
)
