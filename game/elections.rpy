init python:
    def vote((nseats, funk, citizens)):
        '''
        Fournit pour une circo donnée en argument
        le nombre de voix reçue par chaque parti/candidat/liste
        '''
        scores = {parti:0 for parti in partis}
        for citizen in citizens:
            opns = dict() # la liste de son désaccord à propos de chaque parti
            partees = partis[:] # on copie la liste pour la mélanger
            renpy.random.Random(electkey).shuffle(partees)
            for parti in partees:
                # on fait la moyenne des différences d'opinion
                opns[parti] = disagree(citizen, parti)
            # sélectionner le parti avec lequel le désaccord est le plus petit
            # lui ajouter une voix
            scores[min(opns, key=opns.get)] += 1
        return scores

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
        randomobj = renpy.random.Random(electkey)
        scoress = []
        for circo in house.circos:
            scoress.append(circo[1](vote(circo), nseats=circo[0]))
        joinn = join_results(scoress)
        house.members = joinn
        return joinn

    # obtenir un score en pourcentage, ou en nombre de voix, par parti
    # ce score par parti est ensuite donné à une fonction de répartition des votes
    # qui donne le nombre de sièges par parti par circonscription

    # types d'élection :
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
    # scores, une liste de (parti, part)
        # avec part étant un nombre (int ou float) proportionnel au nombre de voix
    # nseats (optionnel), indiquant le nombre de sièges à remplir
    # randomobj (optionnel), utilisé quand on besoin de random
    # thresh (optionnel), utilisé pour les proportionnelles
        # mais doit être curryifié pour être utilisable dans la suite de la simulation

    def majoritaire(scores, nseats=1, **kwargs):
        '''
        Renvoie le seul parti ayant le plus de voix
        A utiliser dans les élections uninominales à un tour avec une seule circonscription
        '''
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

    def tirage_au_sort_population(scores, nseats, randomobj=renpy.random, **kwargs):
        '''
        Tire au sort parmi une population,
        où chaque personne tirée au sort représente son parti préféré
        '''
        retlist = [(tup[0], 0) for tup in scores]
        for seat in range(nseats):
            sum = 0
            ran = randomobj.random()*sub
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

    def proportionnelle_Hondt(scores, nseats, thresh=False, contingent=None, **kwargs):
        '''
        Implémente la proportionnelle d'Hondt, à plus forte moyenne, avec seuil possible
        Si aucun parti ne dépasse le seuil, relance l'attribution des votes sans seuil
        ou via la méthode fournie par `contingent`.
        '''
        scores = list(scores)
        if thresh:
            sum = 0
            for tup in scores:
                sum += tup[1]
            for tup in scores:
                if float(tup[1])/sum < thresh:
                    scores.remove(tup)
        if scores == []:
            return (contingent or proportionnelle_Hondt)(scores, nseats, **kwargs)
        scores = [list(tup)+[0] for tup in scores]
        attrib = 0
        for k in range(nseats):
            maj = 0
            for tup in scores:
                moy = float(tup[1])/(tup[2]+1)
                if moy>maj:
                    maj = moy
                    win = tup[0]
            for tup in scores:
                if tup[0]==win:
                    tup[2]+=1
                    attrib += 1
                    break
        if attrib != nseats:
            raise ValueError("Le nombre de sièges alloués ne correspond pas au nombre total")
        return [(tup[0], tup[2]) for tup in scores]

    def proportionnelle_Hare(scores, nseats, thresh=False, **kwargs):
        '''
        Implémente la proportionnelle de Hare, à plus fort reste, avec seuil possible
        Attention : si aucun parti ne dépasse le seuil, renvoie None
        Unstable, needs testings and fixings #TODO
        '''
        sum = 0
        for tup in scores:
            sum += tup[1]
        if thresh:
            for tup in scores:
                if float(tup[1])/sum < thresh:
                    scores.remove(tup)
        if scores == []:
            return None
        scores = [list(tup)+[0] for tup in scores]
        att = []
        attrib = 0
        for tup in scores:
            sea = float(tup[1])/sum *nseats
            attrib += int(sea)
            tup[2] = int(sea)
            # att.append((tup[0], int(sea)))
            # tup[1] = sea-int(sea)
            att.append((tup[0], sea-int(sea)))
        att.sort(key=lambda x: x[1], reverse=True)
        # print(scores)
        for k in range(nseats-attrib):
            # scores[k][2] += 1
            for tup in scores:
                if tup[0] == att[k][0]: # nom du gagnant
                    tup[2] += 1
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
        for parti in members:
            if not members[parti]:
                members.remoe(parti)
        return members

define proportionals = [# proportionnelle_Hare,
                        proportionnelle_Hondt]

define electypes = [majoritaire,
                    # majoritaire_random,
                    tirage_au_sort_population,
                    # tirage_au_sort_partis
                    ]+proportionals
