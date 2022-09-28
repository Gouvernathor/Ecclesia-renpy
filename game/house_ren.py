"""renpy

default actors.nopinions = 5
# the number of different subjects on which one can have an opinion

default actors.opinmax = 10
# the maximum value of an opinion on a subject (min = -max)

default actors.opinion_alignment_factors = None
# a list of factors for the alignment calculation, one for each opinion
# if None, it's a decreasing series such that Un+1 = Un/2

init python in actors:
"""
from collections import defaultdict, OrderedDict
import store

def _get_alignment(opinions):
    """
    From a list of opinion values, returns the alignment of the actor,
    as a floating-point number between 0 and 1.
    """
    assert all(-opinmax <= o <= opinmax for o in opinions)
    factors = opinion_alignment_factors
    if factors is None:
        # factors = [1/(2**i) for i in range(nopinions)]
        factors = [1-i/(nopinions-1) for i in range(nopinions)]
    sm = sum(opinions[i]*factors[i] for i in range(nopinions))
    mx = opinmax*sum(factors)
    return (sm + mx) / (2 * mx)

def house_election_check(houzes=None, elapsed=0):
    """
    Takes an iterable of Houses, or the existing ones.
    Returns a list of the houses having an election when `elapsed` months have passed.
    """
    if houzes is None:
        houzes = list(store.houses)
        if store.executive.origin == "people":
            houzes.append(store.executive)
    return [h for h in houzes if not (elapsed%h.election_period)]

class House:
    """
    A whole House, in which all members have the same voting power.
    """
    def __init__(self, name,
                       nseats,
                       election_period=48, # durée en mois
                       display=None,
                       majority=.5,
                       ):
        self.name = name
        self.circos = ((nseats, None, ()),)
        # list of tuples (nseats, electionmethod, [citizens]) for each circo
        self.members = {None : self.seats}
        # dict of {party : nseats}
        self.election_period = election_period
        if display is None:
            display = store.newarch
        self.display = display
        self.majority = majority

    @property
    def seats(self):
        return sum(c[0] for c in self.circos)

    def classes(self):
        """
        Converts the different circos to a {(nseats, electionmethod) : number} format.

        The (nseats, electionmethod) tuples are considered to be classes inside
        the House, such that members from the same class are elected the same
        way (albeit not from the same place) and members from different classes
        are elected differently (albeit possibly from the same voters).
        """
        clss = defaultdict(int)
        for nseats, meth, *_o in self.circos:
            clss[nseats, meth] += 1
        return dict(clss)

    def displayable(self, *args, **kwargs):
        liste = [(nmembers, getattr(parti, "color", "#000")) for parti, nmembers in self.members.items() if nmembers]
        return self.display(liste, *args, **kwargs)

    def election(self):
        """
        Triggers an election in each circo (electoral district), and joins the
        results in self.members
        """

        joined_results = defaultdict(int)
        for _nseats, elect_meth, pool in self.circos:
            for party, nseats in elect_meth.election(pool):
                joined_results[party] += nseats
        self.members = OrderedDict(sorted(joined_results.items(), key=(lambda x:x[0].alignment)))
        return self.members

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r}>"

class Executive(House):
    """
    The executive branch.
    Its internal behavior (same as an ordinary House), and its legislative powers.
    """
    def __init__(self, origin, # who elects it, a House or "people"
                       vetopower, # whether it has a veto power
                       vetoverride=False, # who can override it (False or an iterable of House or "joint")
                       supermajority=.5, # the qualified majority needed to override the veto
                       election_period=None,
                       *args,
                       **kwargs):
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

    def veto(self, bill):
        """
        Returns whether the bill is vetoed by the executive.
        """
        """
        Un membre de l'exécutif votera pour le veto si le désaccord entre le (parti du) membre
        et la loi est supérieur à la moitié du désaccord maximal.
        2*opinmax*nopinions/2 < sum(abs(parti_du_membre.opinions[l]-bill.opinions[k]) for k in range(nopinions) if bill.has_opinion[k])
        """
        if not self.vetopower:
            return False

        raise NotImplementedError

class HasOpinions: # type: ignore
    """
    A mixin class for objects that have opinions on subjects.
    """
    def __init__(self, opinions=None, *,
                       randomobj=None,
                       randomkey=None,
                       ):
        if opinions is None:
            if randomobj is None:
                randomobj = renpy.random.Random(randomkey)
            opinions = randomobj.choices(range(-opinmax, opinmax+1), k=nopinions)
            # opinions is a list of integers between -opinmax and opinmax
            # the length of the list is nopinions
            # each element is about a closed question on a certain subject
            # opinmax is totally agree, -opinmax is totally disagree, 0 is neutral
        self.opinions = opinions

        if type(self) is HasOpinions:
            raise TypeError("HasOpinions is an abstract class")

class Bill(HasOpinions):
    """
    A bill, subject to votes from Houses and vetos by the executive.
    """
    def __init__(self, name, opinions, opinion_weights=None):
        self.name = name
        super().__init__(opinions)
        if opinion_weights is None:
            opinion_weights = [1]*nopinions
        self.opinion_weights = opinion_weights # WIP
        raise NotImplementedError

class Citizen(HasOpinions):
    """
    A voter, used to simplify the election system.
    Comes with its own set of opinions on all the subjects there be.
    These can be set manually, or generated randomly.
    """
    def __xor__(self, other):
        """
        Returns how much `self` and `other` disagree.
        The score is strictly positive, the higher the stronger the disagreement.
        """
        if isinstance(other, Citizen):
            return sum(abs(self.opinions[i]-other.opinions[i]) for i in range(nopinions))
        if isinstance(other, Bill):
            raise NotImplementedError
        return NotImplemented

    __rxor__ = __xor__

class Party(HasOpinions):
    """
    A political party, defending a set of opinions.
    """
    huemax = .75
    # the bluest hue generated colors will go to
    # .66 is blue and .75 is blueish purple

    def __init__(self, name,
                       alignment=None,
                       color=None,
                       *args,
                       **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        if color:
            self.color = store.Color(color)
        elif alignment is not None:
            self.alignment = alignment
        else:
            self.alignment = _get_alignment(self.opinions)

    def __xor__(self, other):
        if isinstance(other, Citizen):
            # weighted, because for the same disagreement, if the citizen cares and the party doesn't,
            # it's worse than if the party cares and the citizen doesn't
            return sum(abs((self.opinions[k]-other.opinions[k])*other.opinions[k]) for k in range(nopinions))
        if isinstance(other, Party):
            raise NotImplementedError
        if isinstance(other, Bill):
            raise NotImplementedError
        return NotImplemented

    __rxor__ = __xor__

    @property
    def alignment(self):
        return self.color.hsv[0] / self.huemax

    @alignment.setter
    def alignment(self, value):
        """
        Takes a 0-1 float
        Turns it into a saturated TSV/HSV color
        Hue (first component) between .0 (red) and .66 (blue) or .75 (blue-purple)
        """
        self.color = store.Color(hsv=(value*self.huemax, 1., 1.))

    @classmethod
    def generate(cls, npartis, pool=None):
        """
        Generates a list of npartis parties, with random opinions.
        """
        partis = []
        if pool is None:
            pool = store.citizenpool
        poll = pollopinions(pool)

        random = renpy.random.Random(store.citikey)
        lpartynamepool = random.sample(partynamepool, npartis)
        random.seed(store.citikey)

        opnvals = tuple(poll[0])
        for _k in range(npartis):
            ops = []
            for opn in range(nopinions):
                ops.append(random.choices(opnvals, poll[opn].values())[0])
            partis.append(cls(lpartynamepool.pop(), opinions=ops))
        partis.sort(key=lambda p: p.alignment)
        return partis

def pollopinions(pool):
    """
    Returns the distribution of every value for every opinion among a list of citizens.
    rv[i][j] is the number of citizens who have opinion j of subject i.
    """
    rv = [dict.fromkeys(range(-opinmax, opinmax+1), 0) for _k in range(nopinions)]
    for citizen in pool:
        for opn, opinion in enumerate(citizen.opinions):
            rv[opn][opinion] += 1
    return rv

"""renpy
define actors.partynamepool = (
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
    )
"""
