from pickle import load
import networkx as nx
from math import inf

grafo = load(open('IEEE123bus_grafo_completo.pickle', 'rb'))

def  generate_test_graph():
    # Cria um grafo vazio
    G = nx.Graph()

    # List of nodes with parameters
    nodes = [(1, {'Ncustomers': 0, 'PW': 0, 'isSource': True}),
            (2, {'Ncustomers': 0, 'PW': 0, 'isSource': False}),
            (3, {'Ncustomers': 3, 'PW': 35, 'isSource': False}),
            (4, {'Ncustomers': 4, 'PW': 50, 'isSource': False}),
            (5, {'Ncustomers': 1, 'PW': 20, 'isSource': False}),
            (6, {'Ncustomers': 8, 'PW': 90, 'isSource': False}),
            (7, {'Ncustomers': 6, 'PW': 75, 'isSource': False})]

    # List of edges with parameters
    edges = [(1, 2, {'isSwitch': False}),
            (2, 3, {'isSwitch': True, 'name': 'ch1'}),
            (3, 4, {'isSwitch': False}),
            (4, 5, {'isSwitch': True, 'name': 'ch3'}),
            (2, 6, {'isSwitch': True, 'name': 'ch2'}),
            (6, 7, {'isSwitch': False}),
            (7, 5, {'isSwitch': True, 'name': 'ch4'})]

    # Add nodes and edges to the graph
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G



def get_connection_data(grafo:nx.MultiGraph, open_switches:list):
    graph_copy = grafo.copy()
    for switch in open_switches:
        graph_copy.remove_edge(switch[0],switch[1])
    subgraphs = [graph_copy.subgraph(c).copy() for c in nx.connected_components(graph_copy)]
    connected_ncustomers = 0
    connected_pw = 0
    disconnected_ncustomers = 0
    disconnected_pw = 0
    for graph in subgraphs:
        customers=0
        pw = 0
        connected:bool = False
        for node in graph.nodes(data=True):
            if node[1]['isSource'] is True:
                connected = True
            customers += node[1]['Ncustomers']
            pw += node[1]['PW']
        if connected:
            connected_ncustomers += customers
            connected_pw += pw
        else:
            disconnected_ncustomers += customers
            disconnected_pw += pw
    return {'connected_ncustomers':connected_ncustomers,'connected_pw':connected_pw,'disconnected_ncustomers':disconnected_ncustomers,'disconnected_pw':disconnected_pw}

def busca_no(nome, grafo):
    for no in grafo.nodes(data=True):
        if nome in no[1]['nodes']:
            return no[0]


def calc_saidi(connection_data:dict):
    return connection_data['disconnected_ncustomers']/connection_data['connected_ncustomers']

def calc_ens(connection_data:dict):
    return connection_data['disconnected_pw']/connection_data['connected_pw']

def caso_teste():
    print("Caso considerando obra que precise abrir CH2 e CH4")
    connection_data = get_connection_data(generate_test_graph(),[(2,6),(7,5)])
    print("SAIDI: ",calc_saidi(connection_data))
    print("ENS: ",calc_ens(connection_data))

    print("Considerando que foi colocada uma chave entre as barras 6 e 7 e a obra precisa desligar a barra 6")
    connection_data = get_connection_data(generate_test_graph(),[(2,6),(6,7)])
    print("SAIDI: ",calc_saidi(connection_data))
    print("ENS: ",calc_ens(connection_data))

    print("Considerando que foi colocada uma chave entre as barras 6 e 7 e a obra precisa desligar a barra 7")
    connection_data = get_connection_data(generate_test_graph(),[(6,7),(7,5)])
    print("SAIDI: ",calc_saidi(connection_data))
    print("ENS: ",calc_ens(connection_data))




def switch_placement_rank(G):
    G1 = G.copy()
    # Cria um novo grafo vazio
    G2 = nx.Graph()

    # Remove as arestas onde isSwitch = True
    edges_to_remove = []
    for edge in G1.edges(data=True):
        if edge[2]['isSwitch'] is True:
            edges_to_remove.append(edge)
    #G1.remove_edges_from(edges_to_remove)
    # Adaptação necessária por poder ser um MultiGraph (considerar a possibilidade de ter um key associado a cada aresta)
    for edge in edges_to_remove:
        G1.remove_edge(edge[0],edge[1])

    # Agrupa os nós que estão conectados criando novos nós para um novo grafo

    novos_nos = []

    subgrafos = [G1.subgraph(c).copy() for c in nx.connected_components(G1)]
    for subgrafo in subgrafos:
        name = '+'.join([str(node) for node in subgrafo.nodes()])
        total_customers = 0
        total_PW = 0
        isSource = False
        for node in subgrafo.nodes(data=True):
            total_customers += node[1]['Ncustomers']
            total_PW += node[1]['PW']
            if node[1]['isSource'] is True:
                isSource = True
        novos_nos.append(
            (name, {'Ncustomers': total_customers, 'PW': total_PW, 'isSource': isSource, 'nodes': list(subgrafo.nodes())}))

    for no in novos_nos:
        print(no)

    G2.add_nodes_from(novos_nos)


    novas_arestas = []
    for edge in G.edges(data=True):
        if edge[2]['isSwitch'] is True:
            no1 = busca_no(edge[0], G2)
            no2 = busca_no(edge[1], G2)
            novas_arestas.append((no1, no2, edge[2]))
    G2.add_edges_from(novas_arestas)


    G3 = G2.copy()

    # Calculate the network betweenness centrality
    bc = nx.betweenness_centrality(G3)
    normalized_number_of_customers = {}
    total_number_of_customers = 0
    for node in G3.nodes(data=True):
        total_number_of_customers += node[1]['Ncustomers']
    total_power = 0
    for node in G3.nodes(data=True):
        total_power += node[1]['PW']
    for node in G3.nodes(data=True):
        try:
            normalized_number_of_customers = node[1]['Ncustomers'] /  total_number_of_customers
        except ZeroDivisionError:
            normalized_number_of_customers = 0

        betweenness_centrality = bc[node[0]]
        try:
            normalized_power = node[1]['PW'] / total_power
        except ZeroDivisionError:
            normalized_power = 0
        ranking = normalized_number_of_customers +  betweenness_centrality + normalized_power
        G3.nodes[node[0]]['ranking'] = ranking

    lista_ranking = []
    for node in G3.nodes(data=True):
        lista_ranking.append((node[0], node[1]['ranking']))

    lista_ranking.sort(key=lambda x: x[1], reverse=True)
    return(lista_ranking)



def place_switch(graph:nx.Graph,group_node_string:str):
    node_names =  group_node_string.split('+')
    G = graph.subgraph(node_names).copy()
    aresta_escohida:tuple = None
    diferenca_aresta_escolhida:float=inf

    for edge in G.edges(data=True):
        G1 = G.copy()
        G1.remove_edge(edge[0],edge[1])
        total_customers = sum([node[1]['Ncustomers'] for node in G1.nodes(data=True)])
        total_power  = sum([node[1]['PW'] for node in G1.nodes(data=True)])
        subgraphs = [G1.subgraph(c).copy() for c in nx.connected_components(G1)]
        if len(subgraphs) > 1:
            diferenca_consumidores = abs(sum([node[1]['Ncustomers'] for node in subgraphs[0].nodes(data=True)])-sum([node[1]['Ncustomers'] for node in subgraphs[1].nodes(data=True)]))/total_customers
            diferenca_potencia = abs(sum([node[1]['PW'] for node in subgraphs[0].nodes(data=True)])-sum([node[1]['PW'] for node in subgraphs[1].nodes(data=True)]))/total_power
            diferenca = diferenca_consumidores + diferenca_potencia
            if diferenca < diferenca_aresta_escolhida:
                diferenca_aresta_escolhida = diferenca
                aresta_escohida = edge
    return aresta_escohida

