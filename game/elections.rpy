init python:
    # on va définir des fonctions qui vont donner les sièges à partir des résultats des élections
    # entrée A : liste de tuples
    # éléments de l'entrée A : nom de parti, nombre (ou pourcentage) de voix
    # les partis sont toujours classés de gauche à droite
    # entrée B : nombre de circonscriptions
    # entrée C : nombre d'élus par circonscription
    # sortie : liste de tuples
    # éléments de la sortie : nom de parti, nombre de sièges

    def election(population, partis, (total_seats, fonction, elus_par_circo)):
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

    def tirage_au_sort_population(the_list, nseats, randomobj=renpy.random, **kwargs):
        '''
        Tire au sort parmi une population,
        où chaque personne tirée au sort représente son parti préféré
        Avec un seul siège, équivalente à une majoritaire random
        '''
        retlist = [(tup[0], 0) for tup in the_list]
        for seat in range(nseats):
            sum = 0
            ran = randomobj.random()*sub
            for k in range(len(the_list)):
                sum += the_list[k][1]
                if ran<sum:
                    retlist[k][1] += 1
                    break
        return retlist

    def tirage_au_sort_partis(the_list, nseats, randomobj=renpy.random, **kwargs):
        '''
        Tire au sort parmi les candidats, en donnant un poids égal à tous les partis
        indépendemment de la popularité de chacun
        '''
        npartis = len(the_list)
        the_list = [list(tup)+[0] for tup in the_list]
        for k in range(nseats):
            the_list[randomobj.randint(0, npartis-1)][2] += 1
        return [(tup[0], tup[2]) for tup in the_list]

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

    def sum_results(lolor):
        '''
        Assemble les attributions par circo pour donner la répartition globale
        Peut aussi servir à faire une union de deux chambres
        Prend en entrée une liste de the_list
        donc une liste de listes de tuples (parti, sièges)
        Fournit une the_list avec pour chaque parti, son nombre total de sièges
        '''
        the_dict=[]
        listovp = []
        for the_list in lolor:
            for tup in the_list:
                if tup[0] not in the_dict:
                    the_dict[tup[0]] = 0
                    listovp.append(tup[0])
                the_dict[tup[0]]+=tup[1]
        the_list = []
        for p in listovp:
            the_list.append((p, the_dict[p]))
        # return [(p, s) for p, s in the_dict]
        return the_list

        # partis : couleur TSV/HSV saturée
        # teinte (premier composant) pris entre .0 (rouge) et .66 (bleu) ou .75 (bleu-violet)
        # Color(hsv=(renpy.random.random()*.75, 1.0, 1.0))
        # à classer par teinte
        # col.hsv[0]

# define electypes = {majoritaire : _(""),
#                     majoritaire_random : _(""),
#                     tirage_au_sort_population : _(""),
#                     tirage_au_sort_partis : _(""),
#                     proportionnelle_Hondt : _(""),
#                     proportionnelle_Hare : _("")}
define electypes = [majoritaire,
                    # majoritaire_random,
                    tirage_au_sort_population,
                    tirage_au_sort_partis,
                    proportionnelle_Hondt,
                    proportionnelle_Hare]
