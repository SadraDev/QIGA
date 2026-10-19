import random
import json
import math
from heapq import heappop, heappush

# Constants
BASE_STATION_COUNT = 50
EDGE_SERVER_COUNT = 50
NETWORK_DELAY = 5
USER_COUNT = 190
AREA_SIZE = 100

def load_existing_data(filepath):
    with open(filepath, "r") as f:
        existing_data = json.load(f)
    return existing_data["NetworkSwitch"], existing_data["NetworkLink"], existing_data["BaseStation"], existing_data['EdgeServer']
# Load pre-existing data
network_switches, network_links, base_stations, edge_servers = load_existing_data("scheme/input/ES-50_ED-100.json")

for base_station in base_stations:
    base_station["relationships"]["users"] = []

# from edge_sim_py.dataset_generator.edge_servers import e5430, e5507, e5645, jetson_nano, jetson_tx2, raspberry_pi4
# edge_servers = []
# available_base_stations = random.sample(base_stations, EDGE_SERVER_COUNT)
# for i, base_station in enumerate(available_base_stations):
#     edge_server_model = random.choice([e5430(), e5507(), e5645(), jetson_nano(), jetson_tx2(), raspberry_pi4()])
#     base_station_id = base_station["attributes"]["id"]

#     edge_server = {
#         "attributes": {
#             "id": i + 1,  # Ensure unique edge server ID
#             "available": True,
#             "model_name": edge_server_model.model_name,
#             "cpu": edge_server_model.cpu,
#             "memory": edge_server_model.memory,
#             "disk": edge_server_model.disk,
#             "cpu_demand": 0,
#             "memory_demand": 0,
#             "disk_demand": 0,
#             "coordinates": base_station["attributes"]["coordinates"],
#             "max_concurrent_layer_downloads": 3,
#             "active": True,
#             "power_model_parameters": edge_server_model.power_model_parameters
#         },
#         "relationships": {
#             "power_model": "LinearServerPowerModel",
#             "base_station": {
#                 "class": "BaseStation",
#                 "id": base_station_id
#             },
#             "network_switch": {
#                 "class": "NetworkSwitch",
#                 "id": base_station_id
#             },
#             "services": [],
#             "container_layers": [],
#             "container_images": [],
#             "container_registries": []
#         }
#     }
    
#     edge_servers.append(edge_server)
#     # Assign the edge server to the selected base station
#     base_station["relationships"]["edge_servers"].append({
#         "class": "EdgeServer",
#         "id": i + 1
#     })

services = []
for service_id in range(1, 11):
    service_type = "computationally_intensive" if random.choice([True, False]) else "latency_sensitive"
    
    if service_type == "computationally_intensive":
        data_size = random.choice([2048, 4096])
        weight = random.choice([3990000000, 5320000000])
        deadline = random.choice([5, 6])
        memory_deamnd = 4096
    else:
        data_size = random.choice([4096, 8192])
        weight = random.choice([1330000000, 2660000000])
        deadline = random.choice([3, 5])
        memory_deamnd = 2048
    
    service = {
        "attributes": {
            "id": service_id,
            "label": f"Service_{service_id}",
            "state": 0,
            "_available": True,
            "cpu_demand": random.randint(1, 4),
            "weight": weight,
            "data_size": data_size,
            "deadline": deadline,
            "memory_demand": memory_deamnd,
            "image_digest": f"sha256:{''.join(random.choices('abcdef0123456789', k=64))}"
        },
        "relationships": {
            "application": {
                "class": "Application",
                "id": service_id
            },
            "server": {
                "class": "EdgeServer",
                "id": random.randint(1, EDGE_SERVER_COUNT)
            }
        }
    }
    services.append(service)

applications = []
for app_id in range(1, 11):
    application = {
        "attributes": {
            "id": app_id,
            "label": f"Application_{app_id}"
        },
        "relationships": {
            "services": [
                {
                    "class": "Service",
                    "id": app_id
                }
            ],
            "users": []
        }
    }
    applications.append(application)

def generate_random_waypoint_trace(start_x, start_y):
    trace = [[start_x, start_y]]
    current_x, current_y = start_x, start_y

    for _ in range(20):
        # Generate random destination
        dest_x = random.randint(0, AREA_SIZE)
        dest_y = random.randint(0, AREA_SIZE)
        
        # Calculate distance and travel time
        distance = math.sqrt((dest_x - current_x)**2 + (dest_y - current_y)**2)
        speed = random.uniform(1, 5)
        travel_time = max(int(distance / speed), 1)
        
        # Move towards destination in steps, recording position
        for _ in range(travel_time):
            if len(trace) >= 20:
                break
            
            if distance != 0:
                direction_x = (dest_x - current_x) / distance
                direction_y = (dest_y - current_y) / distance
            else:
                direction_x = 0
                direction_y = 0
            current_x += direction_x * speed
            current_y += direction_y * speed
            trace.append([int(current_x), int(current_y)])
        
        # Pause before choosing a new destination
        trace.extend([[int(current_x), int(current_y)]] * 2)
        current_x, current_y = int(current_x), int(current_y)

    return trace[:20]
users = []
for i in range(1, USER_COUNT + 1):
    x = random.randint(0, AREA_SIZE)
    y = random.randint(0, AREA_SIZE)
    base_station = random.choice(base_stations)
    base_station_id = base_station["attributes"]["id"]

    selected_application_id = random.choice(range(1, 11))

    user = {
        "attributes": {
            "id": i,
            "coordinates": [x, y],
            "coordinates_trace": generate_random_waypoint_trace(x, y),
            "delays": {str(i): random.randint(5, 20)},
            "delay_slas": {str(i): 45},
            "communication_paths": {str(i): [[random.randint(1, BASE_STATION_COUNT), random.randint(1, BASE_STATION_COUNT)]]},
            "making_requests": {str(i): {str(i): True}}
        },
        "relationships": {
            "access_patterns": {
                str(i): {
                    "class": "CircularDurationAndIntervalAccessPattern",
                    "id": i
                }
            },
            "mobility_model": "pathway",
            "applications": [
                {
                    "class": "Application",
                    "id": selected_application_id
                }
            ],
            "base_station": {
                "class": "BaseStation",
                "id": base_station_id
            }
        }
    }
    
    users.append(user)

    # Assign user to the selected application
    applications[selected_application_id - 1]["relationships"]["users"].append({
        "class": "User",
        "id": i
    })

    # Assign the user to the selected base station
    base_station["relationships"]["users"].append({
        "class": "User",
        "id": i
    })

# Access Patterns (for each user, random access to one of the applications)
circular_duration_and_interval_access_pattern = []
for i in range(1, USER_COUNT + 1):
    access_pattern = {
        "attributes": {
            "id": i,
            "duration_values": [
                float("inf")  # Represents Infinity
            ],
            "interval_values": [
                0
            ],
            "history": [
                {
                    "start": 1,
                    "end": float("inf"),
                    "duration": float("inf"),
                    "waiting_time": 0,
                    "access_time": 0,
                    "interval": 0,
                    "next_access": float("inf")
                }
            ]
        },
        "relationships": {
            "user": {
                "class": "User",
                "id": i
            },
            "app": {
                "class": "Application",
                "id": 1 if selected_application_id == 1 else 2  # Link to the assigned application
            }
        }
    }
    circular_duration_and_interval_access_pattern.append(access_pattern)

# Construct the final JSON data structure
output_data = {
    "NetworkSwitch": network_switches,
    "NetworkLink": network_links,
    "BaseStation": base_stations,
    "User" : users,
    "ContainerLayer": [],
    "ContainerImage": [],
    "Service": services,
    "ContainerRegistry": [],
    "Application": applications,
    "EdgeServer": edge_servers,
    "RandomDurationAndIntervalAccessPattern": [],
    "CircularDurationAndIntervalAccessPattern": circular_duration_and_interval_access_pattern
}

# # Write to a JSON file
with open(f"scheme/input/ES-{EDGE_SERVER_COUNT}_ED-{USER_COUNT}.json", "w") as outfile:
    json.dump(output_data, outfile, indent=4)

print("JSON data has been written to input.json")
