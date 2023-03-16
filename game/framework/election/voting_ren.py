"""renpy
init python in voting_method:
"""
_constant = True

import abc
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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name is not None:
            voting_methods.append(cls)

    @abc.abstractmethod
    def vote(self, pool):
        """
        Returns an instance of the self.return_format class.
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
    """
    __slots__ = ("grades") # le nombre de notes différentes, >1
    return_format = results_format.SCORES
    name = _("Score Vote")

class ApprovalVote(CardinalVote):
    """
    Each voter approves, or not, each of the candidates.

    Technically a special case of grading vote where grades are 0 and 1,
    but it makes it open to additional attribution methods (proportional ones for instance).
    The format it returns data in, however, is (potentially) not the same as CardinalVote.
    """
    __slots__ = ()
    return_format = results_format.SIMPLE
    name = _("Approval Vote")

    def __init__(self, *args):
        self.grades = 2
