import logging
import dlt
from dlt.sources.helpers.rest_client import RESTClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://v6.bvg.transport.rest/"
STATIONS = ["900110007", "900140011"]
DURATION = 30
RESULTS_LIMIT = 50

# Initialize REST client
bvg_client = RESTClient(base_url=BASE_URL)

def fetch_transport_data(endpoint: str, table_name: str):
    """
    Fetches data from the BVG API for the given endpoint (departures or arrivals).
    
    Args:
        endpoint (str): API endpoint (e.g., "departures" or "arrivals").
        table_name (str): Table name for storing data.
        
    Yields:
        list: Processed transport data with station ID.
    """
    for station in STATIONS:
        try:
            response = bvg_client.get(
                f"stops/{station}/{endpoint}",
                params={"duration": DURATION, "results": RESULTS_LIMIT},
            )
            data = response.json().get(endpoint, [])
            
            # Add station ID to each entry
            for item in data:
                item["station_id"] = station
            
            yield data

        except Exception as e:
            logger.error(f"Error fetching {endpoint} for station {station}: {e}")

@dlt.resource(table_name="departures", write_disposition="append")
def get_departures():
    """Fetch departures from BVG API with incremental loading."""
    yield from fetch_transport_data("departures", "departures")

@dlt.resource(table_name="arrivals", write_disposition="append")
def get_arrivals():
    """Fetch arrivals from BVG API with incremental loading."""
    yield from fetch_transport_data("arrivals", "arrivals")

@dlt.source
def fetch_data():
    """Source function returning all resources for the pipeline."""
    return get_departures, get_arrivals

# Initialize and run the pipeline
pipeline = dlt.pipeline(
    pipeline_name="bvg_pipeline",
    destination="filesystem",
    dataset_name="bvg_dlt_pipeline"
)

if __name__ == "__main__":
    load_info = pipeline.run(fetch_data())
    logger.info(f"Pipeline run completed with load package: {load_info}")
