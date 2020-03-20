init python:
    # on va définir des fonctions qui vont donner les sièges à partir des résultats des élections
    # entrée A : liste de tuples
    # éléments de l'entrée A : nom de parti, nombre (ou pourcentage) de voix
    # les partis sont toujours classés de gauche à droite
    # entrée B : nombre de circonscriptions
    # entrée C : nombre d'élus par circonscription
    # sortie : liste de tuples
    # éléments de la sortie : nom de parti, nombre de sièges

    def election(population, partis, nb_circos, elus_par_circo, fonction):
        attrib_voix = [(p.name, 0) for p in partis]
        for circo in range(nb_circos):
            pass
        return

    # définir une fonction vote qui prend en entrée la répartition d'idées dans la population
    # et renvoie un score en pourcentage, ou en nombre de voix, par parti
    # ce score par parti est ensite donné à une fonction de répartition des votes
    # qui donne le nombre de sièges par parti par circonscription

    # types d'élection :
    # renvoie une liste d'éléments(parti, nombre de sièges)
    # renvoie la liste dans l'ordre où les partis ont été fournis
    # ne renvoie pas une liste complète
    # majoritaire uninominale 1 tour
    # majoritaire uninominale 2 tours # suspendue ?
    # proportionnelle à plus forte moyenne (Hondt/Jefferson), avec seuil potentiellement nul
    # proportionnelle à plus fort reste (Hare), avec seuil potentiellement nul

    def majoritaire(the_list, nseats=1, **kwargs):
        '''
        Renvoie le seul parti ayant le plus de voix
        A utiliser dans les élections uninominales à un tour avec une seule circonscription
        '''
        win, maj = the_list[0]
        for tup in the_list:
            if tup[1]>maj:
                win, maj = tup
        return [(win, nseats)]

    def majoritaire_random(the_list, nseats=1, randomobj=renpy.random, **kwargs):
        '''
        Renvoie une valeur aéatoire pondérée
        A utiliser dans les élections uninominales à un tour avec plusieurs circonscriptions
        '''
        sum = 0
        for tup in the_list:
            sum += tup[1]
        ran = randomobj.random()*sum
        sum = 0
        for tup in the_list:
            sum += tup[1]
            if ran<sum:
                return [(tup[0], nseats)]
        # on est censé ne jamais arriver ici

    def proportionnelle_Hondt(the_list, nseats, thresh=False, **kwargs):
        '''
        Implémente la proportionnelle d'Hondt, à plus forte moyenne, avec seuil possible
        Attention : si aucun parti ne dépasse le seuil, renvoie None
        '''
        if thresh:
            sum = 0
            for tup in the_list:
                sum += tup[1]
            for tup in the_list:
                if float(tup[1])/sum < thresh:
                    the_list.remove(tup)
        if the_list == []:
            return None
        the_list = [list(tup)+[0] for tup in the_list]
        attrib = 0
        for k in range(nseats):
            maj = 0
            for tup in the_list:
                moy = float(tup[1])/(tup[2]+1)
                if moy>maj:
                    maj = moy
                    win = tup[0]
            for tup in the_list:
                if tup[0]==win:
                    tup[2]+=1
                    attrib += 1
                    break
        if attrib != nseats:
            raise ValueError("Le nombre de sièges alloués ne correspond pas au nombre total")
        return [(tup[0], tup[2]) for tup in the_list]

    def proportionnelle_Hare(the_list, nseats, thresh=False, **kwargs):
        '''
        Implémente la proportionnelle de Hare, à plus fort reste, avec seuil possible
        Attention : si aucun parti ne dépasse le seuil, renvoie None
        '''
        sum = 0
        for tup in the_list:
            sum += tup[1]
        if thresh:
            for tup in the_list:
                if float(tup[1])/sum < thresh:
                    the_list.remove(tup)
        if the_list == []:
            return None
        the_list = [list(tup)+[0] for tup in the_list]
        att = []
        attrib = 0
        for tup in the_list:
            sea = float(tup[1])/sum *nseats
            attrib += int(sea)
            tup[2] = int(sea)
            # att.append((tup[0], int(sea)))
            # tup[1] = sea-int(sea)
            att.append((tup[0], sea-int(sea)))
        att.sort(key=lambda x: x[1], reverse=True)
        # print(the_list)
        for k in range(nseats-attrib):
            # the_list[k][2] += 1
            for tup in the_list:
                if tup[0] == att[k][0]: # nom du gagnant
                    tup[2] += 1
        return [(tup[0], tup[2]) for tup in the_list]
