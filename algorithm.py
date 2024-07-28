from typing import List, Union
import math


class Graph:
    def __init__(self, vertices: int) -> None:
        """
        Description: The constructor of the Graph

        - Saves the number of Nodes required for the sketching of the graph
        - Create a matrix for each Node to store the adjacent Nodes
        - Create a list to store whether each person is assigned.

        Args:
            - vertices: The number of vertex in the graph

        Return nothing
        """
        self.no_vertex = vertices
        self.adj = [[0] * vertices for _ in range(vertices)]

    def add_edge(self, from_node: int, to_node: int, lower_bound: int, capacity: int) -> None:
        """
        Description:
            -This function adds an edge from u to v and a backwards edge (residual) from v to u into the graph
            - It also stores the lower bound & capacity of the edge
            - It then adds the edges into the adjacent edge list (self.adj)

        Args:
            - u: the Node that is directed from
            - v: the Node that is directed to
            - lower_bound: the lower bound of the edge
            - capacity: the upper bound (capacity) of the edge


        Returns nothing
        """
        self.adj[from_node][to_node] = [to_node, lower_bound, capacity, 0] # The forward edge
        self.adj[to_node][from_node] = [from_node, -lower_bound, capacity, capacity]   # The backwards edge

    def get_augmented_path(self, source: int, sink: int, trace: list) -> bool:
        """
        Description:
            - The Breath First Search Algorithm
            - Augments the shortest path from the source to sink
            - Updates the 'trace' list to trace the path

        Args:
            :param source: the index of the source node
            :param sink: the index of the sink node
            :param trace: a list to store the path, allowing the tracing of path

        Returns a boolean on whether the sink is found/ whether there is an available path
        """
        visited = [False] * self.no_vertex
        queue = []
        queue.append(source)
        visited[source] = True

        while queue:
            u = queue.pop(0)

            for i in range(self.no_vertex):
                if self.adj[u][i] != 0:
                    v, lower_bound, capacity, flow = self.adj[u][i]

                    if (not visited[v] and capacity - flow > 0):
                        queue.append(v)
                        trace[v] = u
                        visited[v] = True

        return visited[sink]

    def ford_fulkerson(self, source: int, sink: int) -> int:
        """"
        Description:
            - The Ford Fulkerson Algorithm
            - Allocates people (and drivers) into the correct cars to maximize the flow
            - Paired with BFS: the Edmond Karp's Algorithm

        Args:
            - source: The index of the source
            - sink: The index of the sink

        Return:
            An int of the max flow
        """
        trace = [-3] * self.no_vertex
        max_flow = 0

        while self.get_augmented_path(source, sink, trace):
            curr_flow = float('inf')
            s = sink

            while s != source:
                curr_flow = min(curr_flow, self.adj[trace[s]][s][2])
                s = trace[s]

            v = sink
            while v != source:
                u = trace[v]
                self.adj[u][v][3] += curr_flow
                self.adj[v][u][3] -= curr_flow
                v = trace[v]

            max_flow += curr_flow

        return max_flow

def backtrack(g: Graph,no_car: int, no_friend: int, car_index:list, car_diff: int) -> list:
    """
    Description:
        - This function traces all the flows from the person to the car/destination
        - Assigns each person into the allocated car

    Args:
        :param g: the Graph object
        :param no_car: the number of cars/destination
        :param no_friend: the number of people going to the trip
        :param car_index: the list to store the cars linked to the intermediate mode
        :param car_diff: the index of the first car

    :return:
        - A list of cars with people allocated in it
    """
    allocation = [[] for _ in range(no_car)]
    persons_assigned = [False] * no_friend

    for person in range(no_friend):
        for edge in g.adj[person]:
            if edge != 0 and edge[0] < g.no_vertex - 2 and edge[3] > 0:
                if persons_assigned[person] is False:
                    allocation[car_index[edge[0]]-car_diff].append(person)
                    persons_assigned[person] = True

    return allocation

def allocate(preferences : list, licenses:list) -> Union[None, list]:
    """
    Description:
        -This function allocates people into cars such that it satisfy the constraints
            - Each car must have at least 2 drivers
            - Each car have 5 people max
            - The number of cars must be kept to a minimum
            - People can only be allocated to the cars of their preference

    Approach:
        - Use Circulation with Demands with lower bounds to solve the issue & Ford Fulkerson Algorithm.
        - Create a graph with appropriate Vertices
            - Source & Sink
            - n number of people vertices
            - ceil(n/5) number of car vertices
            - 2 * ceil(n/5) number of 'with license' & 'no license' intermediate vertices. 2 intermediate vertices for each car
        - Add appropriate edges to the graph with constraints
            -Source to people
            -people to intermediate vertices
            -intermediate vertices to cars
            -cars to sink
        - Using Ford-Fulkerson algorithm with BFS (Edmond-Karp algorithm) in attempt to allocate all people into the cars
        - If max-flow is less than the total number of people,
            - Add an extra edge for each car's intermediate nodes
                - where the edge goes from 'with license' to 'no license'
            - Run FordFulkerson once more
                - This allows people with license to go into preferred cars with already 2 drivers (if there is extra space in the car) in the event where there are more people with licenses than required.
        - If max-flow < number of people for the 2nd time,
            - Means no solution
        - Allocate people into the car using backtrack() function

    Args:
        :param preferences: a list of people with their respective preferences of destination (car) in a list
        :param licenses: a list of int which denote which person has a driving license

    :return:
        - A list of cars with people allocated in it, if a solution exists
        - None if no solution exists
 """
    no_friend = len(preferences)
    no_car = math.ceil(no_friend / 5)  # Number of destinations/cars

    # 1) Modify each person's preference such that it includes a boolean on whether they have a driver license or not;
    for i in range(len(preferences)):
        if len(preferences[i]) == 0 or len(preferences[i]) > no_car:
            return None
        else:
            if i in licenses:
                preferences[i] = (preferences[i], i, True)
            else:
                preferences[i] = (preferences[i], i, False)


    # Check if it's impossible to allocate due to insufficient drivers
    if len(licenses) < 2 * no_car:
        return None

    source = no_car + no_friend + (no_car * 2)
    sink = no_car + no_friend + (no_car * 2) + 1

    # Initialize a graph;
    g = Graph(no_car + no_friend + (no_car * 2) + 2)

    # 2) Add edges from source to people
    for person in range(no_friend):
        g.add_edge(source, person, 1, 1)

    reference = [-1] * no_friend

    # 3) Add edge from people to intermediate vertices ("with license" or "no license")
    for i in range(no_friend):
        tup = preferences[i]
        dest_list, index, driver = tup
        for dest in dest_list:
            if driver:
                g.add_edge(i, no_friend + 2 * dest, 0, 1)
            else:
                g.add_edge(i, no_friend + 2 * dest + 1, 0, 1)

            reference[i] = index

    index_diff = g.no_vertex - no_car - 2
    car_index = [None] * (no_friend + 3 * no_car)
    car_diff = []

    # 4) Add edge from the 2 intermediate vertices ("with license" / "no license") of each car to that respective car;
    for license in range(no_friend, g.no_vertex - no_car - 2, 2):
        g.add_edge(license, index_diff, 2, 2)
        g.add_edge(license + 1, index_diff, 0, 3)
        car_index[license] = index_diff
        car_index[license+1] = index_diff
        index_diff += 1



    # Add edges from destinations to sink
    for dest in range(g.no_vertex - no_car - 2, g.no_vertex - 2):
        g.add_edge(dest, sink, 2, 5)
        car_diff.append(dest)



    # Run Ford Fulkerson
    max_flow_value = g.ford_fulkerson(source, sink)

    # Check if the max flow is achieved;
    if max_flow_value != no_friend:
        for i in range(no_friend , source - no_car, 2):     # Add edges between the intermediate node of each car;
            g.add_edge(i, i+1, 0, 3)
        add_flow_value = g.ford_fulkerson(source, sink)      # Run Ford Fulkerson the 2nd time;
        max_flow_value += add_flow_value

    if max_flow_value != no_friend:
        return None

    # Allocate the people into their respective assigned cars
    allocation = backtrack(g, no_car,no_friend,car_index, car_diff[0])

    # Check if all cars have at least two person and whether there are 2 drivers in the car
    for car in allocation:
        if len(car) < 2:
            return None

        count = 0
        for i in range(len(car)):
            if car[i] in licenses:
                count += 1

        if count < 2:
            return None

    return allocation

