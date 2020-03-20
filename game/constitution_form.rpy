
label constitution_form:
    call screen constit(1)# with None
    with Dissolve(3)
    e "hey"
    pause
    # hide screen constit
    jump start

screen constit(page):
    add Null()
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
            # scrollbars "vertical"
            vbox:
                if page==1:
                    hbox:
                        xfill True
                        text _("Page 1 : Legislature") xalign .5 color gui.hover_color size 50
                    null height gui.choice_spacing+gui.pref_spacing
                    default kHouses = 1
                    default housenames = [_("House n°")+str(k+1) for k in range(2)]
                    default housenames_edit = [DictInputValue(housenames, k, default=False) for k in range(2)]
                    # default housenames_edit = [NotFalseDictInputValue(housenames, k, defaultvalue=_("House n°")+str(k+1), default=False) for k in range(2)]
                    default houseperiods = [48, 48]
                    default houseseats = [100, 100]
                    default housestaggering = [False, False]
                    hbox:
                        xfill True
                        text _("Number of Houses of Congress/Parliament") yalign .5
                        vbox:
                            xalign 1.0
                            style_prefix "constform_radio"
                            textbutton _("None") action [SetScreenVariable("kHouses", 0), DisableAllInputValues()]
                            textbutton _("One") action [SetScreenVariable("kHouses", 1), DisableAllInputValues()]
                            textbutton _("Two") action [SetScreenVariable("kHouses", 2), DisableAllInputValues()]
                    null height gui.choice_spacing
                    for khouse index khouse in range(kHouses):
                        button:
                            xmargin 30
                            style_prefix None
                            xalign 0.5
                            key_events True
                            # action [If(housenames[khouse].strip(), None, SetDict(housenames, khouse, _("House n°")+str(khouse+1))), housenames_edit[khouse].Toggle()]
                            action housenames_edit[khouse].Toggle()
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
                                textbutton "-100" action SetDict(houseseats, khouse, houseseats[khouse]-100) sensitive (houseseats[khouse]-100>max(0, housestaggering[khouse]-1))
                                textbutton "-10" action SetDict(houseseats, khouse, houseseats[khouse]-10) sensitive (houseseats[khouse]-10>max(0, housestaggering[khouse]-1))
                                textbutton "-1" action SetDict(houseseats, khouse, houseseats[khouse]-1) sensitive (houseseats[khouse]-1>max(0, housestaggering[khouse]-1))
                                text str(houseseats[khouse])
                                textbutton "+1" action SetDict(houseseats, khouse, houseseats[khouse]+1)
                                textbutton "+10" action SetDict(houseseats, khouse, houseseats[khouse]+10)
                                textbutton "+100" action SetDict(houseseats, khouse, houseseats[khouse]+100)
                        if houseseats[khouse]>1:
                            hbox:
                                xfill True
                                style_prefix "constform_radio"
                                text _("Staggering") yalign .5
                                textbutton (_('Yes') if housestaggering[khouse] else _('No')) action If(housestaggering[khouse], SetDict(housestaggering, khouse, False), SetDict(housestaggering, khouse, 2)) selected housestaggering[khouse]
                        if housestaggering[khouse]:
                            hbox:
                                xfill True
                                text _("Number of staggering classes") yalign .5
                                hbox:
                                    xalign 1.0
                                    style_prefix "constform_selector"
                                    textbutton "-1" action SetDict(housestaggering, khouse, housestaggering[khouse]-1) sensitive (housestaggering[khouse]-1>2)
                                    text str(housestaggering[khouse])
                                    textbutton "+1" action SetDict(housestaggering, khouse, housestaggering[khouse]+1) sensitive (housestaggering[khouse]+1<=houseseats[khouse])
                        # ajouter le choix de la fonction de répartition des votes
                        null height gui.choice_spacing
                    null height gui.pref_spacing
                    # bouton bleu confirmation pour passer à la page suivante
                    textbutton _("Continue") style "big_blue_button" sensitive ([bool(k.strip()) for k in housenames] == [True for k in housenames]) action [Return()]
                    # ne pas oublier de strip les noms
                    null height gui.choice_spacing+gui.pref_spacing

                    # page 2
                    # si il n'y a pas de parlement, obliger que l'exécutif soit élu au suffrage direct
                    # constituer le pouvoir exécutif
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
    xalign .5
style big_blue_button_text:
    color '#fff'
    size 50
