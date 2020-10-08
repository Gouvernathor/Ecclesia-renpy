label constitution_form:
    # play music laplaylistaléatoiredesmusiquespolitiques
    $ npage = 0
    while _return != "finish":
        $ npage += 1
        call screen constit(npage, pagename=_return) with Fade(.5, .5, .5, color='#fff')
    with Dissolve(3)
    stop music fadeout 1.0
    e "hey"
    pause
    # hide screen constit
    jump start

screen constit(npage, pagename=''):
    add Null() # pour empécher l'utilisateur de cliquer et de quitter la création de constitution
    style_prefix "constform"
    vbox:
        null height gui.choice_spacing+gui.pref_spacing
        hbox:
            xfill True
            text _("Constitution") xalign .5 color gui.hover_color size 150
        null height gui.choice_spacing+gui.pref_spacing
        viewport:
            xmaximum .95
            align (.5, .5)
            mousewheel True
            draggable True
            vbox:
                if npage==1:
                    hbox:
                        xfill True
                        text _("Page 1 : Legislature") xalign .5 color gui.hover_color size 50
                    null height gui.choice_spacing+gui.pref_spacing
                    default nHouses = 1
                    default housenames = [_("House n°")+str(k+1) for k in range(maxnhouses)]
                    default housenames_edit = [DictInputValue(housenames, k, default=False) for k in range(maxnhouses)]
                    default houseperiods = [48 for k in range(maxnhouses)]
                    default houseseats = [100 for k in range(maxnhouses)]
                    # default housestaggering = [False for k in range(maxnhouses)]
                    hbox:
                        xfill True
                        text _("Number of Houses of Congress/Parliament") yalign .5
                        vbox:
                            xalign 1.0
                            style_prefix "constform_radio"
                            textbutton _("None") action [SetScreenVariable("nHouses", 0), DisableAllInputValues()]
                            textbutton _("One") action [SetScreenVariable("nHouses", 1), DisableAllInputValues()]
                            textbutton _("Two") action [SetScreenVariable("nHouses", 2), DisableAllInputValues()]
                            # mettre à jour ici en cas de modification de maxnhouses
                    null height gui.choice_spacing
                    for khouse index khouse in range(nHouses):
                        button:
                            xmargin 30
                            style_prefix None
                            xalign 0.5
                            key_events True
                            action [If(housenames[khouse].strip(), None, SetDict(housenames, khouse, _("House n°")+str(khouse+1))), housenames_edit[khouse].Toggle()]
                            # action housenames_edit[khouse].Toggle()
                            input:
                                value housenames_edit[khouse]
                                color gui.hover_color
                                size 50
                                pixel_width 1000
                        hbox:
                            xfill True
                            text _("Term of office") yalign .5
                            hbox:
                                xalign 1.0
                                yalign .5
                                style_prefix "constform_selector"
                                textbutton "-12" action SetDict(houseperiods, khouse, houseperiods[khouse]-12) sensitive (houseperiods[khouse]-12>=0)
                                textbutton "-1" action SetDict(houseperiods, khouse, houseperiods[khouse]-1) sensitive (houseperiods[khouse]-1>=0)
                                if houseperiods[khouse]:
                                    text str(houseperiods[khouse])+" month"+['s', ''][houseperiods[khouse]==1]
                                else:
                                    text _("Life terms (no election)")
                                textbutton "+1" action SetDict(houseperiods, khouse, houseperiods[khouse]+1)
                                textbutton "+12" action SetDict(houseperiods, khouse, houseperiods[khouse]+12)
                        hbox:
                            xfill True
                            text _("Number of seats") yalign .5
                            hbox:
                                style_prefix "constform_selector"
                                xalign 1.0
                                yalign .5
                                textbutton "-100" action SetDict(houseseats, khouse, houseseats[khouse]-100) sensitive (houseseats[khouse]-100>0)# max(0, housestaggering[khouse]-1))
                                textbutton "-10" action SetDict(houseseats, khouse, houseseats[khouse]-10) sensitive (houseseats[khouse]-10>0)# max(0, housestaggering[khouse]-1))
                                textbutton "-1" action SetDict(houseseats, khouse, houseseats[khouse]-1) sensitive (houseseats[khouse]-1>0)# max(0, housestaggering[khouse]-1))
                                text str(houseseats[khouse])
                                textbutton "+1" action SetDict(houseseats, khouse, houseseats[khouse]+1)
                                textbutton "+10" action SetDict(houseseats, khouse, houseseats[khouse]+10)
                                textbutton "+100" action SetDict(houseseats, khouse, houseseats[khouse]+100)
                        # if houseseats[khouse]>1:
                        #     hbox:
                        #         xfill True
                        #         style_prefix "constform_radio"
                        #         text _("Staggering") yalign .5
                        #         textbutton (_('Yes') if housestaggering[khouse] else _('No')):
                        #             action If(housestaggering[khouse], SetDict(housestaggering, khouse, False), SetDict(housestaggering, khouse, 2))
                        #             selected housestaggering[khouse]
                        # if housestaggering[khouse]:
                        #     hbox:
                        #         xfill True
                        #         text _("Number of staggering classes") yalign .5
                        #         hbox:
                        #             xalign 1.0
                        #             style_prefix "constform_selector"
                        #             textbutton "-1" action SetDict(housestaggering, khouse, housestaggering[khouse]-1) sensitive (housestaggering[khouse]-1>=2)
                        #             text str(housestaggering[khouse])
                        #             textbutton "+1" action SetDict(housestaggering, khouse, housestaggering[khouse]+1) sensitive (housestaggering[khouse]+1<=houseseats[khouse])
                        # ajouter le choix de la fonction de répartition des votes
                        null height gui.choice_spacing
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive ([bool(housenames[k].strip()) for k in range(nHouses)] == [True for k in range(nHouses)])
                        # action [Function(create_houses, nHouses, housenames, houseperiods, houseseats, housestaggering), Hide('constit'), Show('constit', transition=Fade(.5, .5, .5, color='#fff'), npage=2, pagename=('elections' if (nHouses and (True in [bool(houseperiods[k]) for k in range(nHouses)])) else 'executif'))]
                        # action [Function(create_houses, nHouses, housenames, houseperiods, houseseats, housestaggering), Hide('constit', transition=Fade(.5, .5, .5, color='#fff')), Return(('elections' if (nHouses and (True in [bool(houseperiods[k]) for k in range(nHouses)])) else 'executif'))]
                        # action [Function(create_houses, nHouses, housenames, houseperiods, houseseats, housestaggering), Return(('elections' if (nHouses and (True in [bool(houseperiods[k]) for k in range(nHouses)])) else 'executif'))]
                        action [Function(create_houses, nHouses, housenames, houseperiods, houseseats), Return(('elections' if (nHouses and (True in [bool(houseperiods[k]) for k in range(nHouses)])) else 'executif'))]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename=='elections':
                    hbox:
                        xfill True
                        text _("Page {} : Elections for the {}").format(npage, houses[npage-2].name) xalign .5 color gui.hover_color size 50
                    null height gui.choice_spacing+gui.pref_spacing
                    default distindex = 0 # indice donnant le nombre d'élus par circonscription, 0 si ils sont tous dans une seule circo
                    default validhd = [0]+validnpdistricts(houses[npage-2]) # nombres de circonscriptions valides
                    default electionfunc = False # fonction d'attribution des sièges à partir des résultats du vote
                    # $ print(validhd)
                    hbox:
                        xfill True
                        style_prefix "constform_radio"
                        text _("Electoral Districts") yalign .5
                        textbutton (_('Yes') if distindex else _('No')):
                            action ToggleScreenVariable('distindex', 0, 1)
                            selected distindex
                    null height gui.choice_spacing
                    hbox:
                        xfill True
                        text _("Number of seats per electoral district")+(_(" (Districts : {})").format(houses[npage-2].seats/validhd[distindex]) if distindex else "") yalign .5
                        hbox:
                            xalign 1.0
                            yalign .5
                            style_prefix "constform_selector"
                            textbutton "-1" action SetScreenVariable("distindex", distindex-1) sensitive (distindex-1 > 0)
                            if distindex == 0:
                                text _("{} (nationwide district)").format(houses[npage-2].seats)
                            else:
                                text str(validhd[distindex])
                            textbutton "+1" action SetScreenVariable("distindex", distindex+1) sensitive (distindex+1 < len(validhd)) and distindex
                    null height gui.choice_spacing
                    hbox:
                        xfill True
                        text _("Election type") yalign .5
                        vbox:
                            xalign 1.0
                            style_prefix "constform_radio"
                            for fonk in [f for f in electypes]:
                                textbutton _(fonk.__name__):
                                    action SetScreenVariable("electionfunc", fonk)
                                    sensitive (fonk in validfuncs(distindex))
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive electionfunc in validfuncs(distindex)
                        action [Function(applyelec, houses[npage-2], validhd[distindex], electionfunc), Return('elections' if (npage<=len(houses)) else 'executif')]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename=='executif':
                    hbox:
                        xfill True
                        text _("Page {} : Executive").format(npage) xalign .5 color gui.hover_color size 50
                    # TODO
                    # page exécutif
                    # si il n'y a pas de parlement, obliger que l'exécutif soit élu au suffrage direct
                    # constituer le pouvoir exécutif

                elif pagename=='opinions':
                    hbox:
                        xfill True
                        text _("Annex 1 : Population & Opinions")
                    null height gui.choice_spacing+gui.pref_spacing
                    # default
                    # TODO

                elif pagename=='partis':
                    hbox:
                        xfill True
                        text _("Annex 2 : Political Organizations")
                    # TODO
                    # dernière page, bouton rouge pour enact la constitution
                # add "prison03"# maxsize (.8, 5.0)
                # add "prison03"# maxsize (.8, 5.0)
                # add "prison03"# maxsize (.8, 5.0)

style constform_button:
    xalign 1.0

style constform_radio_button is constform_button
style constform_radio_button:
    selected_foreground Image("gui/button/constform_selected_foreground.png", xzoom=-1.0, xalign=1.0)
    right_padding 30
    right_margin -15

style constform_selector_button is constform_button
style constform_selector_hbox:
    spacing 30

style constform_button_text:
    font gui.text_font
    selected_idle_color '#000'
style constform_radio_button_text is constform_button_text
style constform_selector_button_text is constform_button_text

style constform_text:
    size 35
    color '#000'
style constform_radio_text is constform_text
style constform_selector_text is constform_text

style big_blue_button:
    background '#009'
    hover_background '#03f'
    insensitive_background '#005'
    xalign .5
style big_blue_button_text:
    color '#fff'
    insensitive_color '#aaa'
    size 50
style big_red_button:
    background '#900'
    hover_background '#f00'
    insensitive_background '#500'
    xalign .5
style big_red_button_text is big_blue_button_text

init python:
    def create_houses(nhouses, housenames, houseperiods, houseseats):
        '''
        Crée les House pour chacune des chambres
        avec le bon nom et la bonne période de renouvellement
        mais avec tous les sièges dans une seule circo et sans fonction de répartition
        (qui sera à rentrer manuellement plus tard)
        '''
        for khouse in range(nhouses):
            houses.append(House(housenames[khouse], circos=[(houseseats[khouse], None)], election_period=houseperiods[khouse]))
            # childlist = []
            # if not housestaggering[khouse]:
            #     housestaggering[khouse] = 1
            # for kclass in range(housestaggering[khouse]):
            #     if housestaggering[khouse] == 1:
            #         sts = houseseats[khouse]
            #         off = 0
            #     else:
            #         if kclass != housestaggering[khouse]-1:
            #             sts = int(houseseats[khouse]/float(housestaggering[khouse]))
            #         else:
            #             sts = houseseats[khouse] - (housestaggering[khouse]-1)*int(houseseats[khouse]/float(housestaggering[khouse]))
            #         off = kclass*houseperiods[khouse]/housestaggering[khouse]
            #     childlist.append(UnderHouse(seats=sts, election_offset=off))
            # houses.append(House(housenames[khouse].strip(), children=childlist, election_period=houseperiods[khouse]))
        return

    def validnpdistricts(house):
        liz = [x for x in range(1, house.seats+1) if (float(house.seats)/x) == float(int(house.seats/x)) and x != house.seats]
        # for uhouse in house.children:
        #     liz = [x for x in range(1, uhouse.seats+1) if (float(uhouse.seats)/x) == float(int(uhouse.seats/x)) and x in liz]
        return liz

    def validfuncs(circoseats):
        if circoseats == 1: # si un seul district
            return [f for f in electypes if f not in {majoritaire_random, proportionnelle_Hondt, proportionnelle_Hare}]
        else:
            return [f for f in electypes if f != majoritaire]

    def applyelec(house, circoseats, fonk):
        # house.elect_types = [(house.seats(), fonk, circoseats)]
        house.circos = [(circoseats, fonk) for k in range(house.seats/circoseats)]
        return
