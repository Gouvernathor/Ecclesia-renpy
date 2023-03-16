"""renpy
default actors.opinion_labels = ("Economy", "Environment", "Immigration", "Healthcare", "Culture")
# the labels for the opinions, has no actual impact on the framework's behavior

default actors.nopinions = len(actors.opinion_labels) # 5
# the number of different subjects on which one can have an opinion

default actors.opinmax = 10
# the maximum value of an opinion on a subject (min = -max)

default actors.opinion_alignment_factors = None
# a list of factors for the alignment calculation, one for each opinion
# if None, it's a decreasing series such that factors[0] = 1

init python in actors:
"""
from collections import defaultdict, OrderedDict, namedtuple
import functools
import math
import store

SQ2 = math.sqrt(2)

def _normal_to_uniform(x, mu, sigma):
    """
    From a x value generated from a normal distribution with mean mu and standard deviation sigma,
    returns the corresponding value in a uniform distribution between 0 and 1.
    """
    return .5 * (1 + math.erf((x-mu) / (sigma*SQ2)))

def _get_alignment(opinions):
    """
    From a list of opinion values, returns the alignment of the actor,
    as a floating-point number between 0 and 1.
    """
    assert all(-opinmax <= o <= opinmax for o in opinions)
    factors = opinion_alignment_factors
    if factors is None:
        # factors = [1/(2**i) for i in range(nopinions)]
        factors = [1-i/(nopinions) for i in range(nopinions)]
    scapro = sum(opinions[i]*factors[i] for i in range(nopinions))
    ran = range(-opinmax, opinmax+1)
    one_sigma = math.sqrt(sum(x**2 for x in ran) / len(ran)) # standard dev of one opinion taken solo
    sigma = math.hypot(*(one_sigma*fac for fac in factors)) # using Lyapunov's central limit theorem
    rv = _normal_to_uniform(scapro, 0, sigma)
    return rv

def house_election_check(houzes=None, elapsed=0):
    """
    Takes an iterable of Houses, or the existing ones.
    Returns a list of the houses having an election when `elapsed` months have passed.
    """
    if houzes is None:
        houzes = list(store.houses)
        houzes.append(store.executive)
    return [h for h in houzes if not (elapsed%h.election_period)]

@renpy.pure
class Vote(namedtuple("Vote", ("votes_for", "votes_against"))):
    """
    The results of a House vote.
    The blank votes are not counted. To calculate a threshold on the whole number of members,
    use `vote.votes_for / house.seats`. To calculate the threshold on the number of duly elected
    members, use `vote.votes_for / sum(house.members.values())`.
    """
    __slots__ = ()

    __lt__ = __gt__ = __le__ = __ge__ = lambda self, other: NotImplemented

    def __neg__(self):
        """
        Returns the reverse of the vote, inverting the for/against ratio.
        Simulates a vote on the opposite motion.
        """
        return type(self)(self.votes_against, self.votes_for)

    @property
    @functools.lru_cache
    def votes_cast(self):
        return sum(self)

    @property
    @functools.lru_cache
    def ratio(self):
        """
        Returns the ratio of votes for over the total of votes cast.
        If there are no votes cast, returns a nan.
        """
        if not self.votes_cast:
            return float("nan")
        return self.votes_for / self.votes_cast

    @staticmethod
    def order(*votes):
        """
        Returns the votes in order of decreasing ratio.
        The ties are ordered by decreasing number of positive votes,
        then by the order they came in.
        """
        return sorted(votes, key=(lambda v:(-v.ratio, -v.votes_for)))

class House:
    """
    A whole House, in which all members have the same voting power.
    """
    def __init__(self, name,
                       circos,
                       members=None,
                       election_period=48, # durée en mois
                       majority=.5,
                       ):
        self.name = name
        self.circos = circos
        # list of tuples (nseats, electionmethod, [citizens]) for each circo
        if members is None:
            members = {None : self.seats}
        self.members = members
        # dict of {party : nseats}
        self.election_period = election_period
        self.majority = majority
        # ratio required for a vote to be considered successful

    @property
    def seats(self):
        return sum(c[0] for c in self.circos)

    def displayable(self, *args, **kwargs):
        """
        To customize this, use a subclass.
        """
        liste = [(nmembers, getattr(parti, "color", "#000")) for parti, nmembers in self.members.items() if nmembers]
        return store.Newarch(liste, *args, **kwargs)

    def election(self):
        """
        Triggers an election in each circo (electoral district), and joins the
        results in self.members
        """
        joined_results = defaultdict(int)
        for _nseats, elect_meth, pool in self.circos:
            if (pool is None) or (pool == "people"):
                pool = store.citizenpool
            if isinstance(pool, House):
                pool = (pool,)
            if isinstance(pool, (list, tuple)) and isinstance(pool[0], House):
                hs = pool
                pool = defaultdict(int)
                for h in hs:
                    for p, n in h.members.items():
                        pool[p] += n
            for party, nseats in elect_meth.election(pool):
                joined_results[party] += nseats
        self.members = OrderedDict(sorted(joined_results.items(), key=(lambda x:x[0].alignment)))
        return self.members

    def vote(self, ho:HasOpinions):
        """
        Simulates a vote on `ho`.
        Returns a Vote.
        """
        votes_for = 0
        votes_against = 0
        for party, nseats in self.members.items():
            disag = party ^ ho
            if disag < .5:
                votes_for += nseats
            else:
                votes_against += nseats
        return Vote(votes_for, votes_against)

    def vetoverride(self, bill, thresh):
        """
        Returns whether the bill has enough support for the veto to get overridden.
        """
        return self.vote(bill).ratio >= thresh

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r}>"

class Executive(House):
    """
    The executive branch.
    Its internal behavior (same as an ordinary House), and its legislative powers.
    """
    def __init__(self, origin, # who elects it, a House or an iterable of Houses or "people"
                       vetopower, # whether it has a veto power
                       vetoverride=False, # who can override it (False or an iterable of House or "joint")
                       supermajority=.5, # the qualified majority required to override the veto
                       election_period=None,
                       *,
                       circos, # if an int, interpreted as the number of seats
                       **kwargs):
        if election_period is None:
            if isinstance(origin, House):
                election_period = origin.election_period
            else:
                election_period = 60
        if isinstance(circos, int):
            circos = [[circos,
                       store.election_method.ElectionMethod(store.voting_method.SingleVote(),
                                                            store.attribution_method.HighestAverages(nseats=circos)),
                       origin]]
        super().__init__(circos=circos, election_period=election_period, **kwargs)
        self.origin = origin
        self.vetopower = vetopower
        self.vetoverride = vetoverride
        self.supermajority = supermajority

    def veto(self, bill):
        """
        Returns whether the bill is vetoed by the executive.
        """
        if not self.vetopower:
            return False

        return self.vote(bill).votes_against/self.seats > self.majority

class HasOpinions:
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

    # functions taking two tuples of length nopinions and value between -opinmax and +opinmax
    # and returning a value between 0 and 1

    @staticmethod
    @functools.lru_cache
    def _symmetric_diff(op_a, op_b):
        """
        Typically for comparing HasOpinions of the same type.
        """
        return sum(abs(a-b) for a, b in zip(op_a, op_b)) / (nopinions*2*opinmax)

    @staticmethod
    @functools.lru_cache
    def _pondered_diff(op_a, op_b):
        """
        The second operand is the one ponderating the difference.
        It's the one whose point of view we're taking, the "most human" of the two.
        """
        return sum(abs((a-b)*b) for a, b in zip(op_a, op_b)) / (nopinions*2*opinmax**2)

    @staticmethod
    @functools.lru_cache
    def _frommax_diff(op_a, op_b):
        """
        The second operand is the "most human", the one whose point of view we're taking.
        This simulates agreeing plainly with laws that aren't going far enough, but
        disagreeing with laws that go too far, or which go the wrong way.
        For each opinion:
            if A's opinion a is of the opposite sign as B's b, it goes "the wrong way"
                the difference is abs(a)*abs(b)
            if A's opinion a is of the same sign as B's b but closer to 0, it "doesn't go far enough"
                the difference is 0
            otherwise, it "goes too far"
                the difference is abs(a-b)
        """
        rv = []
        for a, b in zip(op_a, op_b):
            absa = abs(a)
            absb = abs(b)
            if a*b <= 0:
                rv.append(absa*absb)
            elif absa < absb:
                rv.append(0)
            else:
                rv.append(abs(a-b))
        return sum(rv) / (opinmax**2*nopinions)

class Bill(HasOpinions):
    """
    A bill, subject to votes from Houses and vetos by the executive.
    """
    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

    def __repr__(self):
        # id_ = super().__repr__().rpartition(" at ")[2][:-1]
        # return f"<{type(self).__name__} {id_}, {self.name!r}>"
        return f"<{type(self).__name__} {id(self):0>8}, {self.name!r}>"

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
            return self._symmetric_diff(tuple(self.opinions), tuple(other.opinions))
        if isinstance(other, Bill):
            return self._frommax_diff(tuple(other.opinions), tuple(self.opinions))
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
            return self._pondered_diff(tuple(self.opinions), tuple(other.opinions))
        if isinstance(other, Party):
            return self._symmetric_diff(tuple(self.opinions), tuple(other.opinions))
        if isinstance(other, Bill):
            return self._frommax_diff(tuple(other.opinions), tuple(self.opinions))
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

        ops = [[] for _k in range(npartis)]
        for opn, polln in enumerate(poll):
            for pn in range(npartis):
                pn -= opn%npartis
                # a different party goes first for each opinion
                # that is, if there are more opinions than parties, but even if not,
                # at least it won't always be the same party
                opval, = random.choices(tuple(polln), polln.values())
                ops[pn].append(opval)
                polln[opval] //= 2 # malus for ideas already chosen
        partis = sorted((cls(lpartynamepool[i], opinions=ops[i]) for i in range(npartis)),
                        key=lambda p:p.alignment)
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
