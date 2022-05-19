init python in results_format:
    # SIMPLE : dict(parti : nombre de voix)
    #       {PS : 5, LR : 7} -> 5 voix pour le PS, 7 pour LR
    # ORDER : iterable(iterable(partis ordonnés par préférence décroissante))
    #       [(LR, PS, LFI), (LFI, PS,), ] -> un électeur préfère LR puis PS puis LFI,
    #                                        un autre préfère LFI puis le PS et n'a pas classé LR
    #       max(len(tup) for tup in result) <= (nombre de candidats) - 1
    #                                       == si votingmethod.order_all
    #       Ne pas classer tous les candidats est permis, mais pas d'ex-aequo
    # SCORES : dict(parti : iterable(nombre de voix pour chaque note))
    #       {PS : (0, 2, 5, 9, 1)} -> le PS a reçu 0 fois la pire note, 1 fois la meilleure et t'as compris
    #       (len(tup) for tup in result.values()) est constant, égal à votingmethod.grades

    class SIMPLE(dict):
        __slots__ = ()
    class ORDER(tuple):
        __slots__ = ()
    class SCORES(dict):
        __slots__ = ()

    formats = (SIMPLE, ORDER, SCORES)

init python:
    import abc, inspect

    voting_methods = []

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
            if self.name is None:
                raise TypeError(f"Class {type(self)} is not instantiable.")

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.name is not None:
                voting_methods.append(cls)

        @abc.abstractmethod
        def vote(self, pool): pass

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
            scores = {parti:0 for parti in partis}
            partees = list(partis)
            electrobj.shuffle(partees)
            for citizen in pool:
                # sélectionner le parti avec lequel le désaccord est le plus petit
                # lui ajouter une voix
                scores[min(partees, key=(lambda p:p.disagree(citizen)))] += 1
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
            partees = list(partis)
            electrobj.shuffle(partees)
            for citizen in pool:
                ordered = sorted(partees, key=(lambda p:p.disagree(citizen)))
                bigliz.append(tuple(ordered))
            return bigliz

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

init python:
    from collections import defaultdict

    attribution_methods = []

    class Attribution(abc.ABC):
        """
        Determines how the votes determine the election.
        Non-instanciable class.
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

        def __init__(self, nseats, randomobj=None, randomkey=None):
            if self.name is None:
                raise TypeError(f"{type(self)} is not instanciable. If it should be, it lacks a name.")
            self.nseats = nseats
            if None not in (randomobj, randomkey):
                raise TypeError("Only one of randomobj and randomkey must be provided.")
            if randomobj is None:
                randomobj = renpy.random.Random(randomkey)
            self.randomobj = randomobj
            super().__init__()

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.name is not None:
                attribution_methods.append(cls)

        @abc.abstractmethod
        def attrib(self, results): pass

    class Majority(Attribution):
        """
        Superset of SuperMajority and Plurality.
        """
        __slots__ = ("threshold")
        taken_format = results_format.SIMPLE

        def attrib(self, results):
            win = max(results, key=results.get)
            if (results[win] / sum(results.values())) > self.threshold:
                return [(win, self.nseats)]
            return self.contingency(results)

    class Plurality(Majority):
        __slots__ = ()
        name = _("Plurality")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threshold = 0

    class SuperMajority(Majority):
        __slots__ = ("contingency")
        name = _("(Super) Majority")

        def __init__(self, *args, threshold, **kwargs):
            self.threshold = threshold

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
                        return [(parti, self.nseats)]
                blacklisted.add(min(first_places, key=first_places.get))
            raise Exception("We should never end up here")

    class Borda(Attribution):
        __slots__ = ()
        taken_format = results_format.ORDER
        name = _("Borda Count")

        def attrib(self, results):
            scores = defaultdict(int)
            for ballot in results:
                for k, parti in enumerate(ballot):
                    scores[parti] += k
            return [(min(scores, key=scores.get), self.nseats)]

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
                    return [(parti, self.nseats)]
            if getattr(self, "contingency", None) is None:
                raise Condorcet.Standoff
            return self.contingency.attrib(results)

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

            count = {parti:sum(liz)/len(liz) for parti, liz in counts.items()}

            return [(max(count, key=count.get), self.nseats)]

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

            counts = {parti : sorted(liz) for parti, liz in counts.items()}

            if False:
                # filling the blanks - a parti not listed is given a 0 score
                nvotes = max(len(liz) for liz in counts.values())
                for parti, liz in counts.items():
                    counts[parti] = [0]*(nvotes-len(counts[parti])) + counts[parti]

                winscore = max(liz[nvotes//2] for liz in counts.values())
                winners = [parti for parti in counts if counts[parti][nvotes//2] == winscore]
            else:
                # ballots not voting for a candidate just do not count for that candidate
                winscore = max(liz[len(liz)//2] for liz in counts.values())
                winners = [parti for parti, liz in counts.items() if liz[len(liz)//2] == winscore]

            if len(winners) <= 1:
                return [(winners[0], self.nseats)]
            # remove the non-winners
            trimmed_results = {parti:tup for parti, tup in results.items() if parti in winners}
            return self.contingency.attrib(trimmed_results)

    class Proportional(Attribution):
        __slots__ = ()
        taken_format = results_format.SIMPLE

    class HondtProportional(Proportional):
        __slots__ = ("threshold")
        name = _("Proportional (largest averages)")

        def __new__(cls, threshold=0, *args, **kwargs):
            if threshold:
                return HondtWithThreshold.__new__(HondtWithThreshold, threshold=threshold, *args, **kwargs)
            return HondtNoThreshold.__new__(HondtNoThreshold, *args, **kwargs)

        def __init_subclass__(cls, **kwargs):
            return

        # the attribution method is coded here

    class HondtNoThreshold(HondtProportional):
        __slots__ = ()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threshold = 0

    class HondtWithThreshold(HondtProportional):
        __slots__ = ("contingency")

        def __init__(self, *args, contingency=HondtNoThreshold, **kwargs):
            super().__init__(*args, **kwargs)
            self.contingency = contingency(*args, **kwargs)

    class HareProportional(Proportional):
        __slots__ = ("threshold")
        name = _("Proportional (largest remainder)")

        def __new__(cls, threshold=0, *args, **kwargs):
            if threshold:
                return HareWithThreshold.__new__(HareWithThreshold, threshold=threshold, *args, **kwargs)
            return HareNoThreshold.__new__(HareNoThreshold, *args, **kwargs)

        def __init_subclass__(cls, **kwargs):
            return

        # the attribution method is coded here

    class HareNoThreshold(HareProportional):
        __slots__ = ()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.threshold = 0

    class HareWithThreshold(HareProportional):
        __slots__ = ("contingency")

        def __init__(self, *args, contingency=HareNoThreshold, **kwargs):
            super().__init__(*args, **kwargs)
            self.contingency = contingency(*args, **kwargs)

    class Randomize(Attribution):
        """
        Everyone votes for their favorite candidate, then one ballot (per seat to fill) is selected at random.
        """
        __slots__ = ()
        taken_format = results_format.SIMPLE
        name = _("Random Allotment")

        def attrib(self, results):
            rd = defaultdict(int)
            for seat in range(self.nseats):
                rd[self.randomobj.choices(tuple(results), results.values())[0]] += 1
            return list(rd.items())

    # faire un vrai tirage au sort parmi la population

init python:
    from collections import namedtuple

    class ElectionMethod(namedtuple("ElectionMethod", ("voting_method", "attribution_method"))):
        def election(self, *args, **kwargs):
            return self.attribution_method.attrib(self.voting_method.vote(*args, **kwargs))

init python:
    def is_subclass(a, b, /):
        return isinstance(a, type) and issubclass(a, b)
