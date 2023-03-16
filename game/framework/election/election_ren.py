"""renpy
init python in election_method:
"""
_constant = True

import abc
from collections import namedtuple

class ElectionMethod(namedtuple("ElectionMethod", ("voting_method", "attribution_method")), abc.ABC):
    __slots__ = ()

    def election(self, *args, **kwargs):
        return self.attribution_method.attrib(self.voting_method.vote(*args, **kwargs))

class Sortition(python_object):
    """
    Implements a selection by lottery, directly among the population.
    Poses problems that SingleVote+Randomize doesn't, as it does not return parties.
    That's not supported by the current House system.
    """
    __slots__ = ("nseats", "randomobj")

    def __init__(self, nseats, *, randomkey=None, randomobj=None):
        self.nseats = nseats
        if None not in (randomobj, randomkey):
            raise TypeError("Only one of randomobj and randomkey must be provided.")
        if randomobj is None:
            randomobj = renpy.random.Random(randomkey)
        self.randomobj = randomobj

    def election(self, pool):
        return [(c, 1) for c in self.randomobj.sample(pool, self.nseats)]

ElectionMethod.register(Sortition)
