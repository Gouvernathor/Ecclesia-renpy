init python:
    import types
    def is_subclass(a, b, /):
        return isinstance(a, type) and issubclass(a, b)

label constitution_form:
    $ npage = 0
    while _return != "finish":
        if _return in {'executif', 'execelect'}:
            if "/music/Hail to the Chief instrumental.mp3" != renpy.music.get_playing():
                play music "/music/Hail to the Chief instrumental.mp3" fadeout 3.0
        elif not renpy.music.get_playing() in audio.anthems:
            $ renpy.random.shuffle(audio.anthems)
            play music anthems fadein .5 fadeout 1.0
        $ npage += 1
        call screen constit(npage, pagename=_return, _with_none=False) with Fade(.5, .5, .5, color='#fff')
    with Dissolve(3)
    stop music fadeout 1.0
    return

screen constit_title2(value):
    hbox:
        xfill True
        text value:
            xalign .5
            color gui.hover_color
            size 50

screen constit_election_type(distindex, votingfunc):
    text _("Election type") xalign .5
    hbox:
        xfill True
        vbox:
            # voting kinds
            xalign .0
            style_prefix "constform_radio"
            for fonk in (f for f in voting_methods):
                textbutton __(fonk.name):
                    xalign .0
                    action SetScreenVariable("votingfunc", fonk)
        vbox:
            # attribution kinds
            xalign 1.0
            style_prefix "constform_radio"
            for fonk in (f for f in attribution_methods):
                textbutton __(fonk.name):
                    action SetScreenVariable("attribfunc", fonk)
                    sensitive (fonk in validattribfuncs(distindex, votingfunc))

screen constit_elect_districts(house, distindex, validhd):
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
        text _("Number of seats per electoral district")+(_(" (Districts : {})").format(house.seats//validhd[distindex]) if distindex else "") yalign .5
        hbox:
            xalign 1.0
            yalign .5
            style_prefix "constform_selector"
            textbutton "-1" action SetScreenVariable("distindex", distindex-1) sensitive (distindex-1 > 0)
            if distindex == 0:
                text _("[house.seats] (nationwide district)")
            else:
                text str(validhd[distindex])
            textbutton "+1" action SetScreenVariable("distindex", distindex+1) sensitive (distindex+1 < len(validhd)) and distindex
    null height gui.choice_spacing

screen constit(npage, pagename=''):
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
                if npage == 1:
                    use constit_title2(_("Article 1 : Legislature"))
                    null height gui.choice_spacing+gui.pref_spacing
                    default nHouses = 1
                    default housenames = [_("House n°{}").format(k+1) for k in range(maxnhouses)]
                    default housenames_edit = [DictInputValue(housenames, k, default=False) for k in range(maxnhouses)]
                    default houseperiods = [48]*maxnhouses
                    default houseseats = [100]*maxnhouses
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
                            style_prefix "constform_name"
                            action [If(housenames[khouse].strip(), None, SetDict(housenames, khouse, _("House n°{}").format(khouse+1))), housenames_edit[khouse].Toggle()]
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
                                    if houseperiods[khouse] == 1:
                                        text _("1 month")
                                    else:
                                        text _("{} months").format(houseperiods[khouse])
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
                                textbutton "-100" action SetDict(houseseats, khouse, houseseats[khouse]-100) sensitive (houseseats[khouse]-100>0)
                                textbutton "-10" action SetDict(houseseats, khouse, houseseats[khouse]-10) sensitive (houseseats[khouse]-10>0)
                                textbutton "-1" action SetDict(houseseats, khouse, houseseats[khouse]-1) sensitive (houseseats[khouse]-1>0)
                                text str(houseseats[khouse])
                                textbutton "+1" action SetDict(houseseats, khouse, houseseats[khouse]+1)
                                textbutton "+10" action SetDict(houseseats, khouse, houseseats[khouse]+10)
                                textbutton "+100" action SetDict(houseseats, khouse, houseseats[khouse]+100)
                        null height gui.choice_spacing
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive all(name.strip() for name in housenames)
                        action [Function(create_houses, nHouses, housenames, houseperiods, houseseats), Return(('elections' if (nHouses and any(houseperiods)) else 'executif'))]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename == 'elections':
                    use constit_title2(_("Article [npage] : Elections for the {}").format(houses[npage-2].name))
                    null height gui.choice_spacing+gui.pref_spacing
                    default distindex = 0 # indice donnant le nombre d'élus par circonscription, 0 si ils sont tous dans une seule circo
                    default validhd = [0]+validnpdistricts(houses[npage-2].seats) # nombres de circonscriptions valides
                    default votingfunc = False # fonction de modalité de vote
                    default attribfunc = False # fonction d'attribution des sièges à partir des résultats du vote
                    default thresh = 0
                    use constit_elect_districts(houses[npage-2], distindex, validhd)
                    use constit_election_type(distindex, votingfunc)
                    if isinstance(getattr(attribfunc, "threshold", None), types.MemberDescriptorType):
                        hbox:
                            xfill True
                            text _("Electoral threshold") yalign .5
                            hbox:
                                xalign 1.0
                                yalign .5
                                style_prefix "constform_selector"
                                textbutton "-5%" action SetScreenVariable("thresh", thresh-.05) sensitive (thresh-.05 >= 0)
                                if thresh == 0:
                                    text _("None")
                                else:
                                    text str(int(thresh*100))+"%"
                                textbutton "+5%" action SetScreenVariable("thresh", thresh+.05) sensitive (thresh+.05 <= .3)
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive attribfunc in validattribfuncs(distindex, votingfunc)
                        action [Function(applyelec, houses[npage-2], (validhd[distindex] if distindex else houses[npage-2].seats), votingfunc, attribfunc, thresh), Return('elections' if (npage<=len(houses)) else 'executif')]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename == 'executif':
                    use constit_title2(_("Article [npage] : Executive"))
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
                    default superlist = [(_("50%"), .5),
                                         (_("Three fifth, or 60%"), .6),
                                         (_("Two thirds, or 67%"), 2.0/3),
                                         (_("Three fourths, or 75%"), .75),
                                         (_("Four fifths, or 80%"), .8),
                                         (_("Nine tenths, or 90%"), .9),
                                         (_("Unanimity"), 1)]
                    hbox:
                        xfill True
                        text _("Origin of the Executive branch") yalign .5
                        vbox:
                            xalign 1.0
                            # xfill True
                            xmaximum .6
                            style_prefix "constform_radio"
                            # textbutton _("No executive branch (Parliament governs directly)"):
                            #     action SetScreenVariable("execorigin", False)
                            #     sensitive houses
                            for hous in houses:
                                textbutton hous.name action SetScreenVariable("execorigin", hous)
                            # if not len(houses):
                            #     textbutton _("No parliamentary House")
                            textbutton _("Direct Popular Vote") action SetScreenVariable("execorigin", 'people')
                    null height gui.choice_spacing
                    if execorigin:
                        button:
                            style_prefix "constform_name"
                            if nseats == 1:
                                action [If(exenamea.strip(), None, SetScreenVariable('exenamea', _("Chancellor"))), exenamea_edit.Toggle()]
                                input:
                                    value exenamea_edit
                                    color gui.hover_color
                                    size 50
                                    pixel_width 1000
                            elif nseats in (2, 3):
                                action [If(exenameb.strip(), None, SetScreenVariable('exenameb', _("President"))), exenameb_edit.Toggle()]
                                input:
                                    prefix _('Co-')
                                    suffix _('s')
                                    value exenameb_edit
                                    color gui.hover_color
                                    size 50
                                    pixel_width 1000
                            else:
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
                                    text _("[nseats] [exenamea]")
                                elif nseats in (2, 3):
                                    text _("[nseats] [exenameb]s")
                                else:
                                    text _("[nseats] members of the [exenamec] Council")
                                textbutton "+1" action SetScreenVariable("nseats", nseats+1) sensitive (nseats+1 <= (.1*min([house.seats for house in houses]) if houses else 25))
                                # on ne peut pas avoir plus de sièges que 10% de la chambre moins peuplée si on a des chambres, ou 25 si on n'en a pas
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
                                        textbutton _("by Supermajority in the [hous.name]") action SetScreenVariable("vetoverride", hous)
                                    if len(houses)>1:
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
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive (exenamea if nseats==1 else exenameb if nseats in {2, 3} else exenamec)
                        action [Function(create_exec, (exenamea if nseats==1 else 'Co-'+exenameb+'s' if nseats in {2, 3} else exenamec+' Council'), execorigin, nseats, vetopower, vetoverride, superlist[superindex][1]), Return('execelect' if execorigin=='people' else "trivia")]
                    null height gui.choice_spacing+gui.pref_spacing
                    # TODO
                    # page exécutif
                    # si il n'y a pas de parlement, obliger que l'exécutif soit élu au suffrage direct
                    # constituer le pouvoir exécutif

                elif pagename == 'execelect':
                    use constit_title2(_("Article [npage] : Elections for the [executive.name]"))
                    null height gui.choice_spacing+gui.pref_spacing
                    default distindex = 0 # indice donnant le nombre d'élus par circonscription, 0 si ils sont tous dans une seule circo
                    default validhd = [0]+validnpdistricts(executive.seats) # nombres de circonscriptions valides
                    default votingfunc = False # fonction de modalité de vote
                    default attribfunc = False # fonction d'attribution des sièges à partir des résultats du vote
                    default execperiod = 60
                    hbox:
                        xfill True
                        text _("Term of office") yalign .5
                        hbox:
                            xalign 1.0
                            yalign .5
                            style_prefix "constform_selector"
                            textbutton "-12" action SetScreenVariable("execperiod", execperiod-12) sensitive (execperiod-12>=0)
                            textbutton "-1" action SetScreenVariable("execperiod", execperiod-1) sensitive (execperiod-1>=0)
                            if execperiod:
                                text str(execperiod)+" month"+['s', ''][execperiod==1]
                            else:
                                text _("Life terms (no election)")
                            textbutton "+1" action SetScreenVariable("execperiod", execperiod+1)
                            textbutton "+12" action SetScreenVariable("execperiod", execperiod+12)
                    if executive.seats>1:
                        use constit_elect_districts(executive, distindex, validhd)
                    use constit_election_type((distindex if executive.seats>1 else 1), votingfunc)
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        sensitive attribfunc in validattribfuncs((distindex if executive.seats>1 else 1), votingfunc)
                        action [Function(applyelec, executive, (validhd[distindex] if distindex else executive.seats), votingfunc, attribfunc, 0, execperiod), Return('trivia')]
                    null height gui.choice_spacing+gui.pref_spacing

                elif pagename == 'trivia':
                    use constit_title2(_("Article [npage] : National symbols"))
                    null height gui.choice_spacing+gui.pref_spacing
                    default key1 = ""
                    default key1_edit = ScreenVariableInputValue('key1', default=False)
                    default key2 = ""
                    default key2_edit = ScreenVariableInputValue('key2', default=False)
                    # ajouter un input de clés de génération pour les opinions et pour les élections
                    hbox:
                        xfill True
                        style_prefix "constform_keys"
                        text _("National Motto") yalign .5
                        button:
                            action key1_edit.Toggle()
                            input:
                                italic True
                                value key1_edit
                                pixel_width 1000
                                copypaste True
                    null height gui.choice_spacing
                    hbox:
                        xfill True
                        style_prefix "constform_keys"
                        text _("National Anthem") yalign .5
                        button:
                            action key2_edit.Toggle()
                            input:
                                italic True
                                value key2_edit
                                pixel_width 1000
                                copypaste True
                    null height gui.pref_spacing
                    textbutton _("Continue"):
                        style "big_blue_button"
                        action [If(key1, SetVariable("citikey", key1)), If(key2, Function(electrobj.seed, key2)), Return('population')]

                elif pagename == 'population':
                    use constit_title2(_("Annex 1 : Population"))
                    null height gui.choice_spacing+gui.pref_spacing
                    default citizens = max(10, minncitizen())
                    # afficher le nombre de subdivisions administratives (PPCM de tous les nombres de circos)
                    hbox:
                        xfill True
                        style_prefix "constform_radio"
                        text _("Total number of counties") yalign .5
                        textbutton str(ncounties()):
                            selected True
                            text_color '#000'
                    null height gui.choice_spacing
                    # demander le nombre de citoyen représentatif par subdivision
                        # mettre un truc RP, genre enlightened minds
                        # le nombre de citoyens par circo dans les chambres sera un multiple de ce nombre
                    hbox:
                        xfill True
                        text _("Enfranchised citizens per county")
                        hbox:
                            xalign 1.0
                            yalign .5
                            style_prefix "constform_selector"
                            textbutton "-1" action SetScreenVariable("citizens", citizens-1) sensitive (citizens-1 >= max(1, minncitizen()))
                            text "[citizens]"
                            textbutton "+1" action SetScreenVariable("citizens", citizens+1) sensitive (citizens+1 <= 50)
                    # null height gui.choice_spacing
                    # demander l'échelle de représentation
                        # pour avoir le nombre RP d'habitants dans les subdivisions et dans le pays
                        # sans incidence sur la simulation
                    hbox:
                        xfill True
                        text _("Portion of enfranchised inhabitants")
                        hbox:
                            xalign 1.0
                            yalign .5
                            style_prefix "constform_selector"
                            textbutton "÷10" action SetVariable("popscale", popscale*10) sensitive (popscale*10 < 1000000000)
                            if popscale == 1:
                                text "Everyone"
                            else:
                                text _("1 per [popscale] inhabitants")
                            textbutton "x10" action SetVariable("popscale", popscale//10) sensitive (popscale//10 >= 1)
                    null height gui.choice_spacing
                    # afficher le nombre total d'habitants (calculé, non-stocké)
                    hbox:
                        xfill True
                        style_prefix "constform_radio"
                        text _("Total population") yalign .5
                        textbutton str(ncounties()*citizens*popscale):
                            selected True
                            text_color '#000'
                    # afficher le nombre total de citoyens (calculé pour l'instant)
                    hbox:
                        xfill True
                        style_prefix "constform_radio"
                        text _("Total enfranchized population") yalign .5
                        textbutton str(ncounties()*citizens):
                            selected True
                            text_color '#000'
                    # afficher le nombre d'habitant par parlementaire (calculé, non-stocké)
                    hbox:
                        xfill True
                        style_prefix "constform_radio"
                        text _("Electeds per inhabitant") yalign .5
                        textbutton "1/"+str((ncounties()*citizens*popscale)/(sum([house.seats for house in houses+[executive]]))):
                            selected True
                            text_color '#000'
                    null height gui.pref_spacing
                    # textbutton _("Continue"):
                    #     style "big_blue_button"
                    #     sensitive True
                    #     action [Function(populate, citizens), Return('partis')]
                    # null height gui.choice_spacing+gui.pref_spacing
                    textbutton _("ENACT"):
                        style "big_red_button"
                        sensitive True
                        action [Function(populate, citizens), Return('finish')]
                    null height gui.choice_spacing+gui.pref_spacing
                    # dernière page, bouton rouge pour enact la constitution

                elif pagename == 'partis':
                    # page suspendue
                    # les partis n'ont rien à faire dans la constitution
                    # et grosse flemme de faire un menu pour les customiser
                    use constit_title2(_("Annex 2 : Political Organizations"))
                    null height gui.choice_spacing+gui.pref_spacing
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

style constform_radio_vbox:
    xsize None

style constform_text:
    size 35
    color '#000'
style constform_radio_text is constform_text
style constform_selector_text is constform_text
style constform_selector_text:
    ypadding 6

style constform_name_button:
    xmargin 30
    xpadding 15
    xalign .5
    key_events True
style constform_keys_button is constform_name_button
style constform_keys_button:
    xmargin 0
    # xpadding 100
    xminimum 200
    xalign 1.0
    background '#00000006'
style constform_keys_input is constform_text
style constform_keys_input:
    xalign .5

style big_blue_button:
    background '#009'
    hover_background '#03f'
    insensitive_background '#005'
    xalign .5
    xpadding 20
style big_blue_button_text:
    color '#fff'
    insensitive_color '#aaa'
    size 50
style big_red_button is big_blue_button
style big_red_button:
    background '#f00'
    hover_background '#f32'
    insensitive_background '#f88'
    xpadding 25
style big_red_button_text is big_blue_button_text
style big_red_button_text:
    size 80
    bold True

init python:
    import functools

    def create_houses(nhouses, housenames, houseperiods, houseseats):
        '''
        Crée les House pour chacune des chambres
        avec le bon nom, la bonne période de renouvellement et le bon nombre de sièges
        '''
        for _k, name, nseats, period in zip(range(nhouses), housenames, houseseats, houseperiods):
            houses.append(actors.House(name, nseats=nseats, election_period=period))
        return

    @functools.lru_cache
    def validnpdistricts(nseats):
        '''
        Les nombres valides d'élus par circonscription, pour partager nseats sièges
        Aka les diviseurs de nseats, 1 inclus et nseats exclus
        '''
        return [x for x in range(1, nseats) if ((nseats/x) == int(nseats/x))]

    def validattribfuncs(circoseats, votingfunc):
        '''
        Renvoie les modes d'élection valides pour désigner circoseats dans une seule circonscription
        '''
        if not is_subclass(votingfunc, voting_method.VotingMethod):
            return ()
        # si un seul siège à pourvoir, non-proportionnels
        attribk = attribution_methods
        if (circoseats == 1):
            attribk = (f for f in attribk if not issubclass(f, attribution_method.Proportional))
        return (f for f in attribk if f.taken_format == votingfunc.return_format)

    def applyelec(house, circoseats, votingtype, attribtype, thresh=None, period=60):
        if issubclass(attribtype, attribution_method.SuperMajority):
            thresh = .5

        kwargs = {}
        if thresh:
            kwargs = dict(threshold=thresh)

        votingfonk = votingtype()
        attribfonk = attribtype(nseats=circoseats, **kwargs)
        house.circos = [[circoseats, election_method.ElectionMethod(votingfonk, attribfonk), []] for _k in range(house.seats//circoseats)]
        if house == executive:
            house.election_period = period
        return

    def create_exec(name, origin, nseats, vetopower, vetoverride, supermajority):
        if origin:
            global executive
            executive = actors.Executive(name=name, nseats=nseats, origin=origin, vetopower=vetopower, vetoverride=vetoverride, supermajority=supermajority)
        return

    @functools.lru_cache
    def ppcm(a, *ot):
        if not ot:
            return a
        if (0 in ot) or not a:
            return 0
        b, *ot = ot
        if ot:
            return ppcm(ppcm(a, b), *ot)
        p = a*b
        while a != b:
            a, b = sorted((a, b))
            b -= a
        return p//a

    def ncounties():
        """
        Returns the number of counties, so for each House, for each class,
        all electoral districts have a set of counties, such that all the sets
        are the same size, and disjoints (two-by-two).
        """
        # pour chaque house et pour l'exécutif si il est élu par le peuple
        # diviser les circo en classes
        # faire une liste des nombres de circo dans chaque classe dans chaque chambre
        # et renvoyer le ppcm de tous ces nombres
        numbers = set()
        houzes = list(houses)
        if executive.origin == 'people':
            houzes.append(executive)
        for house in houzes:
            numbers.update(house.classes().values())
        return ppcm(*numbers)

    def minncitizen():
        mins = set()
        ncou = ncounties()
        houzes = list(houses)
        if executive.origin == 'people':
            houzes.append(executive)
        for house in houzes:
            clss = house.classes()
            for (nseats, _elec), ncirco in clss.items():
                mins.add(nseats//(ncou/ncirco))
                # nombre d'élus par circo divisé par le nombre de comtés dans la circo
        # prendre le max
        return max(mins)

    def populate(ncitizens):
        """
        Generates a list of `ncitizen` Citizens,
        and stores it in the global `citizenpool` variable.
        Then, assigns citizens to electoral districts so that each
        citizen has one and only one electoral district, and each
        electoral district of the same class has the same number of citizens.
        """
        global citizenpool
        randomobj = renpy.random.Random(citikey)
        citizenpool = [actors.Citizen(randomobj=randomobj) for k in range(ncitizens*ncounties())]
        houzes = list(houses)
        if executive.origin == 'people':
            houzes.append(executive)
        for house in houzes:
            ramobj = renpy.random.Random(house.name)
            print(f"Populating {house.name}'s electoral district(s)")
            for (cl_nseats, cl_elec), ncirco in house.classes().items():
                citpool = list(citizenpool) # on vide celle-là mais pas la globale
                ramobj.shuffle(citpool)
                for (nseats, elec, citilist) in house.circos:
                    if (nseats, elec) == (cl_nseats, cl_elec):
                        # print(len(circo))
                        # print(len(citpool))
                        # print(ncitizens*ncounties()/ncirco)
                        boundary = ncitizens*ncounties()//ncirco
                        citilist[:], citpool = citpool[:boundary], citpool[boundary:]
            if citpool:
                raise RuntimeError("The citizens were not distributed properly.\nPerhaps the number of citizens was unaccurately set ?")
        return
