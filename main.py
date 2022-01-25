from igraph import *
from igraph.drawing.text import TextDrawer
import cairo
import pdftotext
import json

def getAdjMatrix(pdfFilename, charactersFilename):
    with open(charactersFilename, 'r') as f:
        characters = json.load(f)
    m = len(characters)
    adjMatrix = np.zeros((m, m))

    with open(pdfFilename, 'rb') as f:
        pdf = pdftotext.PDF(f)
        for pg in pdf:
            flags = np.zeros(m)
            for i in range(m):
                if type(characters[i]) is list:
                    for charname in characters[i][1:]:
                        if pg.find(charname) != -1:
                            flags[i] = 1
                else:
                    if pg.find(characters[i]) != -1:
                        flags[i] = 1
            for i in range(m):
                if not flags[i]:
                    continue
                for j in range(i):
                    if flags[j]:
                        adjMatrix[i][j] += 1
                        adjMatrix[j][i] += 1

def plotgraph(pdfFilename, charactersFilename, title, picFilename):
    with open(charactersFilename, 'r') as f:
        characters = json.load(f)
    m = len(characters)
    g = Graph()
    g.add_vertices(m)
    for i in range(m):
        if type(characters[i]) is list:
            g.vs[i]['label'] = characters[i][0]
        else:
            g.vs[i]['label'] = characters[i]
    for i in range(m):
        for j in range(i, m):
            g.add_edge(i, j)
            g.es[g.get_eid(i, j)]['weight'] = 0

    with open(pdfFilename, 'rb') as f:
        pdf = pdftotext.PDF(f)
        for pg in pdf:
            tmp = [0] * m
            for i in range(m):
                if type(characters[i]) is list:
                    for charname in characters[i][1:]:
                        if pg.find(charname) != -1:
                            tmp[i] = 1
                else:
                    if pg.find(characters[i]) != -1:
                        tmp[i] = 1
            for i in range(m):
                if not tmp[i]:
                    continue
                for j in range(m):
                    if tmp[j] and i != j:
                        g.es[g.get_eid(i, j)]['weight'] += 1

    maxweight = 0
    for e in g.es:
        if maxweight < e['weight']:
            maxweight = e['weight']

    g1 = g.copy()
    edges_to_delete = []
    for e in g1.es:
        if e['weight'] < maxweight / 15:
            edges_to_delete.append(e)
    g1.delete_edges(edges_to_delete)
    cl = g1.community_fastgreedy(weights=g1.es['weight'])
    membership = cl.as_clustering().membership
    edges_to_delete = []
    for e in g1.es():
        if membership[e.tuple[0]] != membership[e.tuple[1]]:
            edges_to_delete.append(e)
    g1.delete_edges(edges_to_delete)

    edges_to_delete = []
    for e in g.es:
        if e['weight'] < maxweight / 50:
            edges_to_delete.append(e)
    g.delete_edges(edges_to_delete)
    vertices_to_delete = []
    for v in g.vs:
        if v.degree() < 1:
            vertices_to_delete.append(v)
    g.delete_vertices(vertices_to_delete)
    g1.delete_vertices(vertices_to_delete)

    coords = g1.layout_kamada_kawai()

    for e in g.es:
        e['width'] = e['weight'] * 3 / maxweight
    visual_style = {'vertex_size': 5,
                    'vertex_label_size': 18,
                    'vertex_label_dist': 3,
                    'bbox': (1000, 1000),
                    'margin': 120,
                    'edge_curved': True}

    plot = Plot(target=picFilename, bbox=(1000, 1000), background="white")
    plot.add(g, layout=coords, **visual_style)
    plot.redraw()
    ctx = cairo.Context(plot.surface)
    ctx.set_font_size(24)
    drawer = TextDrawer(ctx, title, halign=TextDrawer.CENTER)
    drawer.draw_at(0, 40, width=1000)
    plot.save()

"""
plotgraph('pdfs/HP1.pdf', 'characters_HP', 'Harry Potter and the Philosopher\'s Stone', 'HP1.png')
plotgraph('pdfs/HP2.pdf', 'characters_HP', 'Harry Potter and the Chamber of Secrets', 'HP2.png')
plotgraph('pdfs/HP3.pdf', 'characters_HP', 'Harry Potter and the Prisoner of Azkaban', 'HP3.png')
plotgraph('pdfs/HP4.pdf', 'characters_HP', 'Harry Potter and the Goblet of Fire', 'HP4.png')
plotgraph('pdfs/HP5.pdf', 'characters_HP', 'Harry Potter and the Order of the Phoenix', 'HP5.png')
plotgraph('pdfs/HP6.pdf', 'characters_HP', 'Harry Potter and the Half-Blood Prince', 'HP6.png')
plotgraph('pdfs/HP7.pdf', 'characters_HP', 'Harry Potter and the Deathly Hallows', 'HP7.png')

plotgraph('pdfs/LTR1.pdf', 'characters_LTR', 'The Lord of the Rings: The Fellowship of the Ring', 'LTR1.png')
plotgraph('pdfs/LTR2.pdf', 'characters_LTR', 'The Lord of the Rings: The Two Towers', 'LTR2.png')
plotgraph('pdfs/LTR3.pdf', 'characters_LTR', 'The Lord of the Rings: The Return of the King', 'LTR3.png')

plotgraph('pdfs/WP.pdf', 'characters_WP', 'Война и мир', 'WP.png')
"""

plotgraph('pdfs/MM.pdf', 'characters_MM', 'Мастер и Маргарита', 'MM.png')
