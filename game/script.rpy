# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
define boldChar = Character(who_bold=True)
define gvt = Character("GOUVERNEMENT", boldChar, who_font='marianne-regular-webfont.otf')

define maxnhouses = 2 # adapter aussi la création de constitution
default houses = []
default executive = None
default popscale = 10000
default citizenpool = []
default citikey = None
default electrobj = renpy.random.Random(None)
default partis = []

define audio.anthems = ["/music/china-national-anthem-instrumental.mp3",
"/music/canada-national-anthem-instrumental.mp3",
"/music/finland-national-anthem-instrumental.mp3",
"/music/Jesse_Stiles_L'internationale.mp3",
"/music/new-zealand-national-anthem-instrumental.mp3",
"/music/north-korea-national-anthem-instrumental.mp3",
"/music/russia-national-anthem-instrumental.mp3",
"/music/united-kingdom-national-anthem-instrumental.mp3",
"/music/united-states-of-america-national-anthem-instrumental.mp3",
"/music/france-national-anthem-la-marseillaise-instrumental.mp3"]
init python:
    if config.developer:
        audio.anthems.pop()


# The game starts here.

label start:
    scene expression '#fff'

    # These display lines of dialogue.

    e "You've created a new Ren'Py game."

    menu:
        "Pick a country template":
            call country_templates
        "Draft your own {b}Constitution{/b}":
            call constitution_form

    if not partis:
        $ renpy.notify(_("Generating random political parties..."))
        $ partis = actors.Party.generate(10)

    show screen displayer
    e "hey"
    pause

    show sand6
    pause
    show bashar
    pause

    e "Once you add a story, pictures, and music, you can release it to the world!"

    gvt "lol non"

    pause
    # gouvernement à droite, opposition à gauche
    $ seats = 1
    label printer:
        show expression newarch([(seats, '#f00', 'left'), (23, '#090', 'center'), (24, '#009', 'right')]) as parli at truecenter
        pause
        show expression Westminster([(1, '#000', 'head'), (seats, '#f00', 'left'), (23, '#090', 'center'), (24, '#009', 'right')]) as parli at truecenter
        pause
        $ seats += 1
        jump printer

    # This ends the game.

    return

label country_templates:
    $ renpy.dynamic("ncitizen")

    $ ncitizens = int(renpy.input(_("Please enter the number of simulated citizens per minimal electoral district :\n"
                                    "(big numbers will multiply memory usage and lag, importance differs depending on the country)"),
                                  default="10",
                                  allow="0123456789") or "1") or 1
    $ houses[:], executive, partis = renpy.display_menu(templates.templates.items())(ncitizens=ncitizens)

    return
