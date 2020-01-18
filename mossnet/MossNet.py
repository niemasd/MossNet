#! /usr/bin/env python
from gzip import open as gopen
from networkx import MultiDiGraph
from os import makedirs
from os.path import isdir,isfile
from pickle import dump as pkldump
from pickle import load as pklload
from scipy.stats import binom

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
                        left, right = u_v_links[f]
                    except:
                        raise TypeError("moss_results_dict must be a 3D dictionary of MOSS results")
                    self.graph.add_edge(u, v, attr_dict = {'file':f, 'left':left, 'right':right})

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
        pkldump(out, f); f.close()

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

    def get_pair(self, u, v, style='tuples'):
        '''Returns the links between nodes ``u`` and ``v``

        Args:
            ``u`` (``str``): A node label

            ``v`` (``str``): A node label not equal to ``u``

            ``style`` (``str``): The representation of a given link

            * ``"tuples"``: Links are ``((u_percent, u_html), (v_percent, v_html))`` tuples

            * ``"html"``: Links are HTML representation (one HTML for all links)

            * ``"htmls"``: Links are HTML representations (one HTML per link)

        Returns:
            ``dict``: The links between ``u`` and ``v`` (keys are filenames)
        '''
        if style not in {'tuples', 'html', 'htmls'}:
            raise ValueError("Invalid link style: %s" % style)
        if u == v:
            raise ValueError("u and v cannot be equal: %s" % u)
        for node in [u,v]:
            if not self.graph.has_node(node):
                raise ValueError("Nonexistant node: %s" % node)
        links = self.graph.get_edge_data(u,v)
        out = dict()
        for k in sorted(links.keys(), key=lambda x: links[x]['attr_dict']['file']):
            d = links[k]['attr_dict']
            filename = d['file']
            u_percent, u_html = d['left']
            v_percent, v_html = d['right']
            if style == 'tuples':
                out[filename] = ((u_percent, u_html), (v_percent, v_html))
            elif style in {'html', 'htmls'}:
                out[filename] = '<html><table style="width:100%%" border="1"><tr><td colspan="2"><center><b>%s</b></center></td></tr><tr><td>%s (%d%%)</td><td>%s (%d%%)</td></tr><tr><td><pre>%s</pre></td><td><pre>%s</pre></td></tr></table></html>' % (filename, u, u_percent, v, v_percent, u_html, v_html)
        if style == 'html':
            out = '<html>' + '<br>'.join(out[filename].replace('<html>','').replace('</html>','') for filename in sorted(out.keys())) + '</html>'
        return out

    def num_links(self, u, v):
        '''Returns the number of links between ``u`` and ``v``

        Args:
            ``u`` (``str``):

            ``v`` (``str``):

        Returns:
            ``int``: The number of links between ``u`` and ``v``
        '''
        for node in [u,v]:
            if not self.graph.has_node(node):
                raise ValueError("Nonexistant node: %s" % node)
        return len(self.graph.get_edge_data(u,v))

    def num_nodes(self):
        '''Returns the number of nodes in this ``MossNet`` object

        Returns:
            ``int``: The number of nodes in this ``MossNet`` object
        '''
        return self.graph.number_of_nodes()

    def num_edges(self):
        '''Returns the number of (undirected) edges in this ``MossNet`` object (including parallel edges)

        Returns:
            ``int``: The number of (undirected) edges in this ``MossNet`` object (including parallel edges)
        '''
        return int(self.graph.number_of_edges()/2)

    def traverse_pairs(self, order='descending'):
        '''Iterate over student pairs

        Args:
            ``order`` (``str``): Order to sort pairs in iteration

            * ``None`` to not sort (may be faster for large/dense graphs)

            * ``"ascending"`` to sort in ascending order of number of links

            * ``"descending"`` to sort in descending order of number of links
        '''
        if order not in {None, 'None', 'none', 'ascending', 'descending'}:
            raise ValueError("Invalid order: %s" % order)
        nodes = list(self.graph.nodes)
        pairs = [(u,v) for u in self.graph.nodes for v in self.graph.neighbors(u) if u < v]
        if order == 'ascending':
            pairs.sort(key=lambda x: len(self.graph.get_edge_data(x[0],x[1])))
        elif order == 'descending':
            pairs.sort(key=lambda x: len(self.graph.get_edge_data(x[0],x[1])), reverse=True)
        for pair in pairs:
            yield pair

    def export(self, outpath, style='html', verbose=False):
        '''Export the links in this ``MossNet`` in the specified style

        Args:
            ``outpath`` (``str``): Path to desired output folder/file

            ``style`` (``str``): Desired output style

            * ``"html"`` to export one HTML file per pair

            ``verbose`` (``bool``): ``True`` to show verbose messages, otherwise ``False``
        '''
        if style not in {'html'}:
            raise ValueError("Invalid export style: %s" % style)
        if isdir(outpath) or isfile(outpath):
            raise ValueError("Output path exists: %s" % outpath)
        if style == 'html':
            makedirs(outpath)
        pairs = list(self.traverse_pairs())
        for i,pair in enumerate(pairs):
            if verbose:
                print("Exporting pair %d of %d..." % (i+1, len(pairs)), end='\r')
            u,v = pair
            if style == 'html':
                f = open("%s/%d_%s_%s.html" % (outpath, self.num_links(u,v), u, v), 'w')
                f.write(self.get_pair(u, v, style='html'))
                f.close()
        if verbose:
            print("Successfully exported %d pairs" % len(pairs))

def load(mossnet_file):
    '''Load a ``MossNet`` object from file

    Args:
        ``mossnet_file`` (``str``): The desired input file

    Returns:
        ``MossNet``: The resulting ``MossNet`` object
    '''
    if mossnet_file.lower().endswith('.gz'):
        return MossNet(pklload(gopen(mossnet_file)))
    else:
        return MossNet(pklload(open(mossnet_file,'rb')))
