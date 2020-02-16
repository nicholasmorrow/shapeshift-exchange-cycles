import networkx as nx
from itertools import cycle

G = nx.DiGraph()

G.add_node("ATOM")
G.add_node("BTC")
G.add_node("BCH")
G.add_node("BNT")
G.add_node("BLK")
G.add_node("CVC")

G.add_edge("ATOM", "BTC")
G.add_edge("ATOM", "BCH")
G.add_edge("ATOM", "BNT")
G.add_edge("ATOM", "BLK")
G.add_edge("ATOM", "CVC")

G.add_edge("BTC", "ATOM")
G.add_edge("BCH", "ATOM")
G.add_edge("BNT", "ATOM")
G.add_edge("BLK", "ATOM")
G.add_edge("CVC", "ATOM")

G.add_edge("BTC", "CVC")

# print(list(nx.simple_cycles(G)))

path = ["ATOM", "BTC", "BCH", "BNT", "BLK"]

pool = cycle(path)
b = next(pool)
for i in path:
    c = next(pool)
    print(f"{b}_{c}")
    b = c
