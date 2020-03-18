init python:
    import math

    class Newarch(renpy.Displayable):
        '''
        Custom displayable
        Zoom .5 to have the real size
        Not to use directly, use the newarch function as a proxy handler
        '''
        def __init__(self, the_list, sizex=config.screen_width, sizey=config.screen_height, **kwargs):
            super(Newarch, self).__init__(**kwargs)
            self.the_list = the_list

            totals = []
            for rows in range(1, 75):
                tot = 0
                rad = 1/float(4*rows-2)
                for r in range(1, rows+1):
                    R = .5 + 2*(r-1)*rad
                    tot += int(math.pi*R/(2*rad))
                totals.append(tot)
            # totals[i] : nombre max de sièges quand on a i+1 rangs
            self.totals = totals

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
            # render.fill('#0f0') # debug, pour voir les limites du render
            canvas = render.canvas()
            poslist, rad = self.seats(self.the_list)
            diam = 1.6*rad
            counter=0
            for p in self.the_list:
                for kant in range(counter, counter+p[0]):
                    canvas.circle(renpy.color.Color(p[1]), # the color
                                  (poslist[kant][0]*height, (1-poslist[kant][1])*height), # the centre
                                  height*diam/2, # the radius
                                  )
                counter = kant+1
            return render
            canvas.circle(renpy.color.Color("#F00"), # the color
                          (width/2, height/2), # the centre
                          40, # the radius
                          width=0 # width - 0 is filled, else linewidth of drawn circle
                          )
            return render

        def seats(self, the_list, **properties):
            # the_list : liste de tuples
            # tuple : nombre de sièges, couleur
            sumdelegates = 0
            # addition des sièges et vérifications défensives
            for p in the_list:
                if len(p)!=2 or type(p[0]) is not int:
                    return None
                sumdelegates += p[0]
                if sumdelegates>self.totals[-1]:
                    return None
            if not sumdelegates:
                return None
            # détermination du nombre de rangées
            for i in range(len(self.totals)):
                if self.totals[i] >= sumdelegates:
                    rows = i+1
                    break
            # définition du rayon maximal des cercles
            rad = 1/float(4*rows-2)
            # listage des centres des cercles
            poslist = []
            # pour chaque rangée
            for r in range(1, rows+1):
                # rayon de la rangée
                R = .5 + 2*(r-1)*rad
                # nombre de sièges sur cette rangée
                if r==rows:
                    J = sumdelegates-len(poslist)
                elif sumdelegates in {3, 4}:
                    # place tous les sièges au dernier rang, pas indispensable mais plus joli
                    continue
                else:
                    # taux de remplissage général (par rapport au totals correspondant) fois le maximum de la rangée
                    J = int(float(sumdelegates) / self.totals[rows-1] * math.pi*R/(2*rad))
                if J==1:
                    poslist.append([math.pi/2.0, 1.0, R])
                else:
                    for j in range(J):
                        # angle de position du siège
                        angle = float(j) * (math.pi-2.0*math.asin(rad/R)) / (float(J)-1.0) + math.asin(rad/R)
                        # position par rapport au président de l'hémicycle (y+ vers le haut)
                        poslist.append([angle, R*math.cos(angle)+1.0, R*math.sin(angle)])
            # on range les points par angle croissant de gauche à droite
            poslist.sort(reverse=True)
            return [po[1:] for po in poslist], rad

    def newarch(the_list, *args, **kwargs):
        return At(Newarch(the_list, *args, **kwargs), Transform(zoom=.5))
