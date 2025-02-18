import argparse
import json
import networkx as nx
from graph import generateDrawings
import itertools
import math
import time

def greedy(graph):
    seen = 0
    adds=0
    sortededges = sorted(graph.edges(),key=lambda x:graph.edges[x]['weight'])
    sortededges_as_tuples = [(x,) for x in sortededges]
    edgeAsSet= set(graph.edges())
    states = sortededges_as_tuples[:]
    while True: #will always choose shortest length solution, could also choose best one if I used bisection.insort
        solution = states.pop(0)
        seen+=1
        captured_nodes = set()
        for edge in solution:#compute nodes we have attached to
            captured_nodes.add(edge[0])
            captured_nodes.add(edge[1])
            adds+=2
        
        missing_edges = edgeAsSet.difference(solution) #edges we must be adjacent to
        missing_edges_left = len(missing_edges) #supposedly faster than set remove function

        for edge in missing_edges:
            if edge[0] not in captured_nodes and edge[1] not in captured_nodes: #check for non-adjacency
                break
            missing_edges_left-=1

        if not missing_edges_left: #valid solution when missing_edges_left is 0
            break
        #there is no point adding cheaper edges as that state has already been added
        #there is no point adding edges that do not contribute new nodes
        most_costly_edge = solution[-1]
        states+=[solution + x for x in sortededges_as_tuples[sortededges.index(most_costly_edge)+1:] if x[0][0] not in captured_nodes or x[0][1] not in captured_nodes]

    for edge in solution:#just for graphic purposes
        graph.edges[edge]['color']="red"
    return graph,solution,seen,adds

def exhaustive(graph):
    seen = 0
    adds = 0
    best_cost = math.inf
    best_solution = None
    edgeAsSet= set(graph.edges())
    for x in range(1,len(graph.edges())+1):#all length possibilities
        for item in  itertools.combinations(graph.edges(),x):#all possible arrangements
            seen+=1
            total_weight = 0
            captured_nodes = set()

            for edge in item:
                captured_nodes.add(edge[0])
                captured_nodes.add(edge[1])
                adds+=2
                total_weight+=graph.edges[edge]['weight']
            
            if total_weight<best_cost:#is it actually worth checking whether this is a valid solution?
                missing_edges = edgeAsSet.difference(item)
                missing_edges_left = len(missing_edges)

                for edge in missing_edges:
                    if edge[0] not in captured_nodes and edge[1] not in captured_nodes:
                        break
                    missing_edges_left-=1

                if not missing_edges_left:
                    best_cost = total_weight
                    best_solution = item

    for edge in best_solution:#just for graphic purposes
        graph.edges[edge]['color']="red"
    return graph,best_solution,seen,adds


if __name__ =="__main__":
    parser= argparse.ArgumentParser()
    
    parser.add_argument("--input",help="input file",default="graph.json")
    parser.add_argument('--graph', dest='graph', action='store_true')
    parser.add_argument('--no-graph', dest='graph', action='store_false')
    parser.set_defaults(graph=True)
    parser.add_argument('--greedy', dest='strat', action='store_true')
    parser.add_argument('--exhaustive', dest='strat', action='store_false')
    parser.set_defaults(strat=True)

    args = parser.parse_args()

    f = open(args.input,"r")
    graphmap = json.loads(f.read())
    f.close()
    graph = nx.readwrite.node_link_graph(graphmap)

    if args.strat:
        timedelta = time.perf_counter()
        graph,solution,seen,adds = greedy(graph)
        timedelta = time.perf_counter() - timedelta
    else:
        timedelta = time.perf_counter()
        graph,solution,seen,adds = exhaustive(graph)
        timedelta = time.perf_counter() - timedelta

    solcost = sum(graph.edges[x]['weight'] for x in solution)
    print(f"{seen},{adds},{solcost},{timedelta}")
    if args.graph:
        generateDrawings(graph)
    