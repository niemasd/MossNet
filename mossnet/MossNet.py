#! /usr/bin/env python
from gzip import open as gopen
from networkx import MultiDiGraph
from pickle import load

class MossNet:
    def __init__(self, moss_results_dict):
        '''Create a ``MossNet`` object from a 2D dictionary of downloaded MOSS results

        Args:
            ``moss_results_dict`` (``dict``): A 2D dictionary of downloaded MOSS results

        Returns:
            ``MossNet``: A ``MossNet`` object
        '''
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
                        percent, html1, html2 = u_v_links[f]
                    except:
                        raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
                    self.graph.add_edge(u, v, attr_dict = {'file':f, 'percent':percent, 'html1':html1, 'html2':html2})
