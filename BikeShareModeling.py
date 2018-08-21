#PROJECT: MODELING TORONTO BIKESHARE NETWORK

#Notes: 

#station info JSON: https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information

#--------------------------------------------------#

#1) IMPORT LIBRARIES

#Computation and Structuring:

import pandas as pd
import json
from pandas.io.json import json_normalize

#Modeling:

import networkx as nx

#Visualization:

import matplotlib.pyplot as plt

#--------------------------------------------------#

#1) DATA IMPORT AND PREP

#First we load the node data from a JSON file containing all of the station's in the Toronto bike network:

#The JSON was in a deep embedded format and not working with Pandas read_json, so needed to take a more manual approach (i.e. can't use pd.read_json):

def unpack_json(filename):
    """function to unpack the JSON file format provided by the Toronto bikeshare network """
    
    with open(filename) as json_file:  
        inter_data = json.load(json_file)
    
    inter_data = json_normalize(inter_data['data'])
    inter_data = list(inter_data.values.flatten()) #creates a list of a list of dictionaries
    inter_data = inter_data[0] #unpacks so it is a list of dictionaries since all data data was in a list object at index[0]
    inter_data_df = pd.DataFrame(inter_data) #convert the list of dictionaires into a df, which is now properly formatted
    
    return inter_data_df

node_data_function = unpack_json('station_info.json') #gets information on station's and locations
node_data_final = node_data_function[['address','capacity','lat','lon','name','station_id']] #only keep relevant columns, this is our final cleaned node data set we can use to build the graph

#Now we load the edge data, which consists of an excel file with ride level data:

edge_data = pd.read_excel('2016_Bike_Share_Toronto_Ridership_Q4.xlsx')

#clean edge data and join to station id information from the node_data file:

def clean_edge_data(df1, df2):
    """cleans and reformats the edge data set so that node information is included"""
    
    edge_data_final = pd.merge(df1,df2[['name','station_id']].rename(columns={'name':'from_station_name'}),how='left',on='from_station_name') #add station_id from the node data to the trip level data 
    edge_data_final = edge_data_final.rename(columns={'station_id':'station_id_from'}) #rename station_id column
    edge_data_final = pd.merge(edge_data_final,df2[['name','station_id']].rename(columns={'name':'to_station_name'}),how='left',on='to_station_name') #add station_id from the node data to the trip level data 
    edge_data_final = edge_data_final.rename(columns={'station_id':'station_id_to'}) #rename station_id column
    edge_data_final = edge_data_final.dropna(subset=['station_id_to', 'station_id_from']) #drops edges where station id info is missing
    edge_data_final['station_id_from'] = pd.to_numeric(edge_data_final['station_id_from'],  downcast='integer') #match to format of station_id in node data set
    edge_data_final['station_id_to'] = pd.to_numeric(edge_data_final['station_id_to'],  downcast='integer') #match to format of station_id in node data set
    
    return edge_data_final

edge_data_final2 = clean_edge_data(edge_data, node_data_final) #creates final cleaned edge data set ready for creating the network

#--------------------------------------------------#

#2) Structure the Bikeshare network as a NetworkX Graph:

NG = nx.MultiDiGraph() #creates empty directed graph

#create nodes in the graph from station_id and give them a position that is equal to their lat-lon coordinates

for i, j, k in zip(node_data_final['station_id'], node_data_final['lon'], node_data_final['lat']):
    NG.add_node(i,pos=(j,k)) #iterates through the node data file to and 

pos= nx.get_node_attributes(NG, 'pos') #set position attribute for drawing
print(pos) #check the dictionary format is correct

#loop through the edge pairs and add to graph:
for i, j in zip(edge_data_final2['station_id_from'], edge_data_final2['station_id_to']):
    NG.add_edge(i,j) #iterates through edge_data and adds edges to the graph
    
#--------------------------------------------------#

#3) Analysis and Visualization: 
    
#Some high level stats for the network:
     
print('# of edges: {}'.format(NG.number_of_edges())) #~147k
print('# of nodes: {}'.format(NG.number_of_nodes())) #336 nodes, matches number of stations
print(NG.degree(node_data_final['station_id'])) #look at most important nodes in network
print(nx.in_degree_centrality(NG)) #computes the in-degree centrality for nodes in the directed network
print(nx.out_degree_centrality(NG)) #coputes the out-degree centrality for nodes in the directed network

#visualization of the network in physical space (using the lat-lon coordinate attributes):

plt.axis('off')
nx.draw(NG,pos,node_size=20,node_color='blue',alpha=0.5,width=0.5)


