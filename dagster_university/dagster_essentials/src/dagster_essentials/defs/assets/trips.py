import requests
import dagster as dg
from dagster_essentials.defs.assets import constants

@dg.asset
def taxi_trips_file() -> None:
    """The raw parquet files for the taxi trips dataset. Sourced from NYC Open Data."""
    month_to_fetch = '2023-03'
    raw_data_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet'
    
    dg.get_dagster_logger().info(f'Fetching raw data from {raw_data_url}')
    
    raw_trips = requests.get(raw_data_url)

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), 'wb') as f:
        f.write(raw_trips.content)
