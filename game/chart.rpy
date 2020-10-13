init python:
    class Chart(renpy.Displayable):
        '''
        values : list[int or float] if style is 'line',
                 list or set[float] if style is 'bars', floats between 0 and 1
                     giving the percentage of the width at which each bar is drawn
        bars_color : None if style is 'line'
                     list[color] if style is 'bars'
                         This decides the style.
                         If a list is given, it defines the color of each bar
        data_border_color : None or the color of the line which connects the values
                                pointless if style is 'bars'
        data_area_color : None or the color of the area underneath the line connecting the values
                              pointless if style is 'bars'
        draw_spokes : bool, whether or not to draw vertical bars at each value
                          pointless if style is 'bars'
        rows_every : None or int, a horizontal line will be drawn every x units to gauge the values
                         pointless if style is 'bars'
        bg : None or color, the color with which to fill the background
        '''
        def __init__(self,
                     values, # liste de nombres
                     labels=None, # liste de displayables ? strings ? ou None
                     bars_colors=None, # liste de couleurs ou None
                     data_border_color='#000', # couleur ou None
                     data_area_color='#08f', # couleur ou None
                     draw_spokes=False, # booléen
                     rows_every=None, # entier ou None
                     bg='#fff', # couleur ou None
                     **kwargs
                     ):
            super(Chart, self).__init__(**kwargs)
            # if labels and len(values) != len(labels):
            #     raise ValueError("The amount of labels does not match the amount of values")
            if bars_colors and len(bars_colors) != len(values):
                raise ValueError("The amount of bar colors does not match the amount of values")
            self.values = values
            self.labels = labels
            self.bars_colors = bars_colors
            self.data_border_color = data_border_color
            self.data_area_color = data_area_color
            self.draw_spokes = draw_spokes
            self.rows_every = rows_every
            self.bg = bg

        def render(self, width, height, st, at):
            width = max(self.style.xminimum, width)
            height = max(self.style.yminimum, height)
            rv = renpy.Render(width, height)
            if self.bg:
                rv.fill(self.bg)
            canvas = rv.canvas()
            if self.bars_colors:
                for k in range(len(self.values)):
                    canvas.line(self.bars_colors[k],
                                (self.values[k]*width/(len(self.values)-1), 0),
                                (self.values[k]*width/(len(self.values)-1), height)
                                )
            else:
                if self.data_area_color:
                    canvas.polygon(self.data_area_color,
                                   zip([1.0*k*width/(len(self.values)-1) for k in range(len(self.values))], [(1-1.0*val/max(self.values))*height for val in self.values])+[[width, height], [0, height]]
                                   )
                if self.data_border_color:
                    canvas.aalines(self.data_border_color,
                                  False,
                                  zip([1.0*k*width/(len(self.values)-1) for k in range(len(self.values))], [(1-1.0*val/max(self.values))*height for val in self.values])
                                  )
                    print(zip([1.0*k*width/(len(self.values)-1) for k in range(len(self.values))], [(1-1.0*val/max(self.values))*height for val in self.values]))
                if self.rows_every:
                    pass
                if self.draw_spokes:
                    for k in range(1, len(self.values)):
                        canvas.line('#000',
                                    (k*width/(len(self.values)-1), 0),
                                    (k*width/(len(self.values)-1), height)
                                    )
            return rv
