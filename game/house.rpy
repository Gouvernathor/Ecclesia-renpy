define nopinions = 30
define opinrange = 5

init python:
    def house_election_check(houses, elapsed):
        '''
        Prend en paramètres un itérable des Houses du pays
        Renvoie un Set des Houses qui doivent se renouveler
        '''
        # liz = set()
        # for house in houses:
        #     if house.election_period:
        #         for uhouse in house.children:
        #             if elapsed%house.election_period == uhouse.election_offset:
        #                 liz.add(uhouse)
        # return liz
        return [house for house in houses if not elapsed%house.election_period]

# _(attrib_function.__name__)
# donne le nom (à traduire, même en lang=None) de la fonction de répartition

    class House():
        '''
        A whole House, in which people all vote with the same power
        '''
        def __init__(self, name,
                     nseats,
                     election_period=48, # durée en mois
                     display='newarch',
                     majority=.5,
                     ):
            self.name = name
            self.circos = [[nseats, None, []]]
            # circos :
            # liste de (nombre de sièges dans la circo,
            #           fonction d'attribution,
            #           liste de citoyens-représentatifs)
            self.members = {None : self.seats}
            self.election_period = election_period
            self.display = display
            self.majority = majority

        @property
        def seats(self):
            return sum([circo[0] for circo in self.circos])

        def classes(self):
            '''
            Divides the electoral districts in classes,
            where in a class every district elects the same number of people
            The idea is that to elect each class every citizen needs to vote
            Returns a dict of {(nseatspercirco, funk) : ncircos}
            '''
            clss = dict()
            for circo in self.circos:
                if tuple(circo[0:2]) in clss:
                    clss[tuple(circo[0:2])] += 1
                else:
                    clss[tuple(circo[0:2])] = 1
            return clss

        def displayable(self, *args, **kwargs):
            liste = [(self.members[parti], ('#000' if parti is None else parti.color)) for parti in self.members if self.members[parti]]
            return eval(self.display)(liste, *args, **kwargs)

    class Executive(House):
        '''
        The head of the Executive branch,
        and its powers relative to the passing of laws by the parliament
        '''
        def __init__(self,
                     origin, # qui l'élit (une House ou 'people')
                     vetopower, # si il a le droit de veto sur les lois du parlement
                     vetoverride, # qui peut l'override (une House ou 'each' ou 'joint' ou False)
                     supermajority, # la majorité qualifiée nécessaire pour override le veto
                     election_period=None,
                     *args,
                     **kwargs
                     ):
            if election_period is None:
                election_period = origin.election_period if (origin in houses) else 60
            super(Executive, self).__init__(election_period=election_period, *args, **kwargs)
            self.origin = origin
            self.vetopower = vetopower
            self.vetoverride = vetoverride
            self.supermajority = supermajority
        # un membre de l'exécutif votera pour déclencher le veto sur law si
        # 2*opinrange*nopinions/2 < sum([abs(parti_du_membre.opinions[k]-bill.opinions[k]) for k in range(nopinions) if k in bill.opinions.keys()])
        # autrement dit si le désaccord entre le parti du membre et la loi
        # est supérieur à la moitié du désaccord maximal possible

    class Citizen():
        '''
        A representative-citizen, used to simplify the simulation
        Comes with its own set of opinions on all the subjects there be
        These can be set manually,
        or generated from a (given or not) random object
        '''
        def __init__(self,
                     randomobj=renpy.random.Random(),
                     opinions=None,
                     ):
            super(Citizen, self).__init__()
            # self.randomobj = copy.deepcopy(randombj)
            self.opinions = opinions or [randomobj.choice(range(-opinrange, opinrange+1)) for k in range(nopinions)]

    class Party(Citizen):
        '''
        A political party, defending a set of opinions
        '''
        def __init__(self,
                     name,
                     alignment=renpy.random.random(),
                     *args,
                     **kwargs
                     ):
            super(Party, self).__init__(*args, **kwargs)
            self.name = name
            self.alignment = alignment # alignement gauche/droite, implique sa couleur et son classement dans l'hémicycle

        @property
        def color(self):
            '''
            couleur TSV/HSV saturée
            teinte (premier composant) pris entre .0 (rouge) et .66 (bleu) ou .75 (bleu-violet)
            '''
            return Color(hsv=(self.alignment*.75, 1.0, 1.0))
