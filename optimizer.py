from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

def calculate_distance(coord1, coord2):
    """
    Calculate distance between two coordinates in meters
    using Haversine formula (real geographic distance)
    """
    R = 6371000  # Earth radius in meters
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return int(R * c)


def build_distance_matrix(locations):
    """
    Build full distance matrix between all locations
    locations = list of (lat, lng) tuples
    """
    size = len(locations)
    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(0)
            else:
                row.append(calculate_distance(locations[i], locations[j]))
        matrix.append(row)
    return matrix


def optimize_route(bins, threshold=70):
    """
    Takes list of bin dicts, returns optimized collection route
    Only includes bins above threshold fill level
    
    bins = [
        {"id": 1, "name": "Bin A", "latitude": 28.57, "longitude": 77.32, "fill_level": 85},
        ...
    ]
    """
    # Depot = municipal office in Noida (Sector 6)
    depot = {"name": "Depot (Municipal Office)", "latitude": 28.5706, "longitude": 77.3219}

    # Filter bins that need collection
    priority_bins = [b for b in bins if b["fill_level"] >= threshold]

    if not priority_bins:
        return {
            "status": "NO_COLLECTION_NEEDED",
            "message": f"All bins below {threshold}% — no collection needed",
            "route": [],
            "total_distance_km": 0
        }

    # Build location list — depot first
    all_locations = [depot] + priority_bins
    coords = [(loc["latitude"], loc["longitude"]) for loc in all_locations]

    # Build distance matrix
    distance_matrix = build_distance_matrix(coords)

    # OR-Tools setup
    manager = pywrapcp.RoutingIndexManager(len(coords), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Search parameters
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = 5

    # Solve
    solution = routing.SolveWithParameters(search_params)

    if not solution:
        return {
            "status": "NO_SOLUTION",
            "message": "Could not find optimal route",
            "route": [],
            "total_distance_km": 0
        }

    # Extract route
    route = []
    total_distance = 0
    index = routing.Start(0)

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        location = all_locations[node]
        route.append({
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "fill_level": location.get("fill_level", None)
        })
        next_index = solution.Value(routing.NextVar(index))
        total_distance += distance_matrix[manager.IndexToNode(index)][manager.IndexToNode(next_index)]
        index = next_index

    # Add depot at end (return journey)
    route.append({
        "name": depot["name"],
        "latitude": depot["latitude"],
        "longitude": depot["longitude"],
        "fill_level": None
    })

    return {
        "status": "SUCCESS",
        "message": f"Optimal route calculated for {len(priority_bins)} bins",
        "total_bins_in_route": len(priority_bins),
        "route": route,
        "total_distance_km": round(total_distance / 1000, 2)
    }