import renpy
from store import _

"""renpy
init python in attribution_method:
"""
_constant = True

from collections import defaultdict
import abc
from statistics import fmean, median
from store import results_format

renpy.store.attribution_methods = attribution_methods = []

def listed_attrib(func):
    attribution_methods.append(func)
    return func

class Attribution(abc.ABC):
    """
    Determines how the votes determine the election.
    Non-instanciable base class.
    """
    __slots__ = ("nseats", "randomobj")
    contingency = None
    # getattr(attribution, "contingency", b) -> b if it can take one, None if not
    # hasattr(attribution, "contingency") -> if False, it needs to be given one
    # hasattr(attribution, "contingency") and attribution.contingency is not None -> it has one as it should
    # the contingency is given a default (or not) by classes using it in the constructor
    # or set afterward by setattr

    taken_format = None # class attribute, not instance attribute
    # `accepts` or `can_follow` staticmethod/classmethod, to say if it accepts a given voting method or not ?

    name = None # class attribute, not instance attribute
    # wrap in _() to make it translatable

    def __init__(self, nseats, *, randomkey=None, randomobj=None):
        if self.name is None:
            raise TypeError(f"{type(self)} is not instanciable. If it should be, it lacks a name.")
        self.nseats = nseats
        if randomobj is None:
            randomobj = renpy.random.Random(randomkey)
        elif randomkey is not None:
            raise TypeError("Only one of randomobj and randomkey must be provided.")
        self.randomobj = randomobj
        super().__init__()

    @abc.abstractmethod
    def attrib(self, results): pass

class Majority(Attribution):
    """
    Superset of SuperMajority and Plurality.
    """
    __slots__ = ()
    taken_format = results_format.SIMPLE

    def attrib(self, results):
        win = max(results, key=results.get)
        if (results[win] / sum(results.values())) > self.threshold:
            return {win : self.nseats}
        return self.contingency(results)

@listed_attrib
class Plurality(Majority):
    __slots__ = ()
    threshold = 0
    name = _("Plurality")

@listed_attrib
class SuperMajority(Majority):
    __slots__ = ("threshold", "contingency")
    name = _("(Super) Majority")

    def __init__(self, *args, threshold, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold

@listed_attrib
class InstantRunoff(Attribution):
    __slots__ = ()
    taken_format = results_format.ORDER
    name = _("Instant-Runoff Voting")

    def attrib(self, results):
        blacklisted = set()
        for _i in range(len(results[0])):
            first_places = defaultdict(int)
            for ballot in results:
                for parti in ballot:
                    if parti not in blacklisted:
                        first_places[parti] += 1
                        break

            total = sum(first_places.values())
            for parti, score in first_places.items():
                if score > total/2:
                    return {parti : self.nseats}
            blacklisted.add(min(first_places, key=first_places.get))
        raise Exception("We should never end up here")

@listed_attrib
class Borda(Attribution):
    __slots__ = ()
    taken_format = results_format.ORDER
    name = _("Borda Count")

    def attrib(self, results):
        scores = defaultdict(int)
        for ballot in results:
            for k, parti in enumerate(ballot):
                scores[parti] += k
        return {min(scores, key=scores.get) : self.nseats}

@listed_attrib
class Condorcet(Attribution):
    """
    This code doesn't support equally-ranked candidates (because the taken format doesn't allow it).
    It also doesn't support incomplete ballots, where not all candidates are ranked.
    """
    __slots__ = ("contingency")
    taken_format = results_format.ORDER
    name = _("Condorcet method")

    class Standoff(Exception): pass

    def __init__(self, *args, contingency=None, **kwargs):
        super().__init__(*args, **kwargs)
        if contingency is not None:
            self.contingency = contingency(*args, **kwargs)

    def attrib(self, results):
        count = defaultdict(int)
        for tup in results:
            for k, parti1 in enumerate(tup):
                for parti2 in tup[k+1:]:
                    count[parti1, parti2] += 1
                    count[parti2, parti1] -= 1
        win = {}
        for parti, autre in count:
            win[parti] = win.get(parti, True) and (count[parti, autre] > 0)
        for parti in win:
            if win[parti]:
                return {parti : self.nseats}
        if getattr(self, "contingency", None) is None:
            raise Condorcet.Standoff
        return self.contingency.attrib(results)

@listed_attrib
class AverageScore(Attribution):
    """
    From a score/rating vote, averages all the scores and elects the one with the best mean.
    """
    __slots__ = ()
    taken_format = results_format.SCORES
    name = _("Score method (average rating)")

    def attrib(self, results):
        # count = defaultdict(int)
        # for parti, tup in results.items():
        #     for score, qty in enumerate(tup):
        #         count[parti] += score * qty

        counts = defaultdict(list)
        for parti, tup in results.items():
            for score, qty in enumerate(tup):
                counts[parti].extend([score]*qty)

        count = {parti:fmean(liz) for parti, liz in counts.items()}

        return {max(count, key=count.get) : self.nseats}

@listed_attrib
class MedianScore(Attribution):
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

        medians = {parti : median(liz) for parti, liz in counts.items()}

        # ballots not voting for a candidate just do not count for that candidate
        winscore = max(medians.values())
        winners = [parti for parti, med in medians.items() if med == winscore]

        if len(winners) <= 1:
            return {winners[0] : self.nseats}
        # remove the non-winners
        trimmed_results = {parti:tup for parti, tup in results.items() if parti in winners}
        return self.contingency.attrib(trimmed_results)

class Proportional(Attribution):
    __slots__ = ()
    taken_format = results_format.SIMPLE

class HondtBase(Proportional):
    __slots__ = ("threshold")
    name = _("Proportional (highest averages)")

    def attrib(self, results):
        if self.threshold:
            results_ = results
            thresh = self.threshold * sum(results.values())
            results = {p:s for p, s in results.items() if s >= thresh}
            if not results:
                return self.contingency.attrib(results_)

        rv = defaultdict(int)
        for _k in range(self.nseats):
            # compute the ratio each party would get with one more seat
            # take the party with the best ratio
            win = max(results, key=(lambda p:results[p]/(rv[p]+1)))
            rv[win] += 1
        return rv

class HondtNoThreshold(HondtBase):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = 0

class HondtWithThreshold(HondtBase):
    __slots__ = ("contingency")

    def __init__(self, *args, threshold, contingency=HondtNoThreshold, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.contingency = contingency(*args, **kwargs)

@listed_attrib
class FakeHondt(HondtBase):
    def __new__(cls, *args, threshold=0, **kwargs):
        if threshold:
            return HondtWithThreshold(threshold=threshold, *args, **kwargs)
        return HondtNoThreshold(*args, **kwargs)

HighestAverages = FakeHondt

class HareBase(Proportional):
    __slots__ = ("threshold")
    name = _("Proportional (largest remainder)")

    def attrib(self, results):
        allvotes = sum(results.values())
        if self.threshold:
            results_ = results
            thresh = self.threshold * allvotes
            results = {p:s for p, s in results.items() if s >= thresh}
            if not results:
                return self.contingency.attrib(results_)

        rv = {parti : int(self.nseats*score/allvotes) for parti, score in results.items()}
        winners = sorted(results, key=(lambda p:self.nseats*results[p]/allvotes%1), reverse=True)
        for win in winners[:self.nseats-sum(rv.values())]:
            rv[win] += 1
        return rv

class HareNoThreshold(HareBase):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = 0

class HareWithThreshold(HareBase):
    __slots__ = ("contingency")

    def __init__(self, *args, threshold, contingency=HareNoThreshold, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = threshold
        self.contingency = contingency(*args, **kwargs)

@listed_attrib
class FakeHare(HareBase):
    def __new__(cls, *args, threshold=0, **kwargs):
        if threshold:
            return HareWithThreshold(threshold=threshold, *args, **kwargs)
        return HareNoThreshold(*args, **kwargs)

LargestRemainder = FakeHare

@listed_attrib
class Randomize(Attribution):
    """
    Everyone votes for their favorite candidate, then one ballot (per seat to fill) is selected at random.
    """
    __slots__ = ()
    taken_format = results_format.SIMPLE
    name = _("Random Allotment")

    def attrib(self, results):
        rd = defaultdict(int)
        for _s in range(self.nseats):
            rd[self.randomobj.choices(tuple(results), results.values())[0]] += 1
        return rd
