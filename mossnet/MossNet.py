#! /usr/bin/env python
from gzip import open as gopen
from networkx import MultiDiGraph
from pickle import dump,load

class MossNet:
    def __init__(self, moss_results_dict):
        '''Create a ``MossNet`` object from a 3D dictionary of downloaded MOSS results

        Args:
            ``moss_results_dict`` (``dict``): A 3D dictionary of downloaded MOSS results

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
                        percent, html1, html2 = u_v_links[f]
                    except:
                        raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
                    self.graph.add_edge(u, v, attr_dict = {'file':f, 'percent':percent, 'html1':html1, 'html2':html2})

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
                    edge = u_v_edge_data[k]['attr_dict']; u_v_links[edge['file']] = (edge['percent'], edge['html1'], edge['html2'])
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
