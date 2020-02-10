import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyInterp

def f(x):
    return np.sin(2*np.pi*x) / (1.1 - np.sin(np.pi*x))

class graphique():
    def __init__(self, f, xmin, xmax, viewer = 'matplotlib'):
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
                'value': 5,
                'min': 1,
                'max': 20,
                'step': 1,
            },
        ]
        for method in pyInterp.interp_list():
            self.p_model.append({
                'type': 'checkbox',
                'variable': 'is_' + method._name,
                'description': method._name,
                'value': False,
            })
        self.p_sim = {'xmin': xmin, 'xmax': xmax, 'NN': 201}
        self.g = pyWiGL.interactive_graph()
        for d in self.p_model:
            self.g.add_parameter(d)
        self._create_dico_default()
        #self._create_dico_solvers()
        self._init_graph()

    def _create_dico_default(self):
        self._dico_default = {}
        for dk in self.p_model:
            self._dico_default[dk['variable']] = dk['value']

    def _init_graph(self):
        xmin, xmax = self.p_sim['xmin'], self.p_sim['xmax']
        self.xx = np.linspace(xmin, xmax, self.p_sim['NN'])
        yy = f(self.xx)
        ymin, ymax = min(yy), max(yy)
        dy = .5*(ymax - ymin)
        ymin -= dy
        ymax += dy
        self.fig = self.viewer.Fig(x_range=(xmin, xmax),
                                   y_range=(ymin, ymax),
                                   width=600,
                                   height=400)
        self.fig.title('Interpolation methods',
                       title_color = 'navy',
                       title_align = 'center')
        self.fig.line(self.xx, yy, line_width = 2, line_color = 'black', line_alpha = 0.5)
        self._compute_solution(self._dico_default)
        self.list_plot = {}
        for method in pyInterp.interp_list():
            nom = method._name
            self.list_plot[nom] = self.fig.line(self.xx, self.list_interp[nom],
                                                line_width = 2,
                                                line_color = method._color,
                                                line_alpha = 0.5,
                                                label = nom)
        self.points = self.fig.scatter(self.x, self.y)
        self.fig.legend(location = "bottom center", orientation = 'vertical', click_policy = "hide")
        for method in pyInterp.interp_list():
            nom = method._name
            self.list_plot[nom].visible(self._dico_default['is_' + nom])
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        for method in pyInterp.interp_list():
            nom = method._name
            self.list_plot[nom].update(self.xx, self.list_interp[nom])
            self.list_plot[nom].visible(args['is_' + nom])
        self.points.update(self.x, self.y)
        self.fig.update()

    def _compute_solution(self, args):
        self.N = args['N']
        self.x = np.linspace(self.p_sim['xmin'], self.p_sim['xmax'], self.N)
        self.y = f(self.x)
        self.list_interp = {}
        for method in pyInterp.interp_list():
            P = method(self.x, self.y)
            self.list_interp[method._name] = P.eval(self.xx)


def interactive_plot(myf = f, xmin = 1., xmax = 3., viewer = 'bokeh'):
    graph = graphique(myf, xmin, xmax, viewer)
    graph.g.build(graph.update)
    graph.g.plot()
