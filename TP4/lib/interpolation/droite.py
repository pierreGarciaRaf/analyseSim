import numpy as np
from .. import viewers
from .. import pyWiGL

class graphique():
    def __init__(self, myf, xmin, xmax, vmin, vmax, viewer = 'matplotlib'):
        self.viewer = viewers.list_viewers.get(viewer, None)
        if self.viewer is None:
            print("Unknown viewer (matplotlib by default)")
            print("The allowed viewers are:")
            for v in viewers.list_viewers.keys():
                print("\t{0}".format(v))
            self.viewer = viewers.list_viewers['matplotlib']
        self.myf = myf
        self.xmin, self.xmax = xmin, xmax
        self.xa, self.xb = vmin, vmax
        self.ya, self.yb = self.myf(self.xa), self.myf(self.xb)
        self.p_model = [
            {
                'type': 'rangeslider',
                'variable': 'ptsInterp',
                'description': "Points d'interpolation",
                'value': (self.xa, self.xb),
                'min': self.xmin,
                'max': self.xmax,
                'step': 0.01,
                'readout_format': '.2f',
            }
        ]
        self.g = pyWiGL.interactive_graph()
        for d in self.p_model:
            self.g.add_parameter(d)
        self._init_graph(vmin, vmax)

    def _init_graph(self, vmin, vmax):
        self.x = np.linspace(self.xmin, self.xmax, 200)
        fy = self.myf(self.x)
        ym, yM = min(fy), max(fy)
        ymin, ymax = ym - 0.25*(yM-ym), yM + 0.25*(yM-ym)
        self.color_default = "navy"
        self._compute_droite()
        self.fig = self.viewer.Fig(x_range = (self.xmin, self.xmax),
                                   y_range = (ymin, ymax))
        self.fig.title('Interpolation à deux points',
                       title_color = self.color_default,
                       title_align = 'center')
        self.fig.line(self.x, fy, line_width = 2, line_color = 'black',
                      line_alpha = 0.5)
        self.points = self.fig.scatter(np.array([self.xa, self.xb]),
                                   np.array([self.ya, self.yb]),
                                   color = self.color, alpha = 0.5)
        self.droite = self.fig.line(self.x, self.dy,
                               line_color = self.color,
                               line_width = 2,
                               line_alpha = .5)
        self.fig.plot()

    def _compute_droite(self):
        xa, xb = self.xa, self.xb
        ya, yb = self.ya, self.yb
        if xb == xa:
            df = (self.myf(xa+1.e-10) - self.myf(xa)) * 1.e10
            self.dy = (self.x-xa) * df + ya
            self.color = 'orange'
        else:
            self.dy = ( (self.x-xa)*yb - (self.x-xb)*ya ) / (xb-xa)
            self.color = self.color_default

    def update(self, **args):
        self.xa, self.xb = args['ptsInterp']
        self.ya, self.yb = self.myf(self.xa), self.myf(self.xb)
        self._compute_droite()
        self.droite.update(self.x, self.dy)
        self.points.update(np.array([self.xa, self.xb]),
                           np.array([self.ya, self.yb]))
        self.droite.line_color(self.color)
        self.points.fill_color(self.color)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

def interactive_plot(myf, xmin = 0., xmax = 1., viewer = 'bokeh'):
    vmin, vmax = 0.667*xmin + 0.333*xmax, 0.333*xmin + 0.667*xmax
    graph = graphique(myf, xmin, xmax, vmin, vmax, viewer = viewer)
    graph.g.build(graph.update)
    graph.g.plot()
