"""renpy
init python in attribution_method:
"""
from statistics import fmean

class SainteLagueBase(Proportional):
    # __slots__ = ("threshold")
    name = _("Proportional (largest averages)")

    threshold = 0 # remove

    def attrib(self, results):
        if self.threshold:
            results_ = results
            thresh = self.threshold * sum(results.values())
            results = {p:s for p, s in results.items() if s >= thresh}
            if not results:
                return self.contingency.attrib(results_)

        def key(p):
            ret = results[p]/(rv[p]+.5)
            return ret

        rv = dict.fromkeys(results, 0)
        for _k in range(self.nseats):
            win = max(results, key=key)
            rv[win] += 1
        return [(p, s) for p, s in rv.items() if s]

class Pavia1(Proportional):
    name = _("Proportional (Pavia)")

    def attrib(self, results):

        advantage = {} # benefit of rounding up rather than down
        rv = {}
        for p, votes in results.items():
            fair = votes*self.nseats/sum(results.values()) # nombre juste flottant de sièges
            rv[p] = int(fair)
            down_error = (fair%1)/fair # erreur de l'arrondi vers le bas, proportionnellement au nombre (juste) de sièges
            up_error = (1-(fair%1))/fair # erreur de l'arrondi vers le haut, proportionnellement au nombre (juste) de sièges
            advantage[p] = abs(up_error) - abs(down_error)

        winners = sorted(advantage, key=advantage.get)[:(self.nseats-sum(rv.values()))]
        for p in winners:
            rv[p] += 1

        return rv.items()

class Pavia2(Proportional):
    """
    A divisor method which seeks to minimize the average error (across all
    states/candidates) between the theoretical floating-point number of
    seats and the apportioned number of seats, relative to the theoretical
    number of seats.
    """

    name = _("Proportional (Pavia)")

    def attrib(self, results):
        fairs = {p : votes*self.nseats/sum(results.values()) for p, votes in results.items()}
        # fair, floating-point number of seats for each party

        def mean_error(party):
            """
            Returns the mean, between all parties, of the error between the
            theoretical number of seats and the apportioned number of
            seats, if `party` were allocated one more seat.
            """
            return fmean(abs(rv[p]+(party==p)-fairs[p])/fairs[p] for p in rv)

        rv = dict.fromkeys(results, 0)
        for _s in range(self.nseats):
            # find the party which would bring the mean error down the most,
            # were it given one more seat
            win = min(results, key=mean_error)
            rv[win] += 1
        return rv.items()

class Pavia3(Proportional):
    """
    A divisor method which seeks to minimize the average error (across all
    states/candidates) between the theoretical floating-point number of
    seats and the apportioned number of seats, relative to the theoretical
    number of seats.
    """

    name = _("Proportional (Pavia)")

    def attrib(self, results):
        shares = {p : votes/sum(results.values()) for p, votes in results.items()}
        # share, percentage of the vote received by each party

        def relative_error(party, offset=0):
            """
            Returns the relative error, normalized by the fair number of
            seats, of the `party`, if it had `offset` more seats.
            """
            return abs((rv[party]+offset)/self.nseats - shares[party]) / shares[party]

        def relative_error_net_gain(party):
            """
            Returns the gain/loss of relative error if `party` were
            allocated one more seat.
            """
            return relative_error(party, 1) - relative_error(party)

        rv = dict.fromkeys(results, 0)
        for _s in range(self.nseats):
            # find the party which would bring the mean error down the most,
            # were it given one more seat
            win = min(results, key=relative_error_net_gain)
            rv[win] += 1
        return rv.items()

class Pavia4(Proportional):
    """
    A divisor method which seeks to minimize the average error (across all
    states/candidates) between the theoretical floating-point number of
    seats and the apportioned number of seats, relative to the theoretical
    number of seats.
    """
    """
    Here is a more optimized version.
    """

    name = _("Proportional (Pavia)")

    def attrib(self, results):
        shares = {p : votes/sum(results.values()) for p, votes in results.items()}
        # share, percentage of the vote received by each party

        def relative_error(party, offset=0):
            """
            Returns the relative error, normalized by the fair number of
            seats, of the `party`, if it had `offset` more seats.
            """
            share = shares[party]
            return abs((rv[party]+offset)/self.nseats - share) / share

        relative_cache = _dict() # party -> relative net error gain
        def relative_error_net_gain(party):
            """
            Returns the gain/loss of relative error if `party` were
            allocated one more seat.
            """
            ret = relative_cache.get(party, None)
            if ret is None:
                ret = relative_error(party, 1) - relative_error(party)
                relative_cache[party] = ret
            return ret

        rv = dict.fromkeys(results, 0)
        for _s in range(self.nseats):
            # find the party such that giving it one more seat would bring
            # the mean error down the most
            win = min(results, key=relative_error_net_gain)
            del relative_cache[win]
            rv[win] += 1
        return rv.items()

Pavia = Pavia4

"""renpy
init python:
"""
alpha = 'abcdefghijklmnopqrstuvwxyz'

def test_proportionals(it=1000):
    from statistics import mean
    from store.attribution_method import FakeHondt, SainteLagueBase, FakeHare, Pavia

    random = renpy.random.Random()
    solutions = 0
    for _k in range(it):
    # while solutions < 5:
        votes = {l : random.randrange(1000, 100000) for l in alpha[:random.randrange(2, 20)]}
        nseats = random.randrange(10, 100)

        # Stand-up Math's example
        # votes = dict(A=21878, B=9713, C=4167, D=3252, E=1065)
        # nseats = 43

        # breaking example - only because of float rounding errors
        # votes = dict(A=31672, B=55069, C=6314, D=70620, E=84109, F=17645, G=84799, H=22875, I=95016, J=24368, K=59459)
        # nseats = 96

        sumvotes = sum(votes.values())

        meandev = {}
        maxdev = {}
        results = {}
        rtemplate = dict.fromkeys(votes, 0)
        for Attrib in (FakeHondt, SainteLagueBase, FakeHare, Pavia):
            result = dict(Attrib(nseats).attrib(votes))
            meandev[Attrib] = mean(abs(result.get(p, 0)-(j:=votes[p]*nseats/sumvotes))/j for p in votes)
            maxdev[Attrib] = max(abs(result.get(p, 0)-(j:=votes[p]*nseats/sumvotes))/j for p in votes)
            results[Attrib] = rtemplate | result

        # if min(meandev, key=meandev.get) != SainteLagueBase:
        # if (meandev[FakeHare] != meandev[Pavia]) or (meandev[SainteLagueBase] != meandev[Pavia]) or (maxdev[FakeHare] != maxdev[Pavia]) or (maxdev[SainteLagueBase] != maxdev[Pavia]):
        # if (meandev[SainteLagueBase] != meandev[Pavia]) or (maxdev[SainteLagueBase] != maxdev[Pavia]):
        if results[SainteLagueBase] != results[Pavia]:
            solutions += 1
            print("Found solution:")
            # if meandev[FakeHondt] < meandev[SainteLagueBase]:
            #     print("UNEXPECTED : FakeHondt is better than SainteLague")
            # if meandev[FakeHare] < meandev[SainteLagueBase]:
            #     print("UNEXPECTED : FakeHare is better than SainteLague")
            # if meandev[FakeHare] < meandev[FakeHondt]:
            #     print("UNEXPECTED : FakeHare is better than FakeHondt")
            if meandev[Pavia] != min(meandev.values()):
                print(f"UNEXPECTED : Pavia is worse than {min(meandev, key=meandev.get)}, in the mean metric")
            # print(f"votes={dict(sorted(votes.items(), key=votes.get, reverse=True))}")
            # if maxdev[Pavia] > maxdev[FakeHare]:
            #     print("UNEXPECTED : Pavia is worse than Hare")
            # if maxdev[Pavia] > maxdev[SainteLagueBase]:
            #     print("UNEXPECTED : Pavia is worse than SainteLague")
            if maxdev[Pavia] != min(maxdev.values()):
                print(f"UNEXPECTED : Pavia is worse than {min(maxdev, key=maxdev.get)}, in the max metric")
            print(f"{nseats=}")
            print(f"{votes=}")
            print(f"{results=}")
            print(f"{meandev=}")
            print(f"{maxdev=}")

        if solutions >= 5:
            break
    print(f"{solutions=}")

def test_monotonicity(Attrib):
    random = renpy.random.Random()

    votes = {l : random.randrange(1000, 100000) for l in alpha[:random.randrange(2, 20)]}
    former_result = {}
    for nseats in range(1, 2000):
        if not (nseats % 100):
            print(f"{nseats=}")
        result = dict(Attrib(nseats).attrib(votes))
        for party in votes:
            if result.get(party, 0) < former_result.get(party, 0):
                print(f"{Attrib} is not monotonic")
                print(f"{votes=}")
                print(f"For {nseats} seats, {result=}")
                print(f"For {nseats-1} seats, {former_result=}")
                return
        former_result = result
    print(f"{Attrib} is (probably) monotonic")

from math import ceil

def test_quota(Attrib, tries=1):
    """
    Warning : this is not efficient at all (a lot of false negatives)
    """
    random = renpy.random.Random()

    lower = upper = True
    for _k in range(tries):
        votes = {l : random.randrange(1000, 100000) for l in alpha[:random.randrange(2, 20)]}
        allvotes = sum(votes.values())
        for nseats in range(1, 2000):
            if not (nseats % 100):
                print(f"{nseats=}")
            result = dict(Attrib(nseats).attrib(votes))
            for party in votes:
                if lower and (result.get(party, 0) < int(votes[party]*nseats/allvotes)):
                    lower = False
                    print(f"{Attrib=} violates lower quota rule")
                    print(f"{votes=}")
                    print(f"For {nseats} seats, {result=}")
                if upper and (result.get(party, 0) > ceil(votes[party]*nseats/allvotes)):
                    upper = False
                    print(f"{Attrib=} violates upper quota rule")
                    print(f"{votes=}")
                    print(f"For {nseats} seats, {result=}")
                    print(f"Party {party} has {votes[party]*nseats/allvotes} fair seats")
                if not (lower or upper):
                    return
    if lower and upper:
        print(f"{Attrib} (probably) respects the quota rule")
