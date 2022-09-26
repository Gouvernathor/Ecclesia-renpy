define nopinions = 5
define opinmax = 10 # valeur max pour chaque opinion (min = -max)

init python:
    from collections import OrderedDict, defaultdict

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
                     display=None,
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
            if display is None:
                display = newarch
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
            clss = defaultdict(int)
            for circo in self.circos:
                clss[tuple(circo[0:2])] += 1
            return dict(clss)

        def displayable(self, *args, **kwargs):
            liste = [(nmembers, getattr(parti, "color", '#000')) for parti, nmembers in self.members.items() if nmembers]
            return self.display(liste, *args, **kwargs)

        def election(self):
            """
            Renouvelle chaque circonscription de la chambre, et assemble les résultat dans l'attribut members
            """

            def join_results(scores):
                '''
                Assemble les attributions de sièges par circo
                pour donner le score de chaque parti à l'échelle de la Chambre
                Prend en entrée une liste de listes scores
                renvoie un dict {parti:nsièges}
                prêt à être rangé dans house.members
                '''
                members = defaultdict(int)
                for score in scores:
                    for parti, nseats in score:
                        members[parti] += nseats
                return members

            scoress = []
            for _nseats, elect_method, pool in self.circos:
                scoress.append(elect_method.election(pool))
            joinedlist = sorted(join_results(scoress).items(), key=(lambda p:p[0].alignment))
            self.members = OrderedDict(joinedlist)
            return self.members

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
                if isinstance(origin, House):
                    election_period = origin.election_period
                else:
                    election_period = 60
            super().__init__(*args, election_period=election_period, **kwargs)
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
            super().__init__()
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
            super().__init__(*args, **kwargs)
            self.name = name
            if color:
                self.color = Color(color)
            elif alignment is not None:
                self.alignment = alignment # utilise le setter
                # alignement gauche/droite, implique sa couleur et son classement dans l'hémicycle
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
        def alignment(self):
            '''
            Accepte un flottant entre 0 et 1
            Transformation en une couleur TSV/HSV saturée
            Teinte (premier composant) pris entre .0 (rouge) et .66 (bleu) ou .75 (bleu-violet)
            '''
            return self.color.hsv[0]/.75

        @alignment.setter
        def alignment(self, value):
            self.color = Color(hsv=(value*.75, 1.0, 1.0))

    def pollopinions(pool):
        gathered = [[0]*(2*opinmax+1) for _k in range(nopinions)]
        for cit in pool:
            for k in range(nopinions):
                gathered[k][cit.opinions[k]+opinmax] += 1
                # c'est décalé de -mx à +max, à de 0 à 2*max
        return gathered

    def generate_partis(npartis):
        '''
        Adds `npartis` partis to the list of partis
        Does not replace the existing ones
        '''
        global partis
        partis = []
        poll = pollopinions(citizenpool)
        lpartynamepool = partynamepool+(npartis-21)*[_("")]
        renpy.random.shuffle(lpartynamepool)
        randomobj = renpy.random.Random(citikey)
        for _k in range(npartis): # choix random pondéré pour chaque sujet
            ops = []
            for nop in range(nopinions):
                ops.append(randomobj.choices(range(2*opinmax+1), poll[nop])[0])
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
    _("Democratic Movement"), # MoDem
    _("Union for the New Republic"), # UNR
    _("Gathering For the Republic"), # RPR
    _("Union of the Independant Right"), # UDI
    _("National Front"), # FN
    _("National Gathering"), # RN
    _("Pirate Party"),
    _("Communist Party"),
    _("Socialist Worker's Party"), # PSO(E)
    _("New Anti-capitalist Party"), # NPA
    _("Independant Worker's Party"), # POI
    _("Workers' Struggle"), # LO
    _("Constitution Party"),
    _("Libertarian Party"),
    _("Northern League"),
    _("Five-Stars Movement"), # M5S
    ]
