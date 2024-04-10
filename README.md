This repository contains two files, indicadores.py and IEEE123bus_grafo_completo.pickle.
The IEEE123bus_grafo_completo.pickle file contains the IEEE 123 bus test case modeled in a networkx graph that could be imported into other files.
The file indicadores.py contains:
  - an example of how to import the Graph from pickle (line 5)
  - A function to generate a test graph of a synthetic network (line 7)
  -  A function to retrieve the connection data from a graph that receives the graph object and the list of switches to be opened (line 36)
  -  Functions to calculate SAIDI and SAIFI (lines 68 and 71)
  -  A function for a test case to demonstrate the impacts of inserting switches on the synthetic network (line 74)
  -  A function that ranks each subgraph returning the list of subgraph nodes and the corresponding rank (line 93)
  -  A function that receives the Graph and the nodes of a subgraph (chosen by the rank) and returns the edge that is the best candidate to be a new switch (line 175)
  -  The two network models could be used to test and compare the performance with other algorithms. The provided functions could be used to test the proposed method with other networks in the same format.
