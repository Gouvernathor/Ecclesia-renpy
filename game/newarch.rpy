default maxrows = 75

init python:
    import math

    class Newarch(renpy.Displayable):
        '''
        Custom Displayable
        Zoom .5 to have the real size
        Not to use directly, use the newarch function as a handler proxy
        '''
        def __init__(self, the_list, bg=False, **kwargs):
            super(Newarch, self).__init__(**kwargs)
            self.the_list = the_list
            self.bg = bg
            self.totals = totals

        def render(self, width, height, st, at):
            width*=2
            height*=2
            if width>2*height:
                width=2*height
            else:
                height=width/2
            render = renpy.Render(width, height)
            # render.fill('#0f0') # debug, pour voir les limites du render
            if self.bg:
                render.fill(self.bg)
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
                if len(p)<2:
                    raise IndexError(_("The number of seats and the color must be supplied for each party."))
                    # Le nombre de siège et la couleur doivent être fournis pour chaque parti
                if type(p[0]) is not int:
                    raise TypeError(_("The number of seats must be an integer."))
                    # Le nombre de sièges doit être un entier
                sumdelegates += p[0]
                if sumdelegates>self.totals[-1]:
                    # raise ValueError(_("More than [self.totals[-1]] seats have been supplied"))
                    raise ValueError(_("Too much seats (more than {}) have been supplied. Consider increasing the maxrows variable.").format(self.totals[-1]))
            if not sumdelegates:
                raise ValueError(_("There are no delegate seats to be found."))
                # Aucun siège n'a été trouvé
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

label after_load:
    python:
        totals = []
        for rows in range(1, maxrows):
            tot = 0
            rad = 1/float(4*rows-2)
            for r in range(1, rows+1):
                R = .5 + 2*(r-1)*rad
                tot += int(math.pi*R/(2*rad))
            totals.append(tot)
        # totals[i] : nombre max de sièges quand on a i+1 rangs
