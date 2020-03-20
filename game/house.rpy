init python:
    def proportional(): # fonction pour électon proportionnelle
        # TODO
        return None

    def house_election_check(houses, elapsed):
        '''
        Prend en paramètres un itérable des Houses du pays
        Renvoie un Set des UnderHouses qui doivent se renouveler
        '''
        liz = set()
        for house in houses:
            if house.election_period:
                for uhouse in house.children:
                    if elapsed%house.election_period == uhouse.election_offset:
                        liz.add(uhouse)
        return liz

    class House():
        '''
        A whole House, in which people all vote with the same power
        Must be supplied one or more UnderHouse instances as children
        '''
        def __init__(self, name, children,
                     display='newarch',
                     impero=False,
                     elect_type=proportional,
                     election_period=48 # durée en mois
                     ):
            self.name = name
            self.children = []
            if not len(children):
                raise IndexError(_("There must be at least one UnderHouse as child."))
            for uhouse in children:
                if uhouse.election_offset not in range(election_period):
                    # si l'offset n'est pas entre 0 inclus et la période exclue
                    uhouse.election_offset %= election_period
                self.children.append(uhouse)
            self.impero = impero
            self.election_period = election_period
            self.elect_type = elect_type
            self.display = display

        def seats(self):
            seat=0
            for uhouse in self.children:
                seat+=uhouse.seats
            return seats

    class UnderHouse():
        '''
        Each UnderHouse has its own delegates,
        and each (normally) have a different election_offset,
        so that it is renewed in a round-robin manner.
        The election period is given by the motherHouse
        '''
        def __init__(self,
                     seats=100,
                     election_offset=0 # durée en mois
                     ):
            if seats<=0:
                raise ValueError(_("The number of seats must be a positive integer"))
            self.seats = seats
            self.election_offset = election_offset
