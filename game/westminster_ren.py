"""renpy
init python:
"""
from pygame_sdl2 import Rect

class Westminster(renpy.Displayable):
    '''
    Custom Displayable
    '''
    def __init__(self, the_list, bg=False, **kwargs):
        super(Westminster, self).__init__(**kwargs)
        self.the_list = the_list
        self.bg = bg

    def render(self, width, height, st, at):
        poslist, blocksize, svgwidth, svgheight = self.seats([(p[0], p[2]) for p in self.the_list])
        # réorganisation des indices pour avoir le même format d'entrée que Newarch
        ratio=svgwidth/svgheight
        ratioc=float(width)/height
        # tâtonnements, testés par disjonction de cas
        if ratio<1.0:
            # le diagramme est portrait
            if ratioc<ratio: # OK
                # le cadre est portrait
                # la hauteur sera inférieure à celle du cadre
                height *= 1/ratio * ratioc
                # la largeur sera celle du cadre
            elif ratioc<1.0: # OK
                # le cadre est portrait
                # la largeur sera inférieure à celle du cadre
                width *= ratio * 1/ratioc
                # la hauteur sera celle du cadre
            else: # OK
                # le cadre est paysage
                # la largeur sera inférieure à la hauteur du cadre
                width *= ratio * 1/ratioc
                # la hauteur sera celle du cadre
            fact = height
        else:
            # le diagramme est paysage
            # on remplace les height par des width, les ratio par 1/ratio et les ratioc par 1/ratioc
            if ratioc>ratio:
                # le cadre est paysage
                # la largeur sera inférieure à celle du cadre
                width *= ratio * 1/ratioc
                # la hauteur sera celle du cadre
            elif ratioc>1.0:
                # le cadre est paysage
                # la hauteur sera inférieure à celle du cadre
                height *= 1/ratio * ratioc
                # la largeur sera celle du cadre
            else:
                # le cadre est portrait
                # la hauteur sera inférieure à la largeur du cadre
                height *= 1/ratio * ratioc
                # la largeur sera celle du cadre
            fact = width
        # mettre des marges de 10 pixels en haut et en bas, si on garde la norme sortante
        render = renpy.Render(width, height)
        # render.fill('#0f0') # debug, pour voir les limites du render
        if self.bg:
            render.fill(self.bg)
        canvas = render.canvas()
        # on parcourt les types de partis
        for wing in {'head', 'left', 'right', 'center'}:
            # on parcourt les partis
            counter=0
            for p in [party for party in self.the_list if party[2] == wing]:
                for kant in range(counter, counter+p[0]):
                    rkt = Rect(poslist[wing][kant][0]*fact, poslist[wing][kant][1]*fact, blocksize*.9*fact, blocksize*.9*fact)
                    canvas.rect(renpy.color.Color(p[1]), # the color
                                rkt, # le rectangle
                                )
                    # écrire un retangle sur le canvas de coordonnées (poslist['head'][kant][0], poslist['head'][kant][1], blocksize*.9, blocksize*.9)
                    pass
                counter = kant+1
        return render

    def seats(self, the_list):
        # éléments des éléments de the_list : nombre de sièges, groupe (droite/gauche/speaker/centre)
        # Keep a running total of the number of delegates in each part of the diagram, for use later.
        sumdelegates = {'left': 0, 'right': 0, 'center': 0, 'head': 0}
        for p in the_list:
            if len(p)<2:
                raise IndexError(_("The number of seats, the wing alignment and the color must be supplied for each party."))
                # Le nombre de siège, l'aile où siéger et la couleur doivent être fournis pour chaque parti
            if type(p[0]) not in {int, bool}:
                raise TypeError(_("The number of seats must be an integer."))
                # Le nombre de sièges doit être un entier
            for wing in sumdelegates:
                if wing in p[1]:
                    sumdelegates[wing] += p[0]
        if sumdelegates['head'] > 1:
            raise ValueError(_("There can't be more than one Speaker."))
            # Il ne peut y avoir plus d'un président pour la chambre
        if not any(sumdelegates.values()):
            raise ValueError(_("There are no delegate seats to be found."))
            # Aucun siège n'a été trouvé
        # calcul du nombre de rangs
        wingrows = int(math.ceil(math.sqrt( max(sumdelegates['left'], sumdelegates['right']) /20.0 ))*2) # ???
        # calcul du nombre de colonnes de sièges
        wingcols = int(math.ceil( max(sumdelegates['left'], sumdelegates['right']) /float(wingrows))) # ???
        # calcul de la taille du groupe du centre
        centercols = int(math.ceil(math.sqrt(sumdelegates['center']/4.0))) # ???
        if centercols:
            centerrows = int(math.ceil(float(sumdelegates['center'])/centercols))
        else:
            centerrows = 0
        # calcul du nombre total de colonnes
        leftoffset = sumdelegates['head']# si il y a un speaker
        totalcols = wingcols + leftoffset
        if sumdelegates['center']:
            totalcols += 1 + centercols
        # calcul du nombre total de rangs
        totalrows = max(2*(wingrows+1), centerrows)
        # taille d'un carré/siège, maximale, en comptant la marge retirée après
        blocksize = 1.0/max(totalcols, totalrows) # 1.0 étant la taille totale
        svgwidth = blocksize*totalcols#+10 # marge retirée
        svgheight = blocksize*totalrows#+10 # marge retirée
        # initialiser la liste des positions
        poslist = {'head':[], 'left':[], 'right':[], 'center':[]}
        # position y du speaker
        centertop = svgheight/2-blocksize*.9/2 # la soustraction parce qu'on sauvegarde le coin supérieur gauche du carré
        # position du speaker
        if sumdelegates['head']:
            poslist['head'].append([blocksize*.05, centertop]) # marge retirée
        for x in range(centercols):
            # nombre de sièges sur cette colonne
            thiscol = int(min(centerrows, sumdelegates['center']-x*centerrows)) # semble correct
            for y in range(thiscol):
                # poslist['center'].append([svgwidth-5.0-(centercols-x-.1/2)*blocksize, ((svgheight-thiscol*blocksize)/2)+blocksize*(y+.1/2)]) # le 5.0 est la marge gauche
                poslist['center'].append([svgwidth-(centercols-x-.1/2)*blocksize, ((svgheight-thiscol*blocksize)/2)+blocksize*(y+.1/2)]) # marge retirée
                poslist['center'].sort(key=lambda point: point[1])
        # le groupe left est au-dessus
        for x in range(wingcols):
            # for y in range(wingrows['left']):
            for y in range(wingrows):
                # poslist['left'].append([5+(leftoffset+x+.1/2)*blocksize, centertop-(1.5+y)*blocksize]) # le 5 est la marge gauche
                poslist['left'].append([(leftoffset+x+.1/2)*blocksize, centertop-(1.5+y)*blocksize]) # marge retirée
        # le groupe right est en-dessous
        for x in range(wingcols):
            for y in range(wingrows):
                # poslist['right'].append([5+(leftoffset+x+.1/2)*blocksize, centertop+(1.5+y)*blocksize]) # le 5 est la marge gauche
                poslist['right'].append([(leftoffset+x+.1/2)*blocksize, centertop+(1.5+y)*blocksize]) # marge retirée
        for wing in {'left', 'right'}:
            poslist[wing].sort(key=lambda point: point[0])
        return poslist, blocksize, svgwidth, svgheight
