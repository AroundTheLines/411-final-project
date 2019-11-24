from collections import namedtuple
from typing import Tuple, List


ALL_PATHS = set()

class Place(object):
    def __init__(self, name, utility, cost, time):
        self.name = name
        self.utility = utility
        self.cost = cost
        self.time = time
        self.paths = []

    def __repr__(self):
        return "<Place {}, {} Paths>".format(
            self.name, len(self.paths),
        )


class Path(object):
    def __init__(self, origin, destination, time, utility):
        self.origin = origin
        self.destination = destination
        self.time = time
        self.utility = utility
    
    def __repr__(self):
        return "<Path from {} to {}>".format(
            self.origin, self.destination,
        )

class Route(object):
    def __init__(self, history=[], utility=0, budget_remaining=0):
        self.history = history
        self.utility = utility
        self.budget_remaining = budget_remaining


def generate_places(problem_def: dict):
    """
    Sample place definition = {
        "places": {
            "Paris": {
                time: 2, # days
                cost: 300,
                utility: 4,
            },
            "Berlin": {
                time: 3,
                cost: 350,
                utility: 10,

            },
            "Venice": {
                time: 1,
                cost: 200,
                utility: 6,
            },
        },
        "paths": [
            {
                "city 1": "Paris",
                "city 2": "Berlin",
                "time": 0.5,
                "utility": 4,
            },
            {
                "city 1": "Paris",
                "city 2": "Venice",
                "time": 1,
                "utility": 1,
            },
            {
                "city 1": "Berlin",
                "city 2": "Venice",
                "time": 0.25,
                "utility": 2,
            },
        ]
    }
    """
    all_places = {}
    for name, defn in problem_def['places'].items():
        all_places[name] = Place(name, defn["utility"], defn["cost"], defn["time"])
    
    for path in problem_def['paths']:
        assert path["city 1"] in all_places
        assert path["city 2"] in all_places
        all_places[path["city 1"]].paths.append(
            Path(
                all_places[path["city 1"]], 
                all_places[path["city 2"]], 
                path["time"], 
                path["utility"]
            )
        )
        all_places[path["city 2"]].paths.append(
            Path(
                all_places[path["city 2"]], 
                all_places[path["city 1"]], 
                path["time"], 
                path["utility"]
            )
        )

    return all_places


def find_max_util(
    cur_place: Place,
    budget_remaining: int,
    time_remaining: float,
    best_route: Route, # need to define type for this
    route: Route,
    cost_per_day_in_transit,
):
    # TODO: if starting city time > time remaining figure it out
    # each place has a list of paths available to it (from its perspective)
    
    route.history.append(cur_place)
    route.budget_remaining = budget_remaining
    route.utility += cur_place.utility
    ALL_PATHS.add(tuple([tuple(route.history), route.utility, route.budget_remaining]))

    path_list = generate_next_path_list(cur_place, budget_remaining, time_remaining, route, cost_per_day_in_transit)
    print("budget", budget_remaining, "paths_available", len(path_list))
    if len(path_list) == 0:
        return compare_routes(route, best_route)
    
    for path in path_list:
        new_route = Route([h for h in route.history], route.utility)
        new_route.history.append(path)
        new_route.utility = route.utility + path.utility
        finished_route = find_max_util(
            path.destination, 
            budget_remaining - path.time * cost_per_day_in_transit - path.destination.cost,
            time_remaining - path.time - path.destination.time,
            best_route,
            new_route,
            cost_per_day_in_transit
        )
        best_route = compare_routes(finished_route, best_route)
    
    return best_route


def generate_next_path_list(
    cur_place,
    budget_remaining,
    time_remaining,
    route,
    cost_per_day_in_transit,
):
    available_paths = []
    for path in cur_place.paths:
        print(path.destination, budget_remaining)
        if path.destination in route.history:
            continue
        if (path.time * cost_per_day_in_transit + path.destination.cost) >= budget_remaining:
            print("cutting out location", path.destination, budget_remaining, path.time * cost_per_day_in_transit + path.destination.cost, budget_remaining - (path.time * cost_per_day_in_transit + path.destination.cost))
            continue
        # lumping in path and destination time together for now
        # can separate this out later
        if path.time + path.destination.time >= time_remaining:
            continue
        available_paths.append(path)
    
    # return unsorted list
    return available_paths

def compare_routes(route_1, route_2):
    if route_1.utility == route_2.utility:
        return route_1 if route_1.budget_remaining > route_2.budget_remaining else route_2
    return route_1 if route_1.utility > route_2.utility else route_2


if __name__ == "__main__":
    sample_defn = {
        "places": {
            "Paris": {
                "time": 2, # days
                "cost": 300,
                "utility": 4,
            },
            "Berlin": {
                "time": 3,
                "cost": 350,
                "utility": 10,

            },
            "Venice": {
                "time": 1,
                "cost": 200,
                "utility": 6,
            },
            "Atlantis": {
                "time": 2,
                "cost": 150,
                "utility": 8,
            }
        },
        "paths": [
            {
                "city 1": "Paris",
                "city 2": "Berlin",
                "time": 0.5,
                "utility": 4,
            },
            {
                "city 1": "Paris",
                "city 2": "Venice",
                "time": 1,
                "utility": 1,
            },
            {
                "city 1": "Berlin",
                "city 2": "Venice",
                "time": 0.25,
                "utility": 2,
            },
            {
                "city 1": "Paris",
                "city 2": "Atlantis",
                "time": 1,
                "utility": 3,
            },
            {
                "city 1": "Berlin",
                "city 2": "Atlantis",
                "time": 2,
                "utility": 2,
            },
            {
                "city 1": "Venice",
                "city 2": "Atlantis",
                "time": 0.75,
                "utility": 5,
            },
        ]
    }

    budget = 700
    days_available = 14
    all_places = generate_places(sample_defn)
    cur_place = all_places["Paris"]
    from pprint import pprint
    pprint(cur_place)
    pprint(cur_place.paths)
    result = find_max_util(cur_place, budget, days_available, Route(), Route(), 100)
    print("result")
    # pprint(result)
    pprint(result.history)
    # print("all paths")
    # pprint(ALL_PATHS)

