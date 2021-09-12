init python:
    from collections import OrderedDict

    class Function_Wrapper:
        def __init__(self, name=None, ttip=None):
            if name is not None:
                self.name = name
            if ttip is not None:
                self.ttip = ttip

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def __eq__(self, other):
            if type(self) == type(other):
                if self.__call__ == other.__call__:
                    if self.name == other.name:
                        return True
            return False

    class VotingMethod(Function_Wrapper): pass

    # Fournit pour une circo donnée en argument
    # le nombre de voix reçue par chaque parti/candidat/liste
    class Vote_Simple(VotingMethod):
        def __call__(self, (nseats, funk, citizens)):
            '''
            Chaque électeur vote uniquement pour son parti préféré
            Renvoie un dictionnaire reliant chaque parti à son nombre de voix
            '''
            scores = {parti:0 for parti in partis}
            for citizen in citizens:
                opns = dict() # son désaccord à propos de chaque parti
                partees = partis[:] # on copie la liste pour la mélanger
                electrobj.shuffle(partees)
                for parti in partees:
                    # on fait la moyenne des différences d'opinion
                    opns[parti] = disagree(citizen, parti)
                    # change the way the opinions are compared between a citizen and a party
                    # consider the value for each subject as how much the citizen's opinion is fervent on the subject
                    # so if the citizen doesn't care and the party cares very much,
                    # it's less of a disagreement than if the citizen cares very much and the party doesn't !
                    # maybe multiply the difference between the two by the absolute magnitude of the opinion ?
                    # *abs(citizen.opinion[k]-.5*opinrange)
                # sélectionner le parti avec lequel le désaccord est le plus petit
                # lui ajouter une voix
                scores[min(opns, key=opns.get)] += 1
            return scores

    class Vote_Unique(Vote_Simple):
        name = "Vote unique pour le candidat préféré"

    class No_Vote(Vote_Simple):
        name = "Aucun vote"

    class Classement(VotingMethod):
        name = "Classement des candidats par ordre de préférence"
        def __call__(self, (nseats, funk, citizens)):
            '''
            Les électeurs classent tous les candidats par ordre de préférence
            Renvoie une liste de tuples ordonnés de partis, les mieux en premier
            Tous les partis ne sont pas obligés d'être dans chacun des tuples
            '''
            bigliz = []
            for citizen in citizens:
                opns = {}
                partees = partis[:]
                electrobj.shuffle(partees)
                for parti in partees:
                    opns[parti] = disagree(citizen, parti)
                partees.sort(key=opns.get)
                bigliz.append(tuple(partees))
            return bigliz

    class Validation(VotingMethod):
        name = "Validation ou non de chaque candidat"
        def __call__(self, (nseats, funk, citizens)):
            '''
            Les électeurs valident entre 1 et n-1 candidats
            '''
            raise NotImplementedError

    class Scoring(VotingMethod):
        name = "Notation de chaque candidat sur une échelle fixe"
        def __call__(self, (nseats, funk, citizens)):
            raise NotImplementedError

    def disagree(cita, citb):
        '''
        Compares the opinions between two citizens,
        or between a citizen and a parti,
        or between two partis
        The score is strictly positive, the higher the stronger the disagreement
        '''
        return sum([abs(cita.opinions[k]-citb.opinions[k]) for k in range(nopinions)])

    def election(house):
        '''
        Renouvelle intégralement la chambre parlementaire fournie
        '''
        scoress = []
        for circo in house.circos:
            attribkind = circo[1]
            try:
                votingkind, attribkind = attribkind
            except TypeError:
                print("TypeError")
                votingkind = Vote()
            scoress.append(attribkind(votingkind(circo), nseats=circo[0], randomobj=electrobj))
        joinedlist = join_results(scoress).items()
        joinedlist.sort(key=lambda p:p[0].alignment)
        joinn = OrderedDict(joinedlist)
        house.members = joinn
        return joinn

    # obtenir un score en pourcentage, ou en nombre de voix, par parti
    # ce score par parti est ensuite donné à une fonction de répartition des votes
    # qui donne le nombre de sièges par parti par circonscription

    # types d'attributions :
    # renvoie une liste d'éléments (parti, nombre de sièges)
    # renvoie la liste dans l'ordre où les partis ont été fournis
    # ne renvoie pas une liste complète
    # ne simule que les élections où chaque citoyen vote pour un parti
        # pas celles où il faut constituer ou modifier une liste soi-même
        # ou où il faut faire un classement des options disponibles #condorcet
    # majoritaire uninominale 1 tour
    # majoritaire uninominale 2 tours #TODO
    # proportionnelle à plus forte moyenne (Hondt/Jefferson), avec seuil potentiellement nul
    # proportionnelle à plus fort reste (Hare), avec seuil potentiellement nul

    # ces fonctions prennent en argument :
    # scores, une liste de (parti, part), pour vote unique et validation
        # avec part étant un nombre (int ou float) proportionnel au nombre de voix
    # scores, une liste de tuples de partis, pour classement
    # nseats (optionnel), indiquant le nombre de sièges à remplir
    # randomobj (optionnel), utilisé quand on besoin de random
    # thresh (optionnel), utilisé pour les proportionnelles
        # mais doit être curryifié pour être utilisable dans la suite de la simulation

    class AttribMethod(Function_Wrapper): pass
    class Proportional: pass

    class Majoritaire(AttribMethod):
        name = "Majoritaire"
        valid = (Vote_Unique, Validation, Scoring)
        def __call__(self, scores, nseats=1, **kwargs):
            '''
            Renvoie le seul parti ayant le plus de voix
            A utiliser dans les élections uninominales à un tour avec une seule circonscription
            '''
            scores = scores.items()
            win, maj = scores[0]
            for tup in scores:
                if tup[1]>maj:
                    win, maj = tup
            return [(win, nseats)]

    def majoritaire_random(scores, nseats=1, randomobj=renpy.random, **kwargs):
        '''
        Renvoie une valeur aéatoire pondérée
        A utiliser dans les élections uninominales à un tour avec plusieurs circonscriptions
        '''
        sum = 0
        for tup in scores:
            sum += tup[1]
        ran = randomobj.random()*sum
        sum = 0
        for tup in scores:
            sum += tup[1]
            if ran<sum:
                return [(tup[0], nseats)]
        # on est censé ne jamais arriver ici

    class InstantRunoff(AttribMethod):
        name = "Vote Alternatif"
        valid = (Classement,)
        def __call__(self, scores, nseats, blacklisted=(), **kwargs):
            '''
            Implémente l'Instant Runoff Voting, où on vire le moins bien classé en moyenne
            jusqu'à arriver à une majorité absolue pour un des candidats restants.
            '''
            # déterminer le nombre de premières places pour chaque parti non-blacklisté
            first_places = {}
            for tup in scores:
                for parti in tup:
                    if parti not in blacklisted:
                        break
                else:
                    continue
                first_places[parti] = first_places.get(parti, 0)+1
                # si il y a une majorité absolue dans les premiers choix, il est choisi
                if first_places[parti] > len(scores)/2:
                    return [(parti, nseats)]
            # blacklister le dernier
            blacklisted += (min(first_places, key=first_places.get),)
            return self(scores, nseats, blacklisted=blacklisted)

    class ProportionnelleHondt(AttribMethod, Proportional):
        name = "Proportionnelle d'Hondt"
        valid = (Vote_Unique, Validation)
        def __call__(self, scores, nseats, thresh=False, contingent=None, **kwargs):
            '''
            Implémente la proportionnelle d'Hondt, à plus forte moyenne, avec seuil possible
            Si aucun parti ne dépasse le seuil, relance l'attribution des votes sans seuil
            ou via la méthode fournie par `contingent`.
            '''
            scores = scores.items()
            oldscores = scores[:]
            # if there's a threshold, each score below it is thrown out
            if thresh:
                sum = 0
                for tup in scores:
                    sum += tup[1]
                for tup in scores:
                    if float(tup[1])/sum < thresh:
                        scores.remove(tup)
            # if no party exceeded the threshold, a contingent election is triggered
            if scores == []:
                # the default contingent behavior is to remove the threshold and start again
                return (contingent or proportionnelle_Hondt)(oldscores, nseats, **kwargs)
            # creating a [party, qvotes, nseats] list
            scores = [list(tup)+[0] for tup in scores]
            attrib = 0 # seats already alotted
            for k in range(nseats):
                maj = 0 # greatest mean (qvotes/(nseats+1)) value among the partis
                for tup in scores:
                    moy = float(tup[1])/(tup[2]+1)
                    if moy>maj:
                        maj = moy
                        win = tup[0]
                # for each party, the one with the greatest mean value earns a seat
                for tup in scores:
                    if tup[0] == win:
                        tup[2] += 1
                        attrib += 1
                        break
            if attrib != nseats:
                raise ValueError("Le nombre de sièges alloués ne correspond pas au nombre total")
            return [(tup[0], tup[2]) for tup in scores]

    class ProportionnelleHare(AttribMethod, Proportional):
        name = "Proportionnelle de Hare"
        valid = (Vote_Unique, Validation)
        def __call__(self, scores, nseats, thresh=False, contingent=None, **kwargs):
            '''
            Implémente la proportionnelle de Hare, à plus fort reste, avec seuil possible
            Si aucun parti ne dépasse le seuil, relance l'attribution des votes sans seuil
            ou via la méthode fournie par `contingent`.
            '''
            scores = scores.items()
            oldscores = scores[:]
            # computing the sum of all vote quantities
            sum = 0
            for tup in scores:
                sum += tup[1]
            # if there is a threshold, each score below it is thrown out
            if thresh:
                for tup in scores:
                    if float(tup[1])/sum < thresh:
                        scores.remove(tup)
            # if no party exceeded the threshold, a contingent election is triggered
            if scores == []:
                # the default contingent behavior is to remove the threshold and start again
                return (contingent or proportionnelle_Hare)(oldscores, nseats, **kwargs)
            # creating a [party, qvotes, nseats] list
            scores = [list(tup)+[0] for tup in scores]
            attrib = 0 # seats already alotted
            # list of decimal parts of remainders of (qvotes/totalqvotes)*nseats
            att = []
            for tup in scores:
                sea = float(tup[1])/sum *nseats
                # give the whole number of seats to the party
                attrib += int(sea)
                tup[2] = int(sea)
                # store the decimal part in its list
                att.append((tup[0], sea-int(sea)))
            # sort parties by decreasig order of remainders
            att.sort(key=lambda x: x[1], reverse=True)
            # give one more seat to the greatest parties until all seats are filled
            for k in range(nseats-attrib):
                for tup in scores:
                    if tup[0] == att[k][0]: # nom du gagnant
                        tup[2] += 1
                        break
            return [(tup[0], tup[2]) for tup in scores]

    class TirageAuSort(AttribMethod):
        name = "Tirage au sort"
        valid = (No_Vote,)
        def __call__(self, scores, nseats, randomobj=renpy.random, **kwargs):
            '''
            Tire au sort parmi une population,
            où chaque personne tirée au sort représente son parti préféré
            '''
            scores = scores.items()
            retlist = [[tup[0], 0] for tup in scores]
            for seat in range(nseats):
                sum = 0
                ran = randomobj.random()*sum
                for k in range(len(scores)):
                    sum += scores[k][1]
                    if ran<sum:
                        retlist[k][1] += 1
                        break
            return retlist

    def tirage_au_sort_partis(scores, nseats, randomobj=renpy.random, **kwargs):
        '''
        Tire au sort parmi les candidats, en donnant un poids égal à tous les partis
        indépendemment de la popularité de chacun
        Tellement facile de spammer les candidatures et de multiplier sa probabilité de victoire qu'un peu vide de sens
        '''
        npartis = len(scores)
        scores = [list(tup)+[0] for tup in scores]
        for k in range(nseats):
            scores[randomobj.randint(0, npartis-1)][2] += 1
        return [(tup[0], tup[2]) for tup in scores]

    def join_results(scoress):
        '''
        Assemble les attributions de sièges par circo
        pour donner le score de chaque parti à l'échelle de la Chambre
        Prend en entrée une liste de listes scores
        renvoie un dict {parti:nsièges}
        prêt à être rangé dans house.members
        '''
        members = {parti:0 for parti in partis}
        for scores in scoress:
            for parti, nseats in scores:
                members[parti] += nseats
        # si on veut retirer les partis sans sièges :
        members = {parti: sieges for parti, sieges in members.items() if sieges}
        return members

define votingkinds = (Vote_Unique(), Classement(), Validation(), No_Vote())
define attribkinds = (Majoritaire(), InstantRunoff(), TirageAuSort(), ProportionnelleHondt(), ProportionnelleHare())
