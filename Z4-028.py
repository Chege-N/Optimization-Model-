import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from scipy.optimize import linprog
%matplotlib inline
import warnings
warnings.filterwarnings('ignore')
fgbike=pd.read_csv('f759ed44774e3a63fedf8d5a3f47ac90_4a5934d4139fe3717c578b1e7f40242d_8.csv')

# Step 1: Preprocess the data to create a table of distances between bike stations
bike_stations = pd.read_csv('f759ed44774e3a63fedf8d5a3f47ac90_4a5934d4139fe3717c578b1e7f40242d_8.csv')
num_stations = len(bike_stations)
distances = np.zeros((num_stations, num_stations))
for i in range(num_stations):
    A_eq = np.zeros((2*num_stations, num_stations**2))
    A_eq[i, i*num_stations : (i+1)*num_stations] = 1
    A_eq[i+num_stations, i::num_stations] = 1
    A_eq[i+num_stations, i*num_stations : (i+1)*num_stations] = -1

    for j in range(num_stations):
        lat1, lon1 = bike_stations.iloc[i]['latitude'], bike_stations.iloc[i]['longitude']
        lat2, lon2 = bike_stations.iloc[j]['latitude'], bike_stations.iloc[j]['longitude']
        distances[i][j] = np.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

# Step 2: Read the weekly usage data and create a flow network
weekly_data = pd.read_csv('f759ed44774e3a63fedf8d5a3f47ac90_4a5934d4139fe3717c578b1e7f40242d_8.csv')
start_bikes = weekly_data.groupby('start_station_id').size().values
end_bikes = weekly_data.groupby('end_station_id').size().values
flow = end_bikes - start_bikes

# Step 3: Use linear programming to find the optimal flow and generate the recommended routes
c = distances.reshape(-1) # Flatten the distance matrix to a 1D array
A_eq = np.zeros((num_stations, num_stations**2)) # Equality constraint matrix
for i in range(num_stations):
    A_eq[i, i*num_stations : (i+1)*num_stations] = 1 # Each station has an inflow and outflow of 1
b_eq = flow # Equality constraint values
bounds = [(0, None) for _ in range(num_stations**2)] # Upper bound of infinity for flow
result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"presolve": False})

flows = result.x.reshape(num_stations, num_stations)
G = nx.DiGraph(flows)
routes = []

for i in range(num_stations):
    for j in range(num_stations):
        if i != j and G.has_edge(i, j):
            if nx.has_path(G, i, j):
                path = nx.shortest_path(G, i, j, weight='weight')
                for k in range(len(path)-1):
                    route = {'start_station': path[k], 'end_station': path[k+1]}
                    routes.append(route)
