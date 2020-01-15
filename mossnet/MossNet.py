#! /usr/bin/env python
from gzip import open as gopen
from networkx import MultiDiGraph
from pickle import dump,load
from scipy.stats import binom

class MossNet:
    def __init__(self, moss_results_dict, num_students=None):
        '''Create a ``MossNet`` object from a 3D dictionary of downloaded MOSS results

        Args:
            ``moss_results_dict`` (``dict``): A 3D dictionary of downloaded MOSS results

            ``num_students`` (``int``): The true number of students, including the ones not in the MOSS results. ``None`` means infer from graph

        Returns:
            ``MossNet``: A ``MossNet`` object
        '''
        if isinstance(moss_results_dict, MultiDiGraph):
            self.graph = moss_results_dict; return
        if isinstance(moss_results_dict, str):
            try:
                if moss_results_dict.lower().endswith('.gz'):
                    moss_results_dict = load(gopen(moss_results_dict))
                else:
                    moss_results_dict = load(open(moss_results_dict,'rb'))
            except:
                raise ValueError("Unable to load dictionary: %s" % moss_results_dict)
        if not isinstance(moss_results_dict, dict):
            raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
        self.graph = MultiDiGraph()
        for u in moss_results_dict:
            u_edges = moss_results_dict[u]
            if not isinstance(u_edges, dict):
                raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
            for v in u_edges:
                u_v_links = u_edges[v]
                if not isinstance(u_edges[v], dict):
                    raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
                for f in u_v_links:
                    try:
                        left, right = u_v_links[f]
                    except:
                        raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
                    self.graph.add_edge(u, v, attr_dict = {'file':f, 'left':left, 'right':right})
        if num_students is None:
            self.num_students_val = self.num_nodes()
        elif num_students < len(self.num_nodes()):
            raise ValueError("num_students must be >= the number of nodes in the MOSS results")
        else:
            self.num_students_val = num_students

    def save(self, outfile):
        '''Save this ``MossNet`` object as a 3D dictionary of MOSS results

        Args:
            ``outfile`` (``str``): The desired output file's path
        '''
        out = dict()
        for u in self.graph.nodes:
            u_edges = dict(); out[u] = u_edges
            for v in self.graph.neighbors(u):
                u_v_links = dict(); u_edges[v] = u_v_links; u_v_edge_data = self.graph.get_edge_data(u,v)
                for k in u_v_edge_data:
                    edge = u_v_edge_data[k]['attr_dict']; u_v_links[edge['file']] = (edge['left'], edge['right'])
        if outfile.lower().endswith('.gz'):
            f = gopen(outfile, mode='wb', compresslevel=9)
        else:
            f = open(outfile, 'wb')
        dump(out, f); f.close()

    def get_networkx(self):
        '''Return a NetworkX ``MultiDiGraph`` equivalent to this ``MossNet`` object

        Returns:
            ``MultiDiGraph``: A NetworkX ``DiGraph`` equivalent to this ``MossNet`` object
        '''
        return self.graph.copy()

    def get_nodes(self):
        '''Returns a ``set`` of node labels in this ``MossNet`` object

        Returns:
            ``set``: The node labels in this ``MossNet`` object
        '''
        return set(self.graph.nodes)

    def num_nodes(self):
        '''Returns the number of nodes in this ``MossNet`` object

        Returns:
            ``int``: The number of nodes in this ``MossNet`` object
        '''
        return self.graph.number_of_nodes()

    def num_students(self):
        '''Returns the number of students in this ``MossNet`` object (equal to ``num_nodes`` unless user specified larger number of students)

        Returns:
            ``int``: The number of students in this ``MossNet`` object
        '''
        return self.num_students_val
    
    def num_edges(self):
        '''Returns the number of (undirected) edges in this ``MossNet`` object (including parallel edges)

        Returns:
            ``int``: The number of (undirected) edges in this ``MossNet`` object (including parallel edges)
        '''
        return int(self.graph.number_of_edges()/2)
