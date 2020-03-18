# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
define boldChar = Character(who_prefix='{b}', who_suffix='{/b}')
define gvt = Character("GOUVERNEMENT", boldChar)


# The game starts here.

label start:
    call after_load
    scene expression '#fff'

    # These display lines of dialogue.

    e "You've created a new Ren'Py game."

    e "Once you add a story, pictures, and music, you can release it to the world!"

    gvt "lol non"

    pause
    # gouvernement à droite, opposition à gauche
    $ seats = 1
    label printer:
        show expression newarch([(seats, '#f00', 'left'), (23, '#090', 'center'), (24, '#009', 'right')]) as parli at Transform(align=(.5, .5))
        pause
        # show expression Solid('#c60', xsize=.25) as solido behind parli
        show expression Westminster([(1, '#000', 'head'), (seats, '#f00', 'left'), (23, '#090', 'center'), (24, '#009', 'right')]) as parli at Transform(align=(.5, .5))
        pause
        $ seats += 1
        jump printer

    # This ends the game.

    return

label after_load:
    python:
        totals = []
        for rows in range(1, maxrows):
            tot = 0
            rad = 1/float(4*rows-2)
            for r in range(1, rows+1):
                R = .5 + 2*(r-1)*rad
                tot += int(math.pi*R/(2*rad))
            totals.append(tot)
        # totals[i] : nombre max de sièges quand on a i+1 rangs
