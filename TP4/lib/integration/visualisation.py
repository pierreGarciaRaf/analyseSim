import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyInterp

def f(x):
    return np.cos(np.pi*x**2)

class graphique():
    def __init__(self, f, xmin, xmax, viewer = 'matplotlib'):
        self.f = f
        self.viewer = viewers.list_viewers.get(viewer, None)
        if self.viewer is None:
            print("Unknown viewer (matplotlib by default)")
            print("The allowed viewers are:")
            for v in viewers.list_viewers.keys():
                print("\t{0}".format(v))
            self.viewer = viewers.list_viewers['matplotlib']
        # parameters
        self.p_model = [
            {
                'type': 'intslider',
                'variable': 'N',
                'description': 'nombre de points',
                'value': 1,
                'min': 0,
                'max': 25,
                'step': 1,
            },
            {
                'type': 'checkbox',
                'variable': 'is_open',
                'description': 'méthode ouverte',
                'value': False,
            },
        ]
        self.p_sim = {'xmin': xmin, 'xmax': xmax, 'NN': 201}
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
        xmin, xmax = self.p_sim['xmin'], self.p_sim['xmax']
        self.xx = np.linspace(xmin, xmax, self.p_sim['NN'])
        yy = self.f(self.xx)
        ymin, ymax = min(yy), max(yy)
        dy = .5*(ymax - ymin)
        ymin -= dy
        ymax += dy
        self.fig = self.viewer.Fig(x_range=(xmin, xmax),
                                   y_range=(ymin, ymax),
                                   width=600,
                                   height=400)
        self.fig.title('Elementary Newton-Cotes methods',
                       title_color = 'navy',
                       title_align = 'center')
        #self.fig.line(self.xx, yy, line_width = 2, line_color = 'black', line_alpha = 0.5)
        #self.fig.line(self.xx, np.zeros(self.xx.shape), line_width = 2, line_color = 'navy', line_alpha = 0.5)
        self._compute_solution(self._dico_default)
        # self.poly = self.fig.line(self.xx, self.yy,
        #                           line_width = 2,
        #                           line_color = 'orange',
        #                           line_alpha = 0.5)
        self.fig.fill(self.xx, yy)
        self.polyf = self.fig.fill(self.xx, self.yy,
                                   line_width = 2,
                                   line_color = 'orange',
                                   fill_color = 'orange',
                                   fill_alpha = 0.5)
        self.points = self.fig.scatter(self.x, self.y, alpha = 1, color = 'navy')
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        # self.poly.update(self.xx, self.yy)
        self.polyf.update(self.xx, self.yy)
        self.points.update(self.x, self.y)
        self.fig.update()

    def _compute_solution(self, args):
        self.N = args['N']
        if not args['is_open']:
            if self.N>0:
                self.x = np.linspace(self.p_sim['xmin'], self.p_sim['xmax'], self.N)
            else:
                self.x = np.array([self.p_sim['xmax']])
        else:
            if self.N == 0:
                self.N += 1
            self.x = np.linspace(self.p_sim['xmin'], self.p_sim['xmax'], self.N+1)
            dx = self.x[1] - self.x[0]
            self.x = self.x[:-1] + .5*dx
        self.y = self.f(self.x)
        P = pyInterp.divided_differences(self.x, self.y)
        self.yy = P.eval(self.xx)


def interactive_plot(myf = f, xmin = 0., xmax = 1., viewer = 'bokeh'):
    graph = graphique(myf, xmin, xmax, viewer)
    graph.g.build(graph.update)
    graph.g.plot()
