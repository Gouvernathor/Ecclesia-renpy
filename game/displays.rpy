screen displayer():
    button: # Houses, afficher les chambres
        xalign 0.0
        yalign 0.0
        padding (0, 0, 0, 0)
        # action [Show("Houses", CropMove(.5, "custom", (0.0, 0.0, 0.0, 0.0), (0.0, 0.0), (0.0, 0.0, 1.0, 1.0), (0.0, 0.0)))]
        action [Show("houses"), With(CropMove(.5, "custom", (0.0, 0.0, 0.0, 0.0), (0.0, 0.0), (0.0, 0.0, 1.0, 1.0), (0.0, 0.0)))]
        fixed:
            fit_first True
            add At(Solid('#f00', xsize=100, ysize=100), Transform(rotate=45), Transform(crop=(.5, .5, .5, .5), crop_relative=True))
            text "H":
                # anchor (0.0, 0.0)
                # pos (12, 4)
                bold True
                anchor (1., .8)
                pos (.5, .5)

    button: # stats
        xalign 1.0
        yalign 0.0
        padding (0, 0, 0, 0)
        action [Show("stats", CropMove(.5, "custom", (1.0, 0.0, 0.0, 0.0), (1.0, 0.0), (0.0, 0.0, 1.0, 1.0), (0.0, 0.0)))]
        fixed:
            fit_first True
            add At(Solid('#08f', xsize=100, ysize=100, align=(1.0, 0.0)), Transform(rotate=45), Transform(crop=(.0, .5, .5, .5), crop_relative=True))
            text "S":
                # anchor (1.0, 0.0)
                # pos (1908, 4)
                bold True
                anchor (.0, .8)
                pos (.5, .5)

screen houses():
    modal True
    imagebutton:
        idle Solid('#0000')
        action Hide("houses")
    add Solid('#eee', xsize=1820):
        xalign .5
    viewport:
        xmaximum 1820
        # ymaximum .95
        mousewheel True
        draggable True
        align (.5, .5)
        # add Solid("#eee") xalign .5
        vbox:
            xfill True
            for house in ([executive] if executive else [])+houses:
                text house.name xalign .5 color gui.hover_color size 50
                add house.displayable(xalign=.5, ysize=500)
                #TODO lister les partis en présence avec les nombres de sièges

screen stats():
    modal True
    imagebutton:
        idle Solid('#0000')
        action Hide('stats')
    add Solid('#eee', xsize=1820):
        xalign .5
    viewport:
        xmaximum 1820
        mousewheel True
        draggable True
        align (.5, .5)
        default popularopinions = actors.pollopinions(citizenpool)
        vbox:
            xfill True
                text ""
            for k in popularopinions:
                # ajouter un graphe de -opinrange à +opinrange qui montre les éléments de popularopinions[k]
