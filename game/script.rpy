# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
define gvt = Character("GOUVERNEMENT", who_prefix='{b}', who_suffix='{/b}')


# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg room

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    show eileen happy

    # These display lines of dialogue.

    e "You've created a new Ren'Py game."

    e "Once you add a story, pictures, and music, you can release it to the world!"

    pause
    $ seats = 1
    label printer:
        show expression newarch([(seats, '#f00'), (24, '#009')]) as parli at Transform(align=(.5, .0))
        pause
        # show expression Solid('#c60', xsize=.25) as solido behind parli
        show expression Westminster([(seats, 'left', '#f00'), (24, 'right', '#009'), (1, 'head', '#000')]) as parli at Transform(align=(.5, .5))
        pause
        $ seats += 1
        jump printer

    # This ends the game.

    return
