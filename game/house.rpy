define nopinions = 30
define opinmax = 100 # valeur max pour chaque opinion (min = -max)

init python:
    def house_election_check(houzes=None, elapsed=None):
        '''
        Prend un itérable des Houses du pays et un nombre de mois écoulés
        Renvoie un Set des Houses qui doivent se renouveler ce mois-ci
        '''
        if houzes is None:
            houzes = houses[:]
            if executive.origin == 'people':
                houzes.append(executive)
        if elapsed is None:
            elapsed = 0
        return [house for house in houzes if not elapsed%house.election_period]

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
        # 2*opinmax*nopinions/2 < sum([abs(parti_du_membre.opinions[k]-bill.opinions[k]) for k in range(nopinions) if k in bill.opinions.keys()])
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
            self.opinions = opinions or [randomobj.choice(range(-opinmax, opinmax+1)) for k in range(nopinions)]

        def disagree(self, other):
            '''
            Compares the opinions between two citizens.
            The score is strictly positive, the higher the stronger the disagreement
            '''
            if not issubclass(type(self), type(other)):
                # equivalent to isstrictsubclass(type(other), type(self))
                return other.disagree(self)

            return sum([abs(self.opinions[k]-other.opinions[k]) for k in range(nopinions)])
            # différence symétrique si les deux sont de même nature


    class Party(Citizen):
        '''
        A political party, defending a set of opinions
        If a color is given, the alignment parameter is ignored
        '''
        def __init__(self,
                     name,
                     alignment=None,
                     color=None,
                     *args,
                     **kwargs
                     ):
            super(Party, self).__init__(*args, **kwargs)
            self.name = name
            if color:
                self.color = color # utilise le setter
            elif alignment is not None:
                self.alignment = alignment # alignement gauche/droite, implique sa couleur et son classement dans l'hémicycle
            else:
                self.alignment = renpy.random.random()

        def disagree(self, other):
            if not isinstance(other, Party):
                # si les deux ne sont pas des partis
                # consider the value for each subject as how much the citizen's opinion is fervent on the subject
                # so if the citizen doesn't care and the party cares very much,
                # it's less of a disagreement than if the citizen cares very much and the party doesn't !
                # maybe multiply the difference between the two by the absolute magnitude of the opinion ?
                # *abs(citizen.opinion[k])
                return sum([abs((self.opinions[k]-other.opinions[k])*other.opinions[k]) for k in range(nopinions)])

            return super().disagree(other)

        @property
        def color(self):
            '''
            couleur TSV/HSV saturée
            teinte (premier composant) pris entre .0 (rouge) et .66 (bleu) ou .75 (bleu-violet)
            '''
            return Color(hsv=(self.alignment*.75, 1.0, 1.0))

        @color.setter
        def color(self, value):
            value = Color(value)
            self.alignment = (value.hsv[0]/.75)

    def pollopinions(pool):
        gathered = [[0 for k in range(2*opinmax+1)] for k in range(nopinions)]
        for cit in pool:
            for k in range(nopinions):
                gathered[k][cit.opinions[k]+opinmax] += 1
                # c'est décalé de -mx à +max à 0 à 2*max
        return gathered

    def weighted_choice(choices, probs=None, randomobj=renpy.random.Random()):
        '''
        Weighted random choice between the first element of each element of `choices`
        It's also possible to give a list of possibilities as `choices` and a list of weights as `probs`
        In that case, any exceeding weight is ignored, and any missing weight is assumed to be 0
        '''
        if probs:
            choices = zip(choices, probs)
        total = sum(w for c, w in choices)
        r = randomobj.uniform(0, total)
        # print(choices)
        for c, w in choices:
            r -= w
            if 0 > r:
                return c
        raise Exception("Shouldn't get here")

    def generate_partis(npartis):
        '''
        Adds `npartis` partis to the list of partis
        Does not replace the existing ones
        '''
        poll = pollopinions(citizenpool)
        lpartynamepool = partynamepool+(npartis-21)*[_("")]
        renpy.random.shuffle(lpartynamepool)
        randomobj = renpy.random.Random(citikey)
        for k in range(npartis): # choix random pondéré pour chaque sujet
            ops = []
            for nop in range(nopinions):
                ops.append(weighted_choice(range(2*opinmax+1), poll[nop], randomobj))
            partis.append(Party(lpartynamepool.pop(), opinions=ops, alignment=randomobj.random()))
        partis.sort(key=lambda p:p.alignment)
        # sinon choix pondéré avec les opinions déjà prises par les autres partis ?

define partynamepool = [
    _("Liberal-Democrat Party"),
    _("Liberal-Conservative Party"),
    _("Socialist Party"),
    _("Democratic Party"),
    _("People's Party"),
    _("Republican Party"),
    _("Freedom Party"),
    _("Green Party"),
    _("Good Old Party"),
    _("Democratic Movement"),
    _("Union for the New Republic"),
    _("Gathering For the Republic"),
    _("Union of the Independant Right"),
    _("National Front"),
    _("National Gathering"),
    _("Pirate Party"),
    _("Communist Party"),
    _("Socialist Worker's Party"),
    _("New Anti-capitalist Party"),
    _("Independant Worker's Party"),
    _("Workers' Struggle"),
    _("Constitution Party"),
    _("Libertarian Party"),
    _("Northern League"),
    _("Five-Stars Movement"),
    ]
