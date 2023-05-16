import renpy
from store import _
python_object = object

"""renpy
init python in templates:
"""
_constant = True

from collections import namedtuple, defaultdict, Counter
from itertools import combinations
from math import lcm as ppcm
import store
from store.actors import House, Executive, Party, Citizen
from store import voting_method
from store import attribution_method
from store.election_method import ElectionMethod

templates = {}
# {translatable name : function (number of electors per smallest district -> (houses, executive, partis))}

class stor_deco(python_object):
    def __init__(self, key):
        self.key = key
    def __call__(self, fun):
        templates[self.key] = fun
        return fun

Template = namedtuple("Template", ("houses", "executive", "parties"), defaults=(None,))

class USPrezElection(python_object):
    def __init__(self, circos, senate):
        self.circos = circos
        self.senate = senate

    def election(self, _pool):
        electors = House("Great Electors of the POTUS", self.circos, election_period=48)
        pool = [p for p, mul in electors.election().items() for _k in range(mul)]
        # print("presidential electors pool :", electors.members)

        true_elect = ElectionMethod(voting_method.SingleVote(),
                                    attribution_method.SuperMajority(nseats=1, threshold=.5))

        # rez = true_elect.voting_method.vote(pool)
        try:
            return true_elect.election(pool)
            # return true_elect.attribution_method.attrib(rez)
        except AttributeError:
            print("Normal election failed, contingency election by the Senate")

            pool = [p for p, mul in self.senate.members.items() for _k in range(mul)]
            contingency = ElectionMethod(voting_method.SingleVote(),
                                         attribution_method.Plurality(nseats=1))
            return contingency.election(pool)

ElectionMethod.register(USPrezElection)

@stor_deco(_("United States"))
def us(ncitizens, **kwargs):
    """
    The Senate is renewed in its integrality every 6 years, instead of by thirds every 2 years.
    Nebraska and Maine's special way of alotting electors for presidential election is also ignored
    and replaced with winner-takes-all.
    All House seats are filled using plurality single-turn elections (no runoffs).
    The presidential contingency election is done by the Senate, not the House-by-state-delegation,
    because it's simpler to implement and relatively equivalent.
    Other than that, it's pretty accurate - apart from the random generation of citizens of course.
    """
    randomobj = renpy.random.Random(store.citikey)
    citizenpool = [Citizen(randomobj=randomobj) for _k in range(ncitizens*436)]
    # 435 for the representatives + 1 for DC
    store.citizenpool = citizenpool

    house_circos = [[1,
                     ElectionMethod(voting_method.SingleVote(),
                                    attribution_method.Plurality(nseats=1)),
                     citizenpool[ncitizens*i:ncitizens*(i+1)]]
                    for i in range(435)]
    # print(f"citizens per representative : {[len(el[2]) for el in house_circos]} ({ncitizens=}, {len(citizenpool)=})")

    # number of representatives per states, and their multiplicity, following the 2020 census
    reps_per_state = ((52, 1), (38, 1), (28, 1), (26, 1), (17, 2), (15, 1), (14, 2),
                      (13, 1), (12, 1), (11, 1), (10, 1), (9, 4), (8, 5), (7, 2),
                      (6, 3), (5, 2), (4, 6), (3, 2), (2, 7), (1, 6))

    senate_circos = []
    accu = 0
    for n, mul in reps_per_state:
        for _i in range(mul):
            senate_circos.append([2,
                                  ElectionMethod(voting_method.SingleVote(),
                                                 attribution_method.Plurality(nseats=2)),
                                                #  attribution_method.FakeHondt(nseats=2)),
                                  citizenpool[accu:accu+n*ncitizens]])
            accu += ncitizens*n
    # a, b, c = sum((cir[2] for cir in house_circos), start=[]), sum((cir[2] for cir in senate_circos), start=[]), citizenpool[:435*ncitizens]
    # print(f"{a==b=}, {a==c=}, {b==c=}")

    prez_elector_circos = [[(nb:=(len(pool)//ncitizens+2)),
                            ElectionMethod(voting_method.SingleVote(),
                                           attribution_method.Plurality(nseats=nb)),
                                        #    attribution_method.FakeHondt(nseats=nb)),
                            pool]
                           for _2, _em, pool in senate_circos]
    prez_elector_circos.append([3,
                                ElectionMethod(voting_method.SingleVote(),
                                               attribution_method.Plurality(nseats=3)),
                                            #    attribution_method.FakeHondt(nseats=3)),
                                citizenpool[-ncitizens:]]) # DC's electors
    print(f"{len(prez_elector_circos)=}, {[len(cir[2]) for cir in prez_elector_circos]}")

    house = House(_("House of Representatives"), house_circos, election_period=24)
    senate = House(_("Senate"), senate_circos, election_period=72, majority=.6)
    congress = (house, senate)
    prez_circos = [[1, USPrezElection(prez_elector_circos, senate), ()]]
    president = Executive(origin="people", vetopower=True, vetoverride=congress, supermajority=2/3,
                          name=_("President of the United States"), circos=prez_circos, election_period=48)

    return Template(congress,
                    president,
                    (Party("Republican Party", color="#f00"),
                     Party("Democratic Party", color="#00f")))

@stor_deco(_("France (Vth Republic)"))
def vth_rep(ncitizens, **kwargs):
    randomobj = renpy.random.Random(store.citikey)
    senate_pops = (3, 3, 2, 1, 1, 5, 2, 2, 1, 2, 2, 2, 8, 3, 2, 2, 3, 2, 2, 1, 1, 3, 3, 2,
                   2, 3, 3, 3, 3, 4, 3, 5, 2, 6, 4, 4, 2, 3, 5, 2, 2, 2, 4, 2, 5, 3, 2, 2,
                   1, 4, 3, 3, 2, 2, 4, 2, 3, 5, 2, 11, 4, 2, 7, 3, 3, 2, 2, 5, 4, 7, 2, 3,
                   3, 2, 3, 12, 6, 6, 6, 2, 3, 2, 2, 4, 3, 3, 2, 2, 2, 2, 1, 5, 7, 6, 6, 5,
                   3, 2, 2, 4, 2, 2, 2, 1, 1, 1, 1, 12)
    citizenpool = [Citizen(randomobj=randomobj) for _k in range(ncitizens*ppcm(sum(senate_pops), 577))]
    store.citizenpool = citizenpool

    cit_per_dept = len(citizenpool)//577
    cit_per_sen_seat = len(citizenpool)//sum(senate_pops)

    assnat_circos = [[1,
                      ElectionMethod(voting_method.SingleVote(),
                                     attribution_method.Plurality(nseats=1)),
                      citizenpool[cit_per_dept*i:cit_per_dept*(i+1)]]
                     for i in range(577)]
    senat_circos = []
    accu = 0
    for nb in senate_pops:
        if nb < 3:
            attrib = attribution_method.Plurality(nseats=nb)
        else:
            attrib = attribution_method.HighestAverages(nseats=nb)
        senat_circos.append([nb,
                             ElectionMethod(voting_method.SingleVote(),
                                            attrib),
                             citizenpool[accu:accu+nb*cit_per_sen_seat]])
        accu += cit_per_sen_seat*nb

    return Template((House(_("National Assembly"), assnat_circos, election_period=60),
                     House(_("Senate"), senat_circos, election_period=72)),
                    Executive(origin="people",
                              vetopower=False,
                              election_period=60,
                              name=_("President of the Republic"),
                              circos=[[1,
                                       ElectionMethod(voting_method.SingleVote(),
                                                      attribution_method.Plurality(nseats=1)),
                                       citizenpool]]))

def get_coalition(members, max_span=.5):
    """
    From a {party: number of seats} dict (preferably a +Counter),
    determines the coalition of parties that can form a government.
    A coalition needs to have an alignment span of at most `max_span`.
    Among these, the most cohesive coalition uniting the absolute majority of the members wins.
    If none does, the largest coalition in terms of number of members is returned.
    """

    house_pop = sum(members.values())

    def max_disag(coal):
        """
        Use alignment rather than all-subjects disagreement.
        Single-use majorities for bills will use disagreement,
        but governmental majority won't.
        """
        # return max((a ^ b) for a in coal for b in coal)
        return max(abs(a.alignment - b.alignment) for a in coal for b in coal)

    valid_coals = []
    # all coalitions whose span is less than half of the maximum possible disagreement
    for r in range(len(members)):
        for coalition in combinations(members, r+1):
            if max_disag(coalition) < max_span:
                valid_coals.append(frozenset(coalition))
    # print(f"valid : {sorted((max_disag(coal), sorted(p.color for p in coal)) for coal in valid_coals)}")

    maj_coals = tuple(filter((lambda coal : sum(members[p] for p in coal) >= house_pop/2), valid_coals))
    # all coalitions holding an absolute majority of the seats
    # print(f"maj : {sorted((max_disag(coal), sorted(p.color for p in coal)) for coal in maj_coals)}")

    if maj_coals:
        # the most cohesive majority coalition wins
        return min(maj_coals, key=max_disag)
    else:
        # the largest valid coalition wins
        return max(valid_coals, key=(lambda coal : sum(members[p] for p in coal)))

class Coalition(python_object):
    """
    Implements the nomination of an executive from an assembly, elected
    from a coalition rather than from the full house.
    The government coalition is determined by the `get_coalition` function.
    Among it, either a proportional election is done (for nseats > 1),
    or the median party wins the sole seat.
    Passing votingmethod or attributionmethod overrides these default ones.
    """
    __slots__ = ("nseats", "randomobj", "votingmethod", "attributionmethod")

    def __init__(self, nseats, *, votingmethod=None, attributionmethod=None, randomkey=None, randomobj=None):
        self.nseats = nseats
        self.votingmethod = votingmethod
        self.attributionmethod = attributionmethod
        if randomobj is None:
            randomobj = renpy.random.Random(randomkey)
        elif randomkey is not None:
            raise TypeError("Only one of randomobj and randomkey must be provided.")
        self.randomobj = randomobj

    def election(self, pool):
        dipool = Counter(iter(pool))

        win_coal = get_coalition(dipool)

        pool = [p for p, mul in dipool.items() if p in win_coal for _k in range(mul)]
        votingmethod = self.votingmethod
        attributionmethod = self.attributionmethod
        if (self.nseats == 1) and (votingmethod is None) and (attributionmethod is None):
            pool.sort(key=(lambda p : p.alignment))
            winner = pool[len(pool)//2]
            return {winner : 1}
        else:
            if votingmethod is None:
                votingmethod = voting_method.SingleVote()
            if attributionmethod is None:
                attributionmethod = attribution_method.Plurality(nseats=self.nseats, randomobj=self.randomobj)
            return ElectionMethod(votingmethod, attributionmethod).election(pool)

ElectionMethod.register(Coalition)

class WestminsterHouse(House):
    head = None
    # {parti : nseats} or None
    # defaults to one blank seat

    locations = None
    # {parti : "right" or "left" or "center"} or None
    # defaults to auto-computing the govt and the opposition

    _coalcache = (None, None)

    def election(self):
        rv = super().election()
        self.head = self.locations = None
        return rv

    def displayable(self, *args, **kwargs):
        if self.locations:
            locations = self.locations
        else:
            hsh = hash(tuple(self.members.items()))
            if hsh == self._coalcache[0]:
                coal = self._coalcache[1]
            else:
                coal = get_coalition(Counter(self.members))
                self._coalcache = hsh, coal

            locations = defaultdict(lambda : "left")
            for p in coal:
                locations[p] = "right"

        def aline(parti, nmembers):
            loc = locations[parti]

            if self.head:
                nmembers -= self.head.get(parti, 0)

            return nmembers, getattr(parti, "color", "#000"), loc

        liste = [aline(parti, nmembers) for parti, nmembers in self.members.items() if nmembers]

        if self.head is None:
            liste.append((1, "#000", "head"))
        else:
            liste.extend((n, getattr(parti, "color", "#000"), "head")
                         for parti, n in self.head.items())

        return store.Westminster(liste, *args, **kwargs)

@stor_deco(_("United Kingdom"))
def uk(ncitizens, **kwargs):
    """
    The House of Lords is ignored, because... come on.
    """
    randomobj = renpy.random.Random(store.citikey)
    citizenpool = [Citizen(randomobj=randomobj) for _k in range(ncitizens*650)]
    store.citizenpool = citizenpool

    commons_circos = [[1,
                       ElectionMethod(voting_method.SingleVote(),
                                      attribution_method.Plurality(nseats=1)),
                       citizenpool[ncitizens*i:ncitizens*(i+1)]]
                      for i in range(650)]

    commons = WestminsterHouse(_("House of Commons"), commons_circos, election_period=60)

    return Template((commons,),
                    Executive(origin=None,
                              circos=[[1, Coalition(1), commons]],
                              vetopower=False,
                              name=_("Prime Minister"),
                              ),
                    None)

@stor_deco(_("Italy"))
def italia(ncitizens, **kwargs):
    """
    The representatives of the abroad citizens are grouped in a single constituency.
    The number of representatives for the chamber of deputies is 148 instead of 147 for
    the single-member constituencies, and 244 instead of 245 for the proportional one.
    """
    randomobj = renpy.random.Random(store.citikey)
    citizenpool = [Citizen(randomobj=randomobj) for _k in range(ncitizens*(148+1))]
    store.citizenpool = citizenpool

    national, abroad = citizenpool[:-ncitizens], citizenpool[-ncitizens:]

    # 148 single, 244 list prop, 8 list prop abroad
    # 74, 122, 4
    deputato_circos = []
    senato_circos = []
    electo = ElectionMethod(voting_method.SingleVote(),
                            attribution_method.Plurality(nseats=1))
    for k in range(148):
        deputato_circos.append([1, electo, [national[k]]])
        if not k%2:
            senato_circos.append([1, electo, national[k:k+2]])
    deputato_circos.append([244,
                            ElectionMethod(voting_method.SingleVote(),
                                           attribution_method.HighestAverages(nseats=244,
                                                                              randomobj=randomobj,
                                                                              threshold=0.03)),
                            national])
    senato_circos.append([122,
                          ElectionMethod(voting_method.SingleVote(),
                                         attribution_method.HighestAverages(nseats=122,
                                                                            randomobj=randomobj,
                                                                            threshold=0.03)),
                          national])
    deputato_circos.append([8,
                            ElectionMethod(voting_method.SingleVote(),
                                           attribution_method.HighestAverages(nseats=8,
                                                                              randomobj=randomobj)),
                            abroad])
    senato_circos.append([4,
                          ElectionMethod(voting_method.SingleVote(),
                                         attribution_method.HighestAverages(nseats=4,
                                                                            randomobj=randomobj)),
                          abroad])

    deputato = House(_("Chamber of Deputies"), deputato_circos, election_period=60)
    senato = House(_("Senate of the Republic"), senato_circos, election_period=60)
    parlement = (deputato, senato)
    return Template(parlement,
                    Executive(origin="both",
                              vetopower=False,
                              circos=[[16, Coalition(16), parlement]], # 1 president + 15 ministers
                              name=_("Government of the Republic")),
                    None)
