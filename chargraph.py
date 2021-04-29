from igraph import *
from igraph.drawing.text import TextDrawer
import cairo
import pdftotext

characters_LOR = ['Frodo', 'Gandalf', 'Sam', 'Merry', 'Pippin', 'Aragorn', 'Legolas', 'Gimli',
                  'Boromir', ['Sauron', 'Dark Lord'], 'Gollum', 'Bilbo', ['Tom Bombadil', 'Tom', 'Bombadil'],
                  'Elrond', 'Arwen', 'Galadriel', 'Saruman',
                  'Shadowfax', 'Treebeard', 'Quickbeam', 'Shelob', 'Faramir',
                  'Denethor', 'Beregond', 'Barliman']

characters_HP = [['Hannah Abbott', 'Hannah', 'Abbott'], ['Katie Bell', 'Katie'],
                 ['Cuthbert Binns', 'Binns'], ['Sirius Black', 'Sirius'],
                 ['Amelia Bones'], ['Susan Bones', 'Susan'], ['Terry Boot', 'Terry'],
                 ['Lavender Brown', 'Lavender'], ['Cho Chang', 'Cho'],
                 ['Penelope Clearwater', 'Penelope'], ['Crabbe'], ['Barty Crouch', 'Barty', 'Crouch'],
                 ['Fleur Delacour', 'Fleur', 'Delacour'], ['Cedric Diggory', 'Cedric'],
                 ['Albus Dumbledore', 'Albus', 'Dumbledore'], ['Dudley Dursley', 'Dudley', 'Dursley'],
                 ['Marge Dursley', 'Marge'], ['Petunia Dursley', 'Petunia'], ['Vernon Dursley', 'Vernon'],
                 ['Arabella Figg', 'Figg'], ['Argus Filch', 'Filch'],
                 ['Justin Finch-Fletchley', 'Justin', 'Finch-Fletchley'], ['Seamus Finnigan', 'Seamus', 'Finnigan'],
                 ['Nicolas Flamel', 'Nicolas', 'Flamel'], ['Mundungus Fletcher', 'Mundungus', 'Fletcher'],
                 ['Filius Flitwick', 'Flitwick'], ['Cornelius Fudge', 'Fudge'], ['Goyle'],
                 ['Hermione Granger', 'Hermione', 'Granger'], ['Gellert Grindelwald', 'Grindelwald'],
                 ['Rubeus Hagrid', 'Hagrid'], ['Rolanda Hooch', 'Hooch'], ['Angelina Johnson', 'Angelina', 'Johnson'],
                 ['Lee Jordan', 'Lee', 'Jordan'], ['Igor Karkaroff', 'Karkaroff'],
                 ['Viktor Krum', 'Viktor', 'Krum'], ['Bellatrix Lestrange', 'Bellatrix', 'Lestrange'],
                 ['Gilderoy Lockhart', 'Lockhart'], ['Alice and Frank Longbottom', 'Alice and Frank'],
                 ['Augusta Longbottom', 'Augusta'], ['Neville Longbottom', 'Neville'], ['Luna Lovegood', 'Luna'],
                 ['Remus Lupin', 'Remus', 'Lupin'], ['Draco Malfoy', 'Draco'], ['Lucius Malfoy', 'Lucius'],
                 ['Narcissa Malfoy', 'Narcissa'], ['Madam Malkin', 'Malkin'],
                 ['Olympe Maxime', 'Olympe', 'Maxime'], ['Ernie Macmillan', 'Ernie', 'Macmillan'],
                 ['Minerva McGonagall', 'Minerva', 'McGonagall'], ['Alastor Moody', 'Mad-Eye', 'Moody'],
                 ['Garrick Ollivander', 'Ollivander'], ['Pansy Parkinson', 'Pansy', 'Parkinson'],
                 ['Padma Patil', 'Padma'], ['Parvati Patil', 'Parvati'], ['Peter Pettigrew', 'Pettigrew', 'Wormtail'],
                 ['Poppy Pomfrey', 'Pomfrey'], ['Harry Potter', 'Harry'], ['James Potter', 'James'],
                 ['Lily Potter', 'Lily'], ['Quirinus Quirrell', 'Quirrell'], 'The Grey Lady',
                 ['Tom Riddle', 'Tom'], ['Rufus Scrimgeour', 'Scrimgeour'], ['Aurora Sinistra', 'Sinistra'],
                 ['Rita Skeeter', 'Skeeter'], ['Horace Slughorn', 'Slughorn'],
                 ['Severus Snape', 'Severus', 'Snape'], ['Alicia Spinnet', 'Alicia', 'Spinnet'],
                 ['Pomona Sprout', 'Sprout'], ['Dean Thomas'], ['Sybill Trelawney', 'Trelawney'],
                 ['Dolores Umbridge', 'Dolores', 'Umbridge'],
                 ['Voldemort', 'You-Know-Who', 'He Who Must Not Be Named', 'the Dark Lord'],
                 ['Myrtle Warren', 'Myrtle'], ['Arthur Weasley', 'Arthur'], ['Charlie Weasley', 'Charlie'],
                 ['Fred Weasley', 'Fred'], ['George Weasley', 'George'], ['Ginny Weasley', 'Ginny'],
                 ['Molly Weasley', 'Molly'], ['Percy Weasley', 'Percy'], ['Ron Weasley', 'Ron'],
                 ['Oliver Wood', 'Oliver', 'Wood'], 'The Bloody Baron', 'Dobby', 'The Fat Lady',
                 'Fawkes', 'Hedwig', 'Nagini', 'Nearly Headless Nick', 'Norbert', 'Peeves', 'Scabbers', 'Trevor'
                 ]


def plotgraph(filename, characters, title, community=True):
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

    with open(filename + '.pdf', 'rb') as f:
        pdf = pdftotext.PDF(f)
        for pg in pdf:
            tmp = [0] * m
            for i in range(m):
                if type(characters[i]) is list:
                    for charname in characters[i]:
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
        if e['weight'] < maxweight / 5:
            edges_to_delete.append(e)
    g1.delete_edges(edges_to_delete)
    if community:
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
        e['width'] = e['weight'] * 4 / maxweight
    visual_style = {'vertex_size': 5,
                    'vertex_label_size': 15,
                    'vertex_label_dist': 3,
                    'bbox': (1000, 1000),
                    'margin': 100,
                    'edge_curved': True}

    plot = Plot(target=filename + '.png', bbox=(1000, 1000), background="white")
    plot.add(g, layout=coords, **visual_style)
    plot.redraw()
    ctx = cairo.Context(plot.surface)
    ctx.set_font_size(24)
    drawer = TextDrawer(ctx, title, halign=TextDrawer.CENTER)
    drawer.draw_at(0, 40, width=1000)
    plot.save()


plotgraph('HP1', characters_HP, 'Harry Potter and the Philosopher\'s Stone', community=False)
plotgraph('HP2', characters_HP, 'Harry Potter and the Chamber of Secrets', community=False)
plotgraph('HP3', characters_HP, 'Harry Potter and the Prisoner of Azkaban', community=False)
plotgraph('HP4', characters_HP, 'Harry Potter and the Goblet of Fire', community=False)
plotgraph('HP5', characters_HP, 'Harry Potter and the Order of the Phoenix', community=False)
plotgraph('HP6', characters_HP, 'Harry Potter and the Half-Blood Prince', community=False)
plotgraph('HP7', characters_HP, 'Harry Potter and the Deathly Hallows', community=False)

plotgraph('LOR1', characters_LOR, 'The Lord of the Rings: The Fellowship of the Ring')
plotgraph('LOR2', characters_LOR, 'The Lord of the Rings: The Two Towers')
plotgraph('LOR3', characters_LOR, 'The Lord of the Rings: The Return of the King')
