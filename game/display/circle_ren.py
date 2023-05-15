import renpy

"""renpy
init python:
"""
class Circle(renpy.Displayable):
    def __init__(self, colour, border=0, **kwargs):
        super(Circle, self).__init__(**kwargs)
        self.colour = colour
        self.border = border

    def render(self, width, height, st, at):
        size = min(width, height)
        render = renpy.Render(size, size)
        # render.fill('#0f0') # debug, pour voir les limites du render
        canvas = render.canvas()
        # return render
        canvas.circle(self.colour, # the color
                        (size/2, size/2), # the centre
                        size/2, # the radius
                        width=self.border, # width - 0 is filled, else linewidth of drawn circle
                        )
        return render
