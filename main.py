from igraph import *
from igraph.drawing.text import TextDrawer
import cairo
import pdftotext
import json
import numpy as np
from ripser import ripser
from persim import plot_diagrams
import matplotlib.pyplot as plt


l = [["Anna Pavlovna", "Scherer"], ["Vasili Kuragin", "Prince Vasili"], ["Helene", "Countess Bezukhova"],
     ["Pierre"], ["Hippolyte Kuragin", "Hippolyte"], ["Andrei Nikolayevich Bolkonsky", "Andrew"],
     ["Anna Mikhaylovna Drubetskaya", "Princess Drubetskaya"], ["Anatole Kuragin", "Anatole"], ["Dolokhov"],
     ["Natasha Rostova", "Natasha"], ["Vera Rostova", "Vera"], ["Nikolai Rostov", "Nicholas"],
     ["Nikolay Andreevitch Bolkonsky", "Nicholas Andreevich", "Nicholas Bolkonski", "Prince Bolkonski"],
     ["Petya Rostov", "Petya"], ["Sonya"], ["Boris Drubetskoy", "Boris"], ["Shinshin"],
     ["Alphonse Karlovich Berg", "Berg"], ["Marya Dmitrievna"], ["Marya Bolkonskaya", "Princess Mary"],
     ["Mademoiselle Bourienne", "Bourienne"], ["Tikhon Shtcherbatov", "Tikhon"],
     ["Michael Ivanovich"], ["Kutuzov"], ["Nesvitski"], ["Zherkov"], ["General Mack", "Mack"], ["Denisov"],
     ["Lavrushka"], ["Bilibin"], ["Emperor Francis", "Francis"], ["Bagration"], ["Tushin"], ["Yakov Alpatych"],
     ["Alexander I", "Alexander"], ["Weyrother"], ["Napoleon", "Bonaparte"], ["Willarski"],
     ["Arakcheev"], ["Rostopchin"], ["Balaga"], ["Murat"]]
with open('characters_WP_en', 'w') as f:
    json.dump(l, f)


def getConnectionData(pdfFilename, charactersFilename):
    with open(charactersFilename, 'r') as f:
        characters = json.load(f)
    m = len(characters)
    if type(pdfFilename) is list:
        adjMatrix = np.zeros((m, m))
        names = []
        for filename in pdfFilename:
            _adjMatrix, names = getConnectionData(filename, charactersFilename)
            adjMatrix += _adjMatrix
        return adjMatrix, names

    adjMatrix = np.zeros((m, m))
    with open(pdfFilename, 'rb') as f:
        pdf = pdftotext.PDF(f)
        for pg in pdf:
            flags = np.zeros(m)
            for i in range(m):
                if type(characters[i]) is list:
                    for charname in characters[i]:
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

    names = []
    for name in characters:
        if (type(name)) is list:
            names.append(name[0])
        else:
            names.append(name)
    return adjMatrix, names


def getDistanceMatrix(adjMatrix, epsilon=1.):
    m = len(adjMatrix)
    distMatrix = np.zeros((m, m))
    degs = np.zeros(m)
    for i in range(m):
        degs[i] = np.sum(adjMatrix[i])
    for i in range(m):
        for j in range(i):
            distMatrix[i][j] = np.sqrt((degs[i] + 1) * (degs[j] + 1)) / (adjMatrix[i][j] + epsilon)
            distMatrix[j][i] = distMatrix[i][j]
    return distMatrix


def plotgraph(adjMatrix, names, title, picFilename, communityThreshold=10, characterTheshold=0.05):
    m = len(names)
    g = Graph()
    g.add_vertices(m)
    for i in range(m):
        g.vs[i]['label'] = names[i]
        for j in range(i, m):
            g.add_edge(i, j)
            g.es[g.get_eid(i, j)]['weight'] = adjMatrix[i][j]

    maxweight = 0
    for e in g.es:
        if maxweight < e['weight']:
            maxweight = e['weight']

    # get a layout that reflects the presence of communities
    g1 = g.copy()
    distMatrix = getDistanceMatrix(adjMatrix)
    edges_to_delete = []
    for i in range(m):
        for j in range(i):
            if distMatrix[i][j] > communityThreshold:
                edges_to_delete.append(g1.get_eid(i, j))
    g1.delete_edges(edges_to_delete)
    cl = g1.community_fastgreedy(weights=g1.es['weight'])
    membership = cl.as_clustering().membership
    edges_to_delete = []
    for e in g1.es():
        if membership[e.tuple[0]] != membership[e.tuple[1]]:
            edges_to_delete.append(e)
    g1.delete_edges(edges_to_delete)

    # delete irrelevant vertices
    edges_to_delete = []
    for e in g.es:
        if e['weight'] < maxweight * characterTheshold:
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


def plotHomologies(adjMatrix, title, picFilename):
    distMatrix = getDistanceMatrix(adjMatrix)
    result = ripser(distMatrix, distance_matrix=True, maxdim=3, do_cocycles=True, thresh=1000)
    diagrams = result['dgms']
    plot_diagrams(diagrams, show=False)
    plt.title(title)
    plt.savefig(picFilename, dpi=200)
    plt.close()


def plotAll():
    adjMatrix, names = getConnectionData(['pdfs/SIF1.pdf', 'pdfs/SIF2.pdf', 'pdfs/SIF3.pdf', 'pdfs/SIF4.pdf', 'pdfs/SIF5.pdf'], 'characterLists/characters_SIF')
    plotHomologies(adjMatrix, 'A Song of Ice and Fire (1 - 5)', 'SIFhom.png')
    adjMatrix, names = getConnectionData(['pdfs/LTR1.pdf', 'pdfs/LTR2.pdf', 'pdfs/LTR3.pdf'], 'characterLists/characters_LTR')
    plotHomologies(adjMatrix, 'The Lord of the Rings (1 - 3)', 'LTRhom.png')
    adjMatrix, names = getConnectionData(['pdfs/HP1.pdf', 'pdfs/HP2.pdf', 'pdfs/HP3.pdf', 'pdfs/HP4.pdf', 'pdfs/HP5.pdf', 'pdfs/HP6.pdf', 'pdfs/HP7.pdf'], 'characterLists/characters_HP')
    plotHomologies(adjMatrix, 'Harry Potter (1 - 7)', 'HPhom.png')
    adjMatrix, names = getConnectionData('pdfs/WP.pdf', 'characterLists/characters_WP')
    plotHomologies(adjMatrix, 'Война и мир', 'WPhom.png')
    plotHomologies(adjMatrix, 'War and Peace', 'WPhom_en.png')
    adjMatrix, names = getConnectionData('pdfs/MM.pdf', 'characterLists/characters_MM')
    plotHomologies(adjMatrix, 'Мастер и Маргарита', 'MMhom.png')
    plotHomologies(adjMatrix, 'The Master and Margarita', 'MMhom_en.png')

    adjMatrix, names = getConnectionData('pdfs/HP1.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Philosopher\'s Stone', 'HP1.png', communityThreshold=12)
    adjMatrix, names = getConnectionData('pdfs/HP2.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Chamber of Secrets', 'HP2.png', communityThreshold=15)
    adjMatrix, names = getConnectionData('pdfs/HP3.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Prisoner of Azkaban', 'HP3.png', communityThreshold=12)
    adjMatrix, names = getConnectionData('pdfs/HP4.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Goblet of Fire', 'HP4.png', communityThreshold=13)
    adjMatrix, names = getConnectionData('pdfs/HP5.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Order of the Phoenix', 'HP5.png', communityThreshold=13)
    adjMatrix, names = getConnectionData('pdfs/HP6.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Half-Blood Prince', 'HP6.png', communityThreshold=15)
    adjMatrix, names = getConnectionData('pdfs/HP7.pdf', 'characterLists/characters_HP')
    plotgraph(adjMatrix, names, 'Harry Potter and the Deathly Hallows', 'HP7.png', communityThreshold=14)

    adjMatrix, names = getConnectionData('pdfs/LTR1.pdf', 'characterLists/characters_LTR')
    plotgraph(adjMatrix, names, 'The Lord of the Rings: The Fellowship of the Ring', 'LTR1.png', communityThreshold=20)
    adjMatrix, names = getConnectionData('pdfs/LTR2.pdf', 'characterLists/characters_LTR')
    plotgraph(adjMatrix, names, 'The Lord of the Rings: The Two Towers', 'LTR2.png', communityThreshold=20)
    adjMatrix, names = getConnectionData('pdfs/LTR3.pdf', 'characterLists/characters_LTR')
    plotgraph(adjMatrix, names, 'The Lord of the Rings: The Return of the King', 'LTR3.png', communityThreshold=25)

    adjMatrix, names = getConnectionData('pdfs/WP.pdf', 'characterLists/characters_WP')
    plotgraph(adjMatrix, names, 'Война и мир', 'WP.png', communityThreshold=15)
    adjMatrix, names = getConnectionData('pdfs/WP.pdf', 'characterLists/characters_WP_en')
    plotgraph(adjMatrix, names, 'War and Peace', 'WP_en.png', communityThreshold=15)

    adjMatrix, names = getConnectionData('pdfs/MM.pdf', 'characterLists/characters_MM')
    plotgraph(adjMatrix, names, 'Мастер и Маргарита', 'MM.png', communityThreshold=25)
    adjMatrix, names = getConnectionData('pdfs/MM.pdf', 'characterLists/characters_MM_en')
    plotgraph(adjMatrix, names, 'The Master and Margarita', 'MM_en.png', communityThreshold=25)

    adjMatrix, names = getConnectionData('pdfs/SIF1.pdf', 'characterLists/characters_SIF')
    plotgraph(adjMatrix, names, 'A Song of Ice and Fire: A Game of Thrones', 'SIF1.png', communityThreshold=25, characterTheshold=0.1)
    adjMatrix, names = getConnectionData('pdfs/SIF2.pdf', 'characterLists/characters_SIF')
    plotgraph(adjMatrix, names, 'A Song of Ice and Fire: A Clash of Kings', 'SIF2.png', communityThreshold=17)
    adjMatrix, names = getConnectionData('pdfs/SIF3.pdf', 'characterLists/characters_SIF')
    plotgraph(adjMatrix, names, 'A Song of Ice and Fire: A Storm of Swords', 'SIF3.png', communityThreshold=20)
    adjMatrix, names = getConnectionData('pdfs/SIF4.pdf', 'characterLists/characters_SIF')
    plotgraph(adjMatrix, names, 'A Song of Ice and Fire: A Feast for Crows', 'SIF4.png', communityThreshold=13)
    adjMatrix, names = getConnectionData('pdfs/SIF5.pdf', 'characterLists/characters_SIF')
    plotgraph(adjMatrix, names, 'A Song of Ice and Fire: A Dance with Dragons', 'SIF5.png', communityThreshold=21)


if __name__ == '__main__':
    plotAll()