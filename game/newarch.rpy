init python:
    totals = []
    for rows in range(1, 75):
        tot = 0
        rad = 1/float(4*rows-2)
        for r in range(1, rows+1):
            R = .5 + 2*(r-1)*rad
            tot += int(math.pi*R/(2*rad))
        totals.append(tot)

    def fnewarch(the_list, **properties):
        # the_list : liste de tuples
        # tuple : nombre de sièges, couleur
        ccls = [(0, 0), 'transmask', (0, 0), 'notif']
        # pour tester les arguments positionnels
        # nombre max de sièges, le nombre de rangs est l'indice+1
        # totals = [4, 15, 33, 61, 95, 138, 189, 247, 313, 388, 469, 559, 657, 762, 876, 997, 1126, 1263, 1408, 1560, 1722, 1889, 2066, 2250, 2442, 2641, 2850, 3064, 3289, 3519, 3759, 4005, 4261, 4522,
        #           4794, 5071, 5358, 5652, 5953, 6263, 6581, 6906, 7239, 7581, 7929, 8287, 8650, 9024, 9404, 9793, 10187, 10594, 11003, 11425, 11850, 12288, 12729, 13183, 13638, 14109, 14580, 15066,
        #           15553, 16055, 16557, 17075, 17592, 18126, 18660, 19208, 19758, 20323, 20888, 21468, 22050, 22645, 23243, 23853, 24467, 25094, 25723, 26364, 27011, 27667, 28329, 29001, 29679, 30367, 31061]
        sumdelegates = 0
        # addition des sièges et vérifications défensives
        for p in the_list:
            if len(p)!=2 or type(p[0]) is not int:
                return None
            sumdelegates += p[0]
            if sumdelegates>totals[-1]:
                return None
        if not sumdelegates:
            return None
        # détermination du nombre de rangées
        for i in range(len(totals)):
            if totals[i] >= sumdelegates:
                rows = i+1
                break
        # définition du rayon maximal des cercles
        # rad = 0.4/rows
        rad = .29/rows # pourquoi ça marche ???
        rad = 1/float(4*rows-2)
        # listage des centres des cercles
        poslist = []
        # pour chaque rangée
        for r in range(1, rows+1):
            # rayon de la rangée
            # R = .5 + (float(r-1) * (1 - 1/float(rows) ) )/(2*float(rows-1))
            R = (3.0*rows+4.0*r-2.0)/(4.0*rows) # ancienne version
            R = (3.0*rows+4.0*r-2.0)/(4.0*rows)*(1.0/1.75)
            R = .5 + 2*(r-1)*rad
            # print(R)
            # nombre de sièges sur cette rangée
            if r==rows:
                J = sumdelegates-len(poslist)
            else:
                # J = int(float(sumdelegates) / totals[rows-1] * math.pi/(2*math.asin(2.0/(3.0*rows+4.0*r-2.0))))
                # taux de remplissage général (par rapport au totals correspondant) fois le maximum de la rangée
                J = int(float(sumdelegates) / totals[rows-1] * math.pi*R/(2*rad))
            if J==1:
                poslist.append([math.pi/2.0, 1.0*R, R])
            else:
                for j in range(J):
                    # angle de position du siège
                    angle = float(j) * (math.pi-2.0*math.asin(rad/R)) / (float(J)-1.0) + math.asin(rad/R)
                    # position par rapport au président de l'hémicycle (y+ vers le haut)
                    poslist.append([angle, R*math.cos(angle)+1.0, R*math.sin(angle)])
        # print(poslist)
        # on range les points par angle croissant de gauche à droite
        poslist.sort(reverse=True)
        # liste des Circle
        ccls = []
        counter=0
        # vrai diamètre des cercles
        return [po[1:] for po in poslist], rad
        # fonctionnement en Composite, discontinued
        poss = []
        diam = 1.6*rad
        ccls.append((0, 0))
        ccls.append(Solid('#0F0'))
        a=640
        rade = int(rad*a)
        for p in the_list:
            color = p[1]
            cir = Circle(color, xsize=rade, ysize=rade)
            for kant in range(counter, counter+p[0]):
                posx = poslist[kant][1]/2#*a #- rade#/2 # à corriger
                posy = (1.0-poslist[kant][2])#*a #- rade#/2 # à corriger
                # poss.append((int(posx), int(posy))) # log des positions
                # ccls.append((int(posx), int(posy)))
                ccls.append((posx, posy))
                ccls.append(cir)
            counter = kant+1
        # return poss
        ccls.append((0, 0))
        ccls.append(cir)
        return Composite((2*a-rade, a-rade), *ccls, **properties)

    class Newarch(renpy.Displayable):
        def __init__(self, the_list, sizex=config.screen_width, sizey=config.screen_height, **kwargs):
            super(Newarch, self).__init__(**kwargs)
            self.the_list = the_list
            # semble étrange mais bon...
            # self.width = 0
            # self.height = 0
            # self.width = sizex
            # self.height = sizey
            # demander comment on fait pour des trucs genre Solid, qui remplissent tout par défaut
            # ou comme LayeredImage, qui shrink à mort par défaut
        def render(self, width, height, st, at):
            width*=2
            height*=2
            width = max(self.style.xminimum, width)
            height = max(self.style.yminimum, height)
            if width>2*height:
                width=2*height
            else:
                height=width/2
            render = renpy.Render(width, height)
            render.fill('#0f0')
            canvas = render.canvas()
            poslist, rad = fnewarch(self.the_list) # on ne peut plus passer de propriétés en paramètres ?
            diam = 1.6*rad
            # diam = 2*rad
            # canvas.circle(renpy.color.Color('#00f'), (0, 0), 40)
            counter=0
            for p in self.the_list:
                color = p[1]
                for kant in range(counter, counter+p[0]):
                    canvas.circle(renpy.color.Color(p[1]), # the color
                                  (poslist[kant][0]*height, (1-poslist[kant][1])*height), # the centre
                                  height*diam/2, # the radius
                                  )
                    # canvas.circle(renpy.color.Color('#00f'), (poslist[kant][0]*height, (1-poslist[kant][1])*height-height*rad), 40)
                counter = kant+1
            return render
            # canvas.circle(color, pos, radius, width=0)
            canvas.circle(renpy.color.Color("#F00"), # the color
                          (width/2, height/2), # the centre
                          40, # the radius
                          width=0 # width - 0 is filled, else linewidth of drawn circle
                          )
            return render

    def newarch(the_list, *args, **kwargs):
        return At(Newarch(the_list, *args, **kwargs), tr_zoom(.5))
