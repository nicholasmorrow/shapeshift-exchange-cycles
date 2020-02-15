from collections import defaultdict
from requests.exceptions import HTTPError
import click
import datetime
import json
import requests
import sys


# class CoinGraph:
#     def __init__(self, exchange_pairs):
#         self.graph = {}
#         self.num_vertices = len(exchange_pairs)
#         for start, end, rate in exchange_pairs:
#             self.add_edge(start, end, rate)
#         print(f"Inserted {len(self.graph)} elements into CoinGraph.")
#         with open("./graph.json", "w") as f:
#             json.dump(self.graph, f, default=str, indent=2)

#     def add_edge(self, start, end, rate):
#         if start not in self.graph:
#             self.graph[start] = {}
#         self.graph[start][end] = rate

#     def get_adjacent_nodes(self, node):
#         if node not in self.graph:
#             return None
#         else:
#             return self.graph[node].items()

#     def get_all_nodes(self):
#         return self.graph.keys()


class CoinGraph:
    def __init__(self, exchange_pairs):
        self.graph = defaultdict(dict)
        self.num_vertices = len(exchange_pairs)
        self.Time = 0
        for start, end, rate in exchange_pairs:
            self.add_edge(start, end, rate)
        print(f"Inserted {len(self.graph)} nodes into CoinGraph.")
        with open("./graph.json", "w") as f:
            json.dump(self.graph, f, default=str, indent=2)

    def add_edge(self, start, end, rate):
        self.graph[start][end] = rate

    def get_adjacent_nodes(self, node):
        if node not in self.graph:
            return None
        else:
            return self.graph[node].items()

    def get_all_nodes(self):
        return self.graph.keys()

    def __dfs(self, v, visited):
        visited[v] = True
        # print(v, end="->") # Uncomment to  show DFS traversal path
        for node in self.graph[v]:
            if visited[node] == False:
                self.__dfs(node, visited)

    def dfs(self, startnode):
        visited = {}
        for node in self.graph.keys():
            visited[node] = False
        self.__dfs(startnode, visited)
        # print("") # Uncomment to show DFS traversal path
        return len(visited)

    def is_strongly_connected(self):
        num_nodes = len(self.graph.keys())
        for node in list(self.graph.keys()):
            if self.dfs(node) != num_nodes:
                print("Graph is not strongly connected.")
                return False
        print("Graph is strongly connected.")
        return True


def get_market_info(pair):
    try:
        marketinfo = requests.get(f"https://www.shapeshift.io/marketinfo/{pair}")
    except HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")

    try:
        marketinfo.json()["rate"]
    except KeyError as err:
        """ We don't have valid market information for this pair, so we need to 
        include a dummy entry so that the graph remains strongly connected. 
        With the rate set to 0.00, we can ensure that these nodes won't be involved
        in the list of profitable cycles. """
        marketinfo = {
            "pair": pair,
            "rate": 0.00,
            "minerFee": 0.0,
            "limit": 0.0,
            "minimum": 0.0,
            "maxLimit": 0.0,
        }
        # print(f"No market info available for pair {pair}")

        return marketinfo
    else:
        return marketinfo.json()


def get_exchange_pairs():
    """ Fetch a list of the currently trading exchange pairs from ShapeShift. """
    pairs = []
    timestamp = datetime.datetime.now()
    # Initialize dict to hold JSON data for save on read from ShapeShift API
    pairdata_json = {}
    pairdata_json["meta"] = {}
    pairdata_json["meta"]["timestamp"] = timestamp
    pairdata_json["meta"]["errors"] = []
    pairdata_json["data"] = []

    # Get a list of the valid conversion pairs
    try:
        pairdata = requests.get("https://www.shapeshift.io/validpairs")
    except HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")

    if pairdata.status_code != 200:
        print(f"Request unsuccessful. Returned code {pairdata.status_code}")

    # Get the market information for each valid pair in the list returned above
    with click.progressbar(
        pairdata.json(), label="Fetching current market data from ShapeShift:"
    ) as bar:
        for pair in bar:
            marketinfo = get_market_info(pair)
            pairs.append((pair.split("_")[0], pair.split("_")[1], marketinfo["rate"]))
            pairdata_json["data"].append(
                {
                    "from": pair.split("_")[0],
                    "to": pair.split("_")[1],
                    "market_info": marketinfo,
                }
            )
            if marketinfo["rate"] == 0.00:
                pairdata_json["meta"]["errors"].append(
                    f"No market info available for pair {pair}"
                )

    pairdata_json["meta"]["num_pairs"] = len(pairs)

    # Export JSON file so that we can reload the data quickly later.
    with open(f"./data/pairdata_{timestamp}.json", "w") as f:
        json.dump(pairdata_json, f, default=str, indent=2)
    print(f"{len(pairs)} exchange pairs fetched from ShapeShift.")
    # print(pairs)
    return pairs


def load_exchange_pairs(filename):
    """ Load a list of exchange pairs previously fetched from ShapeShift. """
    pairs = []
    with open(filename, "r") as f:
        pairdata_json = json.load(f)
        print(pairdata_json["meta"]["timestamp"])

    for pair in pairdata_json["data"]:
        pairs.append((pair["from"], pair["to"], pair["market_info"]["rate"]))

    if len(pairs) != pairdata_json["meta"]["num_pairs"]:
        raise LookupError(
            f"The number of pairs parsed from {filename} does not match the number of pairs recorded. "
        )
    print(f"{len(pairs)} exchange pairs loaded from file {filename}.")
    # print(pairs)
    return pairs


def get_current_coins():
    try:
        coins = requests.get("https://www.shapeshift.io/getcoins")
    except HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")

    if coins.status_code != 200:
        print(f"Request unsuccessful. Returned code {coins.status_code}")
    else:
        print(coins.json())

    return coins.json()


def is_strongly_connected():
    pass


def find_cycles(graph):
    cycles = []
    visited = []
    __find_cycles(graph, cycles, visited)


def __find_cycles(graph, cycles, visited):
    for node in graph:
        pass


@click.command()
@click.version_option(
    version=0.1,
    message="shapeshift-exchange-cycles 0.1\n\
Copyright (C) 2020 Nicholas Morrow\n\
\n\
Written by Nicholas Morrow <nickhudspeth@gmail.com> ",
)
@click.option(
    "--market-data",
    "-m",
    type=click.Path(),
    metavar="<marketdata>",
    help="Optional path to previously obtained market data in JSON format.",
)
@click.option(
    "--dry-run",
    "-d",
    default=False,
    show_default="false",
    is_flag=True,
    required=False,
    help="Analyze market data for profitable cycles without executing transactions.",
)
def main(market_data, dry_run):
    """
    Search cryptocurrency market data provided by ShapeShift to
    determine whether or not exchange cycles exist which allow for
    profits to be made through a sequence of currency conversions
    """
    # Get exchange data from ShapeShift API or local file
    if market_data is None:
        exchange_data = get_exchange_pairs()
    else:
        exchange_data = load_exchange_pairs(market_data)
    # Assemble directed graph from exchange data
    graph = CoinGraph(exchange_data)
    # Traverse graph using DFS from each node to verify that path is strongly connected.
    # If there is a path from each node to every other node, the graph is strongly connected and Johnson's algorithm can be used.
    if not graph.is_strongly_connected():
        sys.exit(0)
    # For each strongly connected component, use Johnson's algorithm to find all elementary cycles and append each cycle to a list
    # For each cycle in the list, remove the cycle if the product of the exchange rates across the cycle is less than 1.
    # Print the list of cycles


if __name__ == "__main__":
    main()