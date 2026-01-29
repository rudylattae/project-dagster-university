import os
import duckdb
import requests
import dagster as dg
from dagster_essentials.defs.assets import constants
from dagster._utils.backoff import backoff


@dg.asset
def taxi_trips_file() -> None:
    """The raw parquet files for the taxi trips dataset. Sourced from NYC Open Data."""
    month_to_fetch = '2023-03'
    raw_data_url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet'
    
    dg.get_dagster_logger().info(f'Fetching raw data from {raw_data_url}')
    
    raw_trips = requests.get(raw_data_url)

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), 'wb') as f:
        f.write(raw_trips.content)


@dg.asset
def taxi_zones_file() -> None:
    """CSV of the distinct taxi zones in NYC. Sourced from NYC Open Data."""
    zones_data_url = 'https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv'
    
    dg.get_dagster_logger().info(f'Fetching taxi zones data from {zones_data_url}')
    
    zones_data = requests.get(zones_data_url)

    with open(constants.TAXI_ZONES_FILE_PATH, 'wb') as f:
        f.write(zones_data.content)


@dg.asset(
    deps=[taxi_trips_file],
)
def taxi_trips() -> None:
    """A DuckDB table containing the rawtaxi trips data."""
    month_to_fetch = '2023-03'
    raw_file_path = constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)
    query = f"""
        CREATE OR REPLACE TABLE taxi_trips AS (
            SELECT VendorID as vendor_id,
                PULocationID as pickup_zone_id,
                DOLocationID as dropoff_zone_id,
                RatecodeID as rate_code_id,
                payment_type as payment_type,
                tpep_dropoff_datetime as dropoff_datetime,
                tpep_pickup_datetime as pickup_datetime,
                trip_distance as trip_distance,
                passenger_count as passenger_count,
                total_amount as total_amount
        FROM '{raw_file_path}');
    """

    dg.get_dagster_logger().info(f'Loading raw data from {raw_file_path} into DuckDB table taxi_trips')

    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={'database': os.getenv('DUCKDB_DATABASE')},
        max_retries=10,
    )
    conn.execute(query)
