import numpy as np
import numpy.random as rd
import scipy.interpolate as interp
from .. import viewers
from .. import pyWiGL
import warnings

warnings.simplefilter('ignore', np.RankWarning)

def f(x, a = None):
    y = 4*x*(1-x)
    if a is not None:
        y += a * rd.randn(*x.shape)
    return y

class graphique():
    def __init__(self, viewer = 'matplotlib'):
        self.viewer = viewers.list_viewers.get(viewer, None)
        if self.viewer is None:
            print("Unknown viewer (matplotlib by default)")
            print("The allowed viewers are:")
            for v in viewers.list_viewers.keys():
                print("\t{0}".format(v))
            self.viewer = viewers.list_viewers['matplotlib']
        self.p_model = [
            {
                'type': 'intslider',
                'variable': 'N',
                'description': 'nombre de points',
                'value': 5,
                'min': 2,
                'max': 25,
                'step': 1,
            },
            {
                'variable': 'a',
                'description': 'amplitude du bruit',
                'value': 0.,
                'min': 0.,
                'max': 0.25,
                'step': 0.01,
            },
            {
                'type': 'intslider',
                'variable': 'n',
                'description': "degré de l'approximation",
                'value': 2,
                'min': 1,
                'max': 10,
            },
        ]

        self.p_sim = {
            'Nx': 1000,
            'bornes': (0, 1, -.25, 1.25),
        }

        self.g = pyWiGL.interactive_graph()
        for d in self.p_model:
            self.g.add_parameter(d)
        self._create_dico_default()
        self._init_graph()

    def _create_dico_default(self):
        self._dico_default = {}
        for dk in self.p_model:
            self._dico_default[dk['variable']] = dk['value']

    def _init_graph(self):
        self.xmin, self.xmax, self.ymin, self.ymax = self.p_sim['bornes']
        self.xx = np.linspace(self.xmin, self.xmax, self.p_sim['Nx'])
        self._compute_courbes(self._dico_default)
        self.fig = self.viewer.Fig(x_range=(self.xmin, self.xmax),
                                   y_range=(self.ymin, self.ymax))
        self.fig.title('Interpolation ou approximation',
                       title_color = 'navy',
                       title_align = 'center')
        self.points = self.fig.scatter(self.x, self.y, color = 'navy', label = 'points', alpha = 0.5)
        self.interp = self.fig.line(self.xx, self.yi, line_color = 'orange', line_alpha = 0.5, label = 'interpolation', line_width = 2)
        self.approx = self.fig.line(self.xx, self.ya, line_color = 'green', line_alpha = 0.5, label = 'approximation', line_width = 2)
        self.fig.legend(location = "lower center")
        self.fig.plot()

    def update(self, **args):
        self._compute_courbes(args)
        self.points.update(self.x, self.y)
        self.interp.update(self.xx, self.yi)
        self.approx.update(self.xx, self.ya)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_courbes(self, args):
        N = args['N']
        a = args['a']
        n = args['n']
        self.x = np.linspace(self.xmin, self.xmax, N)
        self.y = f(self.x, a = a)
        #pi = np.poly1d(np.polyfit(self.x, self.y, self.x.size)) # interpolation
        pi = interp.lagrange(self.x, self.y)                    # interpolation
        pa = np.poly1d(np.polyfit(self.x, self.y, n))           # approximation
        self.yi = pi(self.xx)
        self.ya = pa(self.xx)


def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()
