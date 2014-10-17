def show_network(sbml):
    '''
    Create a network diagram from a sbml model.
    
    sbml -- an SBML string, libsbml.SBMLDocument object, or libsbml.Model object
    
    '''
    import networkx as nx
    import libsbml
    
    if isinstance(sbml, basestring):
        doc = libsbml.readSBMLFromString(sbml)
        model = doc.getModel()
    elif isinstance(sbml, libsbml.SBMLDocument):
        doc = sbml
        model = doc.getModel()
    elif isinstance(sbml, libsbml.Model):
        model = sbml
    else:
        raise Exception('SBML Input is not valid')
    
    G = nx.DiGraph()
    labels = {}
    species = []
    reactions = []
    for i, s in enumerate(model.species):
        G.add_node(s.getId())
        species.append(s.getId())
    for i, r in enumerate(model.reactions):
        G.add_node(r.getId())
        reactions.append(r.getId())
        for s in r.reactants:
            G.add_edge(s.getSpecies(), r.getId(), kind='reactant')
        for s in r.products:
            G.add_edge(r.getId(), s.getSpecies(), kind='product')
        for s in r.modifiers:
            G.add_edge(s.getSpecies(), r.getId(), kind='modifier')
    
    modifier_edges = [key for key, val in nx.get_edge_attributes(G, 'kind').items() if val == 'modifier']
    product_edges = [key for key, val in nx.get_edge_attributes(G, 'kind').items() if val == 'product']
    reactant_edges = [key for key, val in nx.get_edge_attributes(G, 'kind').items() if val == 'reactant']
    #mass_transfer_edges = [key for key, val in nx.get_edge_attributes(G, 'kind').items() if val != 'modifier']
    
    import matplotlib.pyplot as plt
    
    # pos=nx.circular_layout(G)
    # pos=nx.shell_layout(G)
    # pos=nx.spring_layout(G)
    pos=nx.spectral_layout(G)
    
    nx.draw_networkx_nodes(G,pos,
                           nodelist=species,
                           node_color='r',
                           node_size=500,
                           alpha=0.8)
    nx.draw_networkx_edges(G, pos, edgelist=product_edges)
    nx.draw_networkx_edges(G, pos, edgelist=reactant_edges, arrows=False)
    nx.draw_networkx_edges(G, pos, edgelist=modifier_edges, style='dashed')
    
    labels = {}
    for n in G.nodes():
        if n in species:
            labels[n] = n
    nx.draw_networkx_labels(G,pos,labels,font_size=16)
    plt.axis('off')
    plt.show()