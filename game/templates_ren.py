"""renpy
init python in templates:
"""
_constant = True

from collections import namedtuple
import store
from store.actors import House, Executive, Party, Citizen
from store import voting_method
from store import attribution_method
from store.election_method import ElectionMethod

templates = {}

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
        print("presidential electors pool :", electors.members)

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
                                                #  attribution_method.Plurality(nseats=2)),
                                                 attribution_method.FakeHondt(nseats=2)),
                                  citizenpool[accu:accu+n*ncitizens]])
            accu += ncitizens*n
    # a, b, c = sum((cir[2] for cir in house_circos), start=[]), sum((cir[2] for cir in senate_circos), start=[]), citizenpool[:435*ncitizens]
    # print(f"{a==b=}, {a==c=}, {b==c=}")

    prez_elector_circos = [[(nb:=(len(pool)//ncitizens+2)),
                            ElectionMethod(voting_method.SingleVote(),
                                           attribution_method.Plurality(nseats=nb)),
                                        #    attribution_method.FakeHondt(nseats=nb)),
                            pool] for _2, _em, pool in senate_circos]
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
                          name=_("President"), circos=prez_circos, election_period=48)

    return Template(congress,
                    president,
                    (Party("Republican Party", color="#f00"),
                     Party("Democratic Party", color="#00f")))

