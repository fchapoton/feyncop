
"""qed_gen.py: Implements functions to generate QED graphs. """

__author__ = "Michael Borinsky"
__email__ = "borinsky@physik.hu-berlin.de"



import itertools
from weighted_graph import WeightedGraph

import phi_k_gen

def gen_graphs( L, r_t2, m, cntd, edge2cntd, vtx2cntd, notadpoles ):
    """Generate QED graphs with the desired parameters and properties. 
        L: Loop number
        r_t2: Ext. fermion number
        m: Ext. boson number"""
    
    phi3_graphs = ( phi_k_gen.gen_graphs( L, 3, r_t2 + m, cntd, edge2cntd, vtx2cntd, notadpoles) )

    for g_phi3 in phi3_graphs:
        gen_qed_graphs = ( g.unlabeled_graph for g in gen_from_phi3_g( g_phi3, r_t2, m ) )

        qed_graphs = frozenset( gen_qed_graphs )

        for g in qed_graphs:
            yield g

def gen_from_phi3_g( fg, r_t2, m ):
    """Helper function: Generate full fledged QED graphs from the bulk output of 
        phi_k_gen.gen_graphs."""

    ext_vtcs = fg.external_vtcs_set
    int_vtcs = fg.internal_vtcs_set

    is_sl = [ fg.is_selfloop(edge) for e,edge in enumerate(fg.edges) ]
    ext_adj = [ frozenset(fg.adj_edges(v, fg.edges_set)) for v in ext_vtcs ]
    int_adj = [ frozenset(fg.adj_edges(v, fg.edges_set)) for v in int_vtcs ]
    for weights in itertools.product((1,2), repeat=len(fg.edges)):
        boson_edges = frozenset( e for e,w in enumerate(weights) if w == 2 )
        boson_adj = [ adj&boson_edges for adj in int_adj ]
        boson_valences = ( sum( 2 if is_sl[e] else 1 for e in adj ) for adj in boson_adj )
        if any( val != 1 for val in boson_valences ):
            continue

        fermion_edges = frozenset( e for e,w in enumerate(weights) if w == 1 )
        fermion_adj = [ adj&fermion_edges for adj in int_adj ]
        fermion_valences = ( sum( 2 if is_sl[e] else 1 for e in adj ) for adj in fermion_adj )
        if any( val != 2 for val in fermion_valences ):
            continue

        fermion_legs = sum( 1 for adj in ext_adj for e in adj if weights[e] == 1 )

        if fermion_legs != r_t2:
            continue

        boson_legs = sum( 1 for adj in ext_adj for e in adj if weights[e] == 2 )

        if boson_legs != m:
            continue

        for fermion_weights in itertools.product( (-1,1), repeat=len(fermion_edges)):
            dir_weights = list(weights)
            for i,e in enumerate(fermion_edges):
                dir_weights[e] = fermion_weights[i]
            
            def dir( e, v ):
                v1,v2 = fg.edges[e]
                return 1 if v1 == v else -1

            fermion_res = ( sum( 0 if is_sl[e] else dir(e,v)*dir_weights[e] for e in adj ) for v,adj in zip(int_vtcs,fermion_adj) )
            if any( res != 0 for res in fermion_res ):
                continue

            flip = lambda (v1,v2) : (v2,v1)
            edges = tuple( edge if w == 1 or w == 2 else flip(edge) for edge, w in zip(fg.edges, dir_weights) )
            translated_weights = tuple( 2 if w == 2 else 1 for w in weights )
            
            yield WeightedGraph( tuple(edges), tuple(translated_weights) )

