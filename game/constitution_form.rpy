label constitution_form:
    $ npage = 0
    while _return != "finish":
        if _return in {'executif', 'execelect'}:
            if not "Hail to the Chief" in renpy.music.get_playing():
                play music "/music/Hail to the Chief instrumental.mp3" fadein 1.0 fadeout 1.0
        elif not renpy.music.get_playing() in audio.anthems:
            $ renpy.random.shuffle(audio.anthems)
            play music anthems fadein 1.0 fadeout 1.0
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
                    default validhd = [0]+validnpdistricts(houses[npage-2].seats) # nombres de circonscriptions valides
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
                        action [Function(applyelec, houses[npage-2], (validhd[distindex] if distindex else houses[npage-2].seats), electionfunc), Return('elections' if (npage<=len(houses)) else 'executif')]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename=='executif':
                    hbox:
                        xfill True
                        text _("Page {} : Executive").format(npage) xalign .5 color gui.hover_color size 50
                    null height gui.choice_spacing+gui.pref_spacing
                    default execorigin = 'people'
                    default nseats = 1
                    default exenamea = _('President')
                    default exenamea_edit = ScreenVariableInputValue('exenamea')
                    default exenameb = _('Consul')
                    default exenameb_edit = ScreenVariableInputValue('exenameb')
                    default exenamec = _('Executive')
                    default exenamec_edit = ScreenVariableInputValue('exenamec')
                    default vetopower = False
                    default vetoverride = False
                    default superindex = 0
                    default superlist = [(_("50%"), .5), (_("Three fifth, or 60%"), .6), (_("Two thirds, or 67%"), 2.0/3), (_("Three fourths, or 75%"), .75), (_("Four fifths, or 80%"), .8), (_("Nine tenths, or 90%"), .9), (_("Unanimity"), 1)]
                    hbox:
                        xfill True
                        text _("Origin of the Executive branch") yalign .5
                        vbox:
                            xalign 1.0
                            # xfill True
                            xmaximum .6
                            style_prefix "constform_radio"
                            textbutton _("No executive branch (Parliament governs directly)"):
                                action SetScreenVariable("execorigin", False)
                                sensitive houses
                            for hous in houses:
                                textbutton hous.name action SetScreenVariable("execorigin", hous)
                            # if not len(houses):
                            #     textbutton _("No parliamentary House")
                            textbutton _("Direct Popular Vote") action SetScreenVariable("execorigin", 'people')
                    null height gui.choice_spacing
                    if execorigin:
                        if nseats==1:
                            button:
                                xmargin 30
                                style_prefix None
                                xalign 0.5
                                key_events True
                                action [If(exenamea.strip(), None, SetScreenVariable('exenamea', _("Chancellor"))), exenamea_edit.Toggle()]
                                input:
                                    value exenamea_edit
                                    color gui.hover_color
                                    size 50
                                    pixel_width 1000
                        elif nseats in {2, 3}:
                            button:
                                xmargin 30
                                style_prefix None
                                xalign 0.5
                                key_events True
                                action [If(exenameb.strip(), None, SetScreenVariable('exenameb', _("President"))), exenameb_edit.Toggle()]
                                input:
                                    prefix _('Co-')
                                    suffix _('s')
                                    value exenameb_edit
                                    color gui.hover_color
                                    size 50
                                    pixel_width 1000
                        else:
                            button:
                                xmargin 30
                                style_prefix None
                                xalign 0.5
                                key_events True
                                action [If(exenamec.strip(), None, SetScreenVariable('exenamec', _("National"))), exenamec_edit.Toggle()]
                                input:
                                    suffix _(' Council')
                                    value exenamec_edit
                                    color gui.hover_color
                                    size 50
                                    pixel_width 1000
                        hbox:
                            xfill True
                            text _("Head of the Executive branch") yalign .5
                            hbox:
                                xalign 1.0
                                yalign .5
                                style_prefix "constform_selector"
                                textbutton "-1" action SetScreenVariable("nseats", nseats-1) sensitive (nseats-1 > 0)
                                if nseats == 1:
                                    text _("{} {}").format(nseats, exenamea)
                                elif nseats in {2, 3}:
                                    text _("{} {}s").format(nseats, exenameb)
                                else:
                                    text _("{} members of the {} Council").format(nseats, exenamec)
                                textbutton "+1" action SetScreenVariable("nseats", nseats+1) sensitive (nseats+1 <= (.1*min([house.seats for house in houses]) if houses else 25))
                                # on ne peut pas avoir plus de sièges que 1 ou 10% de la chambre moins peuplée si on a des chambres, ou 25 si on n'en a pas
                        if houses:
                            hbox:
                                xfill True
                                style_prefix "constform_radio"
                                text _("Veto power") yalign .5
                                textbutton (_('Yes') if vetopower else _('No')):
                                    action ToggleScreenVariable("vetopower", True, False)
                                    selected vetopower
                        if vetopower:
                            hbox:
                                xfill True
                                text _("Overridable") yalign .5
                                vbox:
                                    xalign 1.0
                                    # xfill True
                                    xmaximum .6
                                    style_prefix "constform_radio"
                                    textbutton _("No") action SetScreenVariable("vetoverride", False)
                                    for hous in houses:
                                        textbutton _("by Supermajority in the {}").format(hous.name) action SetScreenVariable("vetoverride", hous)
                                    textbutton _("by Supermajority in every House") action SetScreenVariable("vetoverride", 'each')
                                    textbutton _("by Supermajority in joint Congress") action SetScreenVariable("vetoverride", 'joint')
                            if vetoverride:
                                hbox:
                                    xfill True
                                    text _("Supermajority") yalign .5
                                    hbox:
                                        xalign 1.0
                                        yalign .5
                                        style_prefix "constform_selector"
                                        textbutton "Less" action SetScreenVariable("superindex", superindex-1) sensitive (superindex-1 >= 0)
                                        text str(superlist[superindex][0])
                                        textbutton "More" action SetScreenVariable("superindex", superindex+1) sensitive (superindex+1 < len(superlist))# and superindex
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive (exenamea if nseats==1 else exenameb if nseats in {2, 3} else exenamec)
                        action [Function(create_exec, (exenamea if nseats==1 else 'Co-'+exenameb+'s' if nseats in {2, 3} else exenamec+' Council'), execorigin, nseats, vetopower, vetoverride, superlist[superindex][1]), Return('execelect' if execorigin=='people' else "population")]
                    null height gui.choice_spacing+gui.pref_spacing
                    # TODO
                    # page exécutif
                    # si il n'y a pas de parlement, obliger que l'exécutif soit élu au suffrage direct
                    # constituer le pouvoir exécutif

                elif pagename=='execelect':
                    hbox:
                        xfill True
                        text _("Page {} : Elections for the {}").format(npage, executive.name) xalign .5 color gui.hover_color size 50
                    null height gui.choice_spacing+gui.pref_spacing
                    default distindex = 0 # indice donnant le nombre d'élus par circonscription, 0 si ils sont tous dans une seule circo
                    default validhd = [0]+validnpdistricts(executive.seats) # nombres de circonscriptions valides
                    default electionfunc = False # fonction d'attribution des sièges à partir des résultats du vote
                    if executive.seats>1:
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
                            text _("Number of seats per electoral district")+(_(" (Districts : {})").format(executive.seats/validhd[distindex]) if distindex else "") yalign .5
                            hbox:
                                xalign 1.0
                                yalign .5
                                style_prefix "constform_selector"
                                textbutton "-1" action SetScreenVariable("distindex", distindex-1) sensitive (distindex-1 > 0)
                                if distindex == 0:
                                    text _("{} (nationwide district)").format(executive.seats)
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
                                    sensitive (fonk in validfuncs((distindex if executive.seats>1 else 1)))
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive electionfunc in validfuncs((distindex if executive.seats>1 else 1))
                        action [Function(applyelec, executive, (validhd[distindex] if distindex else executive.seats), electionfunc), Return('population')]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename=='population':
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
        avec le bon nom, la bonne période de renouvellement et le bon nombre de sièges
        '''
        for khouse in range(nhouses):
            houses.append(House(housenames[khouse], nseats=houseseats[khouse], election_period=houseperiods[khouse]))
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

    def old_validnpdistricts(house):
        liz = [x for x in range(1, house.seats+1) if (float(house.seats)/x) == float(int(house.seats/x)) and x != house.seats]
        for uhouse in house.children:
            liz = [x for x in range(1, uhouse.seats+1) if (float(uhouse.seats)/x) == float(int(uhouse.seats/x)) and x in liz]
        return liz

    def validnpdistricts(nseats):
        '''
        Les nombres valides d'élus par circonscription, pour partager nseats sièges
        '''
        return [x for x in range(1, nseats+1) if (float(nseats)/x) == float(int(nseats/x)) and x != nseats]

    def validfuncs(circoseats):
        if circoseats == 1: # si un seul district
            return [f for f in electypes if f not in {proportionnelle_Hondt, proportionnelle_Hare}]
        else:
            return [f for f in electypes]

    def applyelec(house, circoseats, fonk):
        # house.elect_types = [(house.seats(), fonk, circoseats)]
        house.circos = [(circoseats, fonk) for k in range(house.seats/circoseats)]
        return

    def create_exec(name, origin, nseats, vetopower, vetoverride, supermajority):
        if origin:
            global executive
            executive = Executive(name, origin, nseats, vetopower, vetoverride, supermajority)
        return
