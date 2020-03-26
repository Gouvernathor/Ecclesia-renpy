init python:
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

# dans le script, à chaque mois :
# check house_election_check en lui donnant en argument une liste des houses
# parcourir le set d'underhouses renvoyé, en annonçant visuellement un élection (partielle ou non) à chaque underhouse
# puis appeler lolor = [election(population, partis, electype) for electype in uhouse.elect_types]
# assembler les résultats avec sum_results, garder lolor sous la main pour afficher tous les résultats dans un viewport

# _(attrib_function.__name__)
# donne le nom (à traduire, même en lang=None) de la fonction de répartition

    class House():
        '''
        A whole House, in which people all vote with the same power
        Must be supplied one or more UnderHouse instances as children
        '''
        def __init__(self, name, children,
                     display='newarch',
                     impero=False,
                     elect_types=[],
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
            self.display = display
            self.elect_types = elect_types
            # elect_types :
            # liste de tuples (nombre de sièges concernés, fonction de répartition, nombre de sièges par circo)
            # chaque tuple doit avoir une combinaison (fonction de répartition, sièges par circo) unique
            # la somme des nombres de sièges concernés doit être le nombre total de sièges dans la chambre
            # le nombre de sièges par circo doit être un diviseur du nombre de sièges concernés
            # ou 0, et c'est comme si il était égal au nombre de sièges concernés

        def seats(self):
            seat=0
            for uhouse in self.children:
                seat+=uhouse.seats
            return seat

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
