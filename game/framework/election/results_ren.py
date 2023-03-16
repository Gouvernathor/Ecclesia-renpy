"""renpy
init -1 python in results_format:
"""
_constant = True

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

class SIMPLE(_dict):
    __slots__ = ()
class ORDER(tuple):
    __slots__ = ()
class SCORES(_dict):
    __slots__ = ()

formats = (SIMPLE, ORDER, SCORES)
