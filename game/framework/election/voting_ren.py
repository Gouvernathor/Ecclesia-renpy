import renpy
from store import _

"""renpy
init python in voting_method:
"""
_constant = True

import abc
from math import nextafter, floor
import store
from store import results_format

renpy.store.voting_methods = voting_methods = []

class VotingMethod(abc.ABC):
    """
    Determines the process through which the voters cast their votes.
    Non-instanciable class.
    """
    __slots__ = ()
    return_format = None # class attribute, not instance attribute

    name = None # class attribute, not instance attribute
    # wrap in _() to make it translatable

    def __init__(self):
        if None in (self.name, self.return_format):
            raise TypeError(f"Class {type(self)} is not instantiable.")

    def __init_subclass__(cls, final=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if (final is None) and (cls.name is not None) or final:
            voting_methods.append(cls)

    @abc.abstractmethod
    def vote(self, pool:Collection, /):
        """
        Override in subclasses.

        `pool` contains the opinionated voters. Generally, though not necessarily,
        Citizens (it can also be Parties). Their disagreement with the parties are
        quantified by the `^` operator, returning values in the 0-1 range, the
        higher the stronger disagreement.

        Must return an instance of self.return_format.
        """

class SingleVote(VotingMethod):
    """
    Each voter casts one vote for one of the available candidates, or for none of them.
    """
    __slots__ = ()
    return_format = results_format.SIMPLE
    name = _("Single Vote")

    def vote(self, pool):
        """
        Tactical voting isn't simulated. Everyone votes for their favorite party.
        """
        partees = list(store.partis)
        scores = self.return_format.fromkeys(partees, 0)
        store.electrobj.shuffle(partees)
        for citizen in pool:
            # sélectionner le parti avec lequel le désaccord est le plus petit
            # lui ajouter une voix
            scores[min(partees, key=(lambda p:p^citizen))] += 1
        return scores

class OrderingVote(VotingMethod):
    """
    Each voter orders all (or a subset) of the available candidates.
    """
    __slots__ = ("order_all")
    return_format = results_format.ORDER
    name = _("Positional/Rank Vote")

    def vote(self, pool):
        bigliz = []
        partees = list(store.partis)
        store.electrobj.shuffle(partees)
        for citizen in pool:
            ordered = sorted(partees, key=(lambda p:p^citizen))
            bigliz.append(tuple(ordered))
        return self.return_format(bigliz)

class CardinalVote(VotingMethod):
    """
    Each voter gives a note (or grade) for each of the candidates.

    This one is not as straightforward as the two preceding ones, even setting aside strategic voting.
    What do you consider the range of grades to cover ? From nazis to angels, or from the worst present candidate to the best ?
    The answer lies only in the minds of the voters.
    The latter is more akin to OrderingVote, so I made the former the default,
    but it causes issues for lower grades so ApprovalVote uses the latter.
    """
    __slots__ = ("grades") # the number of different grades, >1
    return_format = results_format.SCORES
    name = _("Score Vote")

    def __init__(self, grades):
        super().__init__()
        self.grades = grades

    def vote(self, pool):
        """
        Each voter gives a grade to each party proportional to the raw disagreement.
        This may yield situations where every party is graded 0, especially with lower numbers of grades.
        """
        grades = self.grades
        rv = results_format.SCORES.fromgrades(grades)
        partees = list(store.partis)
        store.electrobj.shuffle(partees)

        # uncorrected version, may return cases where every party is graded 0
        grades = nextafter(grades, .0) # if the disagreement is .0, the grade will be grades-1 and not grades
        for voter in pool:
            for parti in partees:
                grad = floor((1-(voter^parti)) * grades)
                rv[parti][grad] += 1

        return rv

class BalancedCardinalVote(CardinalVote, final=False):
    def vote(self, pool):
        """
        Each voter gives a grade to each party, affine wrt its minimum and
        maximum disagreement with the candidate parties only.
        Each voter will give the best grade at least once, and
        either grade all parties equally or give the worst grade at least once.
        """
        grades = self.grades
        rv = results_format.SCORES.fromgrades(grades)
        partees = list(store.partis)
        store.electrobj.shuffle(partees)

        # balanced version
        grades = nextafter(grades, .0) # if the disagreement is .0, the grade will be grades-1 and not grades
        for voter in pool:
            prefs = {parti:1-(voter^parti) for parti in partees}
            minpref = min(prefs.values())
            maxpref = max(prefs.values())

            if minpref != maxpref: # avoid division by zero
                maxpref -= minpref

            for parti in partees:
                grad = floor(grades * (prefs[parti] - minpref) / maxpref)
                rv[parti][grad] += 1

        return rv

class ApprovalVote(BalancedCardinalVote):
    """
    Each voter approves, or not, each of the candidates.

    Technically a special case of grading vote where grades are 0 and 1,
    but it makes it open to additional attribution methods (proportional ones for instance).
    The format it returns, however, is not the same as CardinalVote.
    """
    __slots__ = ()
    return_format = results_format.SIMPLE
    name = _("Approval Vote")

    def __init__(self):
        super().__init__(grades=2)

    def vote(self, pool):
        scores = super().vote(pool)
        rv = self.return_format()
        for parti, (_nos, yeas) in scores.items():
            rv[parti] += yeas
        return rv
