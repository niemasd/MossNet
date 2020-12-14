#! /usr/bin/env python
from gzip import open as gopen
from math import log
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
                    self.graph.add_edge(u, v, attr_dict = {'files':f, 'left':left, 'right':right})

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
                    edge = u_v_edge_data[k]['attr_dict']; u_v_links[edge['files']] = (edge['left'], edge['right'])
        if outfile.lower().endswith('.gz'):
            f = gopen(outfile, mode='wb', compresslevel=9)
        else:
            f = open(outfile, 'wb')
        pkldump(out, f); f.close()

    def __add__(self, o):
        if not isinstance(o, MossNet):
            raise TypeError("unsupported operand type(s) for +: 'MossNet' and '%s'" % type(o).__name__)
        g = MultiDiGraph()
        g.add_edges_from(list(self.graph.edges(data=True)) + list(o.graph.edges(data=True)))
        g.add_nodes_from(list(self.graph.nodes(data=True)) + list(o.graph.nodes(data=True)))
        return MossNet(g)

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
        for k in sorted(links.keys(), key=lambda x: links[x]['attr_dict']['files']):
            d = links[k]['attr_dict']
            u_fn, v_fn = d['files']
            u_percent, u_html = d['left']
            v_percent, v_html = d['right']
            if style == 'tuples':
                out[(u_fn, v_fn)] = ((u_percent, u_html), (v_percent, v_html))
            elif style in {'html', 'htmls'}:
                out[(u_fn, v_fn)] = '<html><table style="width:100%%" border="1"><tr><td colspan="2"><center><b>%s/%s --- %s/%s</b></center></td></tr><tr><td>%s (%d%%)</td><td>%s (%d%%)</td></tr><tr><td><pre>%s</pre></td><td><pre>%s</pre></td></tr></table></html>' % (u, u_fn, v, v_fn, u, u_percent, v, v_percent, u_html, v_html)
        if style == 'html':
            out = '<html>' + '<br>'.join(out[fns].replace('<html>','').replace('</html>','') for fns in sorted(out.keys())) + '</html>'
        return out

    def get_summary(self, style='html'):
        '''Returns a summary of this ``MossNet``

        Args:
            ``style`` (``str``): The representation of this ``MossNet``

        Returns:
            ``dict``: A summary of this ``MossNet``, where keys are filenames
        '''
        if style not in {'html'}:
            raise ValueError("Invalid summary style: %s" % style)
        matches = list() # list of (u_path, u_percent, v_path, v_percent) tuples
        for u,v in self.traverse_pairs(order=None):
            links = self.graph.get_edge_data(u,v)
            for k in links:
                d = links[k]['attr_dict']
                u_fn, v_fn = d['files']
                u_percent, u_html = d['left']
                v_percent, v_html = d['right']
                matches.append(('%s/%s' % (u,u_fn), u_percent, '%s/%s' % (v,v_fn), v_percent))
        matches.sort(reverse=True, key=lambda x: max(x[1],x[3]))
        return '<html><table style="width:100%%" border="1">%s</table></html>' % ''.join(('<tr><td>%s (%d%%)</td><td>%s (%d%%)</td></tr>' % tup) for tup in matches)

    def num_links(self, u, v):
        '''Returns the number of links between ``u`` and ``v``

        Args:
            ``u`` (``str``): A node label

            ``v`` (``str``): A node label not equal to ``u``

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

    def outlier_pairs(self):
        '''Predict which student pairs are outliers (i.e., too many problem similarities).
        The distribution of number of links between student pairs (i.e., histogram) is modeled as y = A/(B^x),
        where x = a number of links, and y = the number of student pairs with that many links

        Returns:
            ``list`` of ``tuple``: The student pairs expected to be outliers (in decreasing order of significance)
        '''
        links = dict() # key = number of links; value = set of student pairs that have that number of links
        for u,v in self.traverse_pairs():
            n = self.num_links(u,v)
            if n not in links:
                links[n] = set()
            links[n].add((u,v))
        mult = list(); min_links = min(len(s) for s in links.values()); max_links = max(len(s) for s in links.values())
        for i in range(min_links, max_links):
            if i not in links or i+1 not in links or len(links[i+1]) > len(links[i]):
                break
            mult.append(float(len(links[i]))/len(links[i+1]))
        B = sum(mult)/len(mult)
        A = len(links[min_links]) * (B**min_links)
        n_cutoff = log(A)/log(B)
        out = list()
        for n in sorted(links.keys(), reverse=True):
            if n < n_cutoff:
                break
            for u,v in links[n]:
                out.append((n,u,v))
        return out

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

    def export(self, outpath, style='html', gte=0, verbose=False):
        '''Export the links in this ``MossNet`` in the specified style

        Args:
            ``outpath`` (``str``): Path to desired output folder/file

            ``style`` (``str``): Desired output style

            ``gte`` (``int``): The minimum number of links for an edge to be exported

            * ``"dot"`` to export as a GraphViz DOT file

            * ``"gexf"`` to export as a Graph Exchange XML Format (GEXF) file

            * ``"html"`` to export one HTML file per pair

            ``verbose`` (``bool``): ``True`` to show verbose messages, otherwise ``False``
        '''
        if style not in {'dot', 'gexf', 'html'}:
            raise ValueError("Invalid export style: %s" % style)
        if isdir(outpath) or isfile(outpath):
            raise ValueError("Output path exists: %s" % outpath)
        if not isinstance(gte, int):
            raise TypeError("'gte' must be an 'int', but you provided a '%s'" % type(gte).__name__)
        if gte < 0:
            raise ValueError("'gte' must be non-negative, but yours was %d" % gte)

        # export as folder of HTML files
        if style == 'html':
            summary = self.get_summary(style='html')
            pairs = list(self.traverse_pairs(order=None))
            makedirs(outpath)
            f = open('%s/summary.html' % outpath, 'w'); f.write(summary); f.close()
            for i,pair in enumerate(pairs):
                if verbose:
                    print("Exporting pair %d of %d..." % (i+1, len(pairs)), end='\r')
                u,v = pair
                if self.num_links(u,v) < gte:
                    continue
                if style == 'html':
                    f = open("%s/%d_%s_%s.html" % (outpath, self.num_links(u,v), u, v), 'w')
                    f.write(self.get_pair(u, v, style='html'))
                    f.close()
            if verbose:
                print("Successfully exported %d pairs" % len(pairs))

        # export as GraphViz DOT or a GEXF file
        elif style in {'dot', 'gexf'}:
            if verbose:
                print("Computing colors...", end='')
            max_links = max(self.num_links(u,v) for u,v in self.traverse_pairs())
            try:
                from seaborn import color_palette
            except:
                raise RuntimeError("Exporting as a DOT or GEXF file currently requires seaborn")
            pal = color_palette("Reds", max_links)
            if verbose:
                print(" done")
                print("Computing node information...", end='')
            nodes = list(self.get_nodes())
            index = {u:i for i,u in enumerate(nodes)}
            if verbose:
                print(" done")
                print("Writing output file...", end='')
            outfile = open(outpath, 'w')
            if style == 'dot':
                pal = [str(c).upper() for c in pal.as_hex()]
                outfile.write("graph G {\n")
                for u in nodes:
                    outfile.write('  node%d[label="%s"]\n' % (index[u], u))
                for u,v in self.traverse_pairs():
                    curr_num_links = self.num_links(u,v)
                    if curr_num_links < gte:
                        continue
                    outfile.write('  node%d -- node%d[color="%s"]\n' % (index[u], index[v], pal[curr_num_links-1]))
                outfile.write('}\n')
            elif style == 'gexf':
                from datetime import datetime
                pal = [(int(255*c[0]), int(255*c[1]), int(255*c[2])) for c in pal]
                outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                outfile.write('<gexf xmlns="http://www.gexf.net/1.3draft" xmlns:viz="http://www.gexf.net/1.3draft/viz">\n')
                outfile.write('  <meta lastmodifieddate="%s">\n' % datetime.today().strftime('%Y-%m-%d'))
                outfile.write('    <creator>MossNet</creator>\n')
                outfile.write('    <description>A MossNet network exported to GEXF</description>\n')
                outfile.write('  </meta>\n')
                outfile.write('  <graph mode="static" defaultedgetype="undirected">\n')
                outfile.write('    <nodes>\n')
                for u in nodes:
                    outfile.write('      <node id="%d" label="%s"/>\n' % (index[u], u))
                outfile.write('    </nodes>\n')
                outfile.write('    <edges>\n')
                for i,pair in enumerate(self.traverse_pairs()):
                    u,v = pair
                    curr_num_links = self.num_links(u,v)
                    if curr_num_links == 0:
                        continue
                    color = pal[curr_num_links-1]
                    outfile.write('      <edge id="%d" source="%d" target="%d">\n' % (i, index[u], index[v]))
                    outfile.write('        <viz:color r="%d" g="%d" b="%d"/>\n' % (color[0], color[1], color[2]))
                    outfile.write('      </edge>\n')
                outfile.write('    </edges>\n')
                outfile.write('  </graph>\n')
                outfile.write('</gexf>\n')
            outfile.close()
            if verbose:
                print(" done")

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
