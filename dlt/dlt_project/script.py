import dlt
from dlt.sources.helpers.rest_client import RESTClient

bvg_client = RESTClient(base_url="https://v6.bvg.transport.rest/")

STATIONS = ["900110007", "900140011"]

@dlt.resource(table_name="departures", write_disposition="append")
def get_departures():
    for station in STATIONS:
        response = bvg_client.get(                              
            f"stops/{station}/departures",                          
            params={                                              
                "duration": 30,
                "results": 50
            }
        )
        departures = response.json().get('departures', [])
        for dep in departures:
            dep['station_id'] = station
        yield departures                                          

@dlt.resource(table_name="arrivals", write_disposition="append")
def get_arrivals():
    for station in STATIONS:
        response = bvg_client.get(                              
            f"stops/{station}/arrivals",                          
            params={                                              
                "duration": 30,
                "results": 50
            }
        )
        
        arrivals = response.json().get('arrivals', [])
        for arr in arrivals:
            arr['station_id'] = station
        yield arrivals    

@dlt.source
def fetch_data():
    return get_departures, get_arrivals


pipeline = dlt.pipeline(
    pipeline_name="bvg_pipeline",
    destination="filesystem",
    dataset_name="bvg_data_dlt_pipeline"
)

load_info = pipeline.run(fetch_data())

print(f"Pipeline run completed with load package: {load_info}")