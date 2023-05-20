python_dict = dict

"""renpy
init -1 python in results_format:
"""
_constant = True

from collections import Counter as __Counter

# SIMPLE : Counter(parti : nombre de voix)
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
#       si l'électeur doit noter tous les candidats, (sum(tup) for tup in result.values()) est constant et égal au nombre d'électeurs

class SIMPLE(__Counter):
    __slots__ = ()

    @classmethod
    def fromkeys(cls, keys, value=None):
        return cls(python_dict.fromkeys(keys, value))

class ORDER(tuple):
    __slots__ = ()

class SCORES(python_dict):
    __slots__ = ()

formats = frozenset((SIMPLE, ORDER, SCORES))
