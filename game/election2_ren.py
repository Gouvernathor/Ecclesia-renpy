"""renpy
init 1 python in more_attribution_method:
"""
import functools
from math import sqrt
from operator import mul
from statistics import fmean

from store.attribution_method import *

class MedianScoreOld(Attribution, final=False):
    """
    Unoptimized, and uses the high median.
    """
    __slots__ = ("contingency")
    taken_format = results_format.SCORES
    name = _("Majority judgment (median rating)")

    def __init__(self, *args, contingency=AverageScore, **kwargs):
        super().__init__(*args, **kwargs)
        self.contingency = contingency(*args, **kwargs)

    def attrib(self, results):

        counts = defaultdict(list)
        for parti, tup in results.items():
            for score, qty in enumerate(tup):
                counts[parti].extend([score]*qty)

        for liz in counts.values():
            liz.sort()

        # ballots not voting for a candidate just do not count for that candidate
        winscore = max(liz[len(liz)//2] for liz in counts.values())
        winners = [parti for parti, liz in counts.items() if liz[len(liz)//2] == winscore]

        if len(winners) <= 1:
            return {winners[0] : self.nseats}
        # remove the non-winners
        trimmed_results = {parti:tup for parti, tup in results.items() if parti in winners}
        return self.contingency.attrib(trimmed_results)

class SainteLagueBase(Proportional, final=False):
    # Obsolete, the Webster implementation is better
    # __slots__ = ("threshold", "contingency")
    name = _("Proportional (largest averages)")

    threshold = 0 # remove

    def attrib(self, results):
        if self.threshold:
            results_ = results
            thresh = self.threshold * sum(results.values())
            results = {p:s for p, s in results.items() if s >= thresh}
            if not results:
                return self.contingency.attrib(results_)

        # from fractions import Fraction

        def key(p):
            # ret = Fraction(results[p], Fraction(2*rv[p]+1, 2))
            ret = results[p]/(rv[p]+.5)
            # print(f"- For party {p}, {ret=}")
            return ret

        rv = Counter()
        for _k in range(self.nseats):
            # print(f"Seat n°{_k+1}")
            win = max(results, key=key)
            # print(f"-Winner : {win}")
            rv[win] += 1
            # print(f"Tally : {rv}")
        return rv

class HuntingtonHill(DivisorMethod, final=False):
    __slots__ = ("threshold")
    name = _("Proportional (Huntington-Hill)")

    def __init__(self, *args, threshold=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold

    def divisor(self, k):
        # won't work without initial seats value, causing division by zero
        return sqrt(k*(k+1))

class Pavia1(Proportional, final=False):
    """
    This is actually a Quota-Pavia method.
    """

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

        return rv

class Pavia2(Proportional, final=False):
    """
    A divisor(?) method which seeks to minimize the average error (across all
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
        return rv

class Pavia3(Proportional, final=False):
    """
    A divisor(?) method which seeks to minimize the average error (across all
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
        return rv

class Pavia4(Proportional, final=False):
    """
    A divisor(?) method which seeks to minimize the average error (across all
    states/candidates) between the theoretical floating-point number of
    seats and the apportioned number of seats, relative to the theoretical
    number of seats.
    """
    """
    Here is a more optimized version, using a cache.
    """

    name = _("Proportional (Pavia)")

    def attrib(self, results):
        # from fractions import Fraction
        # shares = {p : Fraction(votes, sum(results.values())) for p, votes in results.items()}
        shares = {p : votes/sum(results.values()) for p, votes in results.items()}
        # share, percentage of the vote received by each party

        def relative_error(party, offset=0):
            """
            Returns the relative error, normalized by the fair number of
            seats, of the `party`, if it had `offset` more seats.
            """
            share = shares[party]
            # return Fraction(abs(Fraction((rv[party]+offset), self.nseats) - share), share)
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
            # print(f"- For party {party}, {ret=}")
            return ret

        rv = dict.fromkeys(results, 0)
        for _s in range(self.nseats):
            # print(f"Seat n°{_s+1}")
            # find the party such that giving it one more seat would bring
            # the mean error down the most
            win = min(results, key=relative_error_net_gain)
            # print(f"-Winner : {win}")
            del relative_cache[win]
            rv[win] += 1
            # print(f"Tally : {rv}")
        return rv

class Pavia5(RankIndexMethod, final=False):
    __slots__ = ()
    name = _("Proportional (Pavia)")

    def rank_index_function(self, t, a):
        h = self.nseats
        # current_prop_error = Fraction(Fraction(a, h) - t, t)
        # prop_error_if_incr = Fraction(Fraction(a+1, h)-t, t)
        # return abs(current_prop_error) - abs(prop_error_if_incr)
        return self._rank_index_function(h, t, a)

    @staticmethod
    @functools.lru_cache
    def _rank_index_function(h, t, a):
        current_prop_error = Fraction(Fraction(a, h) - t, t)
        prop_error_if_incr = Fraction(Fraction(a+1, h)-t, t)
        return abs(current_prop_error) - abs(prop_error_if_incr)

Pavia = Pavia5

"""renpy
init python:
"""
def sum_raw_error(seats, votes):
    """
    Doesn't actually represent anything : what I call "raw error" is not
    actually what Sainte-Laguë tries to minimize.
    """
    all_votes = sum(votes.values())
    h = sum(seats.values())
    zp = [(seats[p], Fraction(votes[p], all_votes)) for p in seats]
    return sum(abs(Fraction(a, h) - t) for a, t in zp)

def sum_prop_error(seats, votes):
    """
    What I'm trying to minimize.
    """
    all_votes = sum(votes.values())
    h = sum(seats.values())
    zp = [(seats[p], Fraction(votes[p], all_votes)) for p in seats]
    return sum(abs(Fraction(Fraction(a, h)-t, t)) for a, t in zp)

alpha = 'abcdefghijklmnopqrstuvwxyz'

def random_votes(n=None, random=renpy.random.Random()):
    if n is None:
        n = random.randrange(5, 27)
    votes = sorted((random.randrange(1, 1_000_000) for _i in range(n)), reverse=True)
    votes = dict(zip(alpha, votes))
    return votes

def test(i, n=None, h=None, limit=None):
    from store.more_attribution_method import Webster, Pavia
    random = renpy.random.Random()
    if limit is None:
        limit = float('inf')
    sh = h

    clss = (
        Webster,
        Pavia,
    )

    found = 0
    for _i in range(i):
        if sh is None:
            h = random.randrange(10, 800)
        votes = random_votes(n)
        results = {}
        for cls in clss:
            results[cls] = cls(h).attrib(votes)
        # if not (results[NotWebster] == results[Webster] == results[Pavia]):
        if results[Pavia] != results[Webster]:
        # if results[NotWebster] != results[Webster]:
        # if results[SimpleNotWebster] != results[NotWebster]:
            found += 1
            print(f"{h=}\n{votes=}")

            for cls, r in results.items():
                print(cls.__name__, ":")
                print(r)
                print("prop. error :", float(sum_prop_error(r, votes)))
                print("raw error :", float(sum_raw_error(r, votes)))

            print()

            if found > limit:
                break

def test_proportionals(it=1000):
    from statistics import mean
    from store.more_attribution_method import DHondt, SainteLagueBase, Hare, Pavia

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
        for Attrib in (DHondt, SainteLagueBase, Hare, Pavia):
            result = dict(Attrib(nseats).attrib(votes))
            meandev[Attrib] = mean(abs(result.get(p, 0)-(j:=votes[p]*nseats/sumvotes))/j for p in votes)
            maxdev[Attrib] = max(abs(result.get(p, 0)-(j:=votes[p]*nseats/sumvotes))/j for p in votes)
            results[Attrib] = rtemplate | result

        # if min(meandev, key=meandev.get) != SainteLagueBase:
        # if (meandev[Hare] != meandev[Pavia]) or (meandev[SainteLagueBase] != meandev[Pavia]) or (maxdev[Hare] != maxdev[Pavia]) or (maxdev[SainteLagueBase] != maxdev[Pavia]):
        # if (meandev[SainteLagueBase] != meandev[Pavia]) or (maxdev[SainteLagueBase] != maxdev[Pavia]):
        if results[SainteLagueBase] != results[Pavia]:
            solutions += 1
            print("Found solution:")
            # if meandev[DHondt] < meandev[SainteLagueBase]:
            #     print("UNEXPECTED : DHondt is better than SainteLague")
            # if meandev[Hare] < meandev[SainteLagueBase]:
            #     print("UNEXPECTED : Hare is better than SainteLague")
            # if meandev[Hare] < meandev[DHondt]:
            #     print("UNEXPECTED : Hare is better than DHondt")
            if meandev[Pavia] != min(meandev.values()):
                print(f"UNEXPECTED : Pavia is worse than {min(meandev, key=meandev.get)}, in the mean metric")
            # print(f"votes={dict(sorted(votes.items(), key=votes.get, reverse=True))}")
            # if maxdev[Pavia] > maxdev[Hare]:
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
            print()

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

def test_sorting(it=1000):
    from itertools import starmap
    from store.more_attribution_method import Hare, DHondt

    random = renpy.random.Random()
    found = 0

    for _k in range(it):
        votes = {l : random.randrange(1000, 100000) for l in alpha[:random.randrange(2, 20)]}
        votes = dict(zip(votes, sorted(votes.values())))
        # allvotes = sum(votes.values())
        nseats = random.randrange(1, 2000)

        hondt = DHondt(nseats).attrib(votes)
        hare = Hare(nseats).attrib(votes)

        cumul_hare = sum(starmap(mul, enumerate(hare.values())))
        cumul_hondt = sum(starmap(mul, enumerate(hondt.values())))
        if cumul_hare > cumul_hondt:
            found += 1
            print(f"Hondt favors smaller parties over Hare")
            print(f"{votes=}")
            print(f"{nseats=}")
            print(f"{hondt=}")
            print(f"{hare=}")
            if found >= 5:
                return

def test_median(it=10):
    from statistics import median, median_low, median_high
    from collections import defaultdict
    from store.more_attribution_method import MedianScoreOld, MedianScore

    random = renpy.random.Random()
    solutions = 0
    for _k in range(it):
        nvotes = random.randrange(10, 1000)
        ngrades = random.randrange(2, 20)
        votes = {}
        for pk in range(random.randint(3, 26)):
            vot = [0]*ngrades
            for _v in range(nvotes):
                vot[random.randrange(ngrades)] += 1
            votes[alpha[pk]] = vot

        counts = defaultdict(list)
        for parti, tup in votes.items():
            for score, qty in enumerate(tup):
                counts[parti].extend([score]*qty)

        medians = {parti : median(liz) for parti, liz in counts.items()}
        medians_low = {parti : median_low(liz) for parti, liz in counts.items()}
        medians_high = {parti : median_high(liz) for parti, liz in counts.items()}

        results = {}
        for Attrib in (MedianScoreOld, MedianScore):
            results[Attrib] = dict(Attrib(1).attrib(votes))

        if results[MedianScoreOld] != results[MedianScore]:
            solutions += 1
            print("Found solution:")
            print(f"{votes=}")
            print(f"{nvotes=}, {ngrades=}")
            print(f"{results=}")
            print(f"{medians=}")
            print(f"{medians_low=}")
            print(f"{medians_high=}")
            # print(f"{counts=}")

        if solutions >= 5:
            break
    print(f"{solutions=}")
