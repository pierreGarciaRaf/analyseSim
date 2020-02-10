import numpy as np
from .. import viewers
from .. import pyWiGL

"""

Malthus model

N'(t) = (b - e) N(t)

solution : N(t) = N(0) e^((b-e)t)

"""

class graphique():
    def __init__(self, viewer = 'matplotlib'):
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
                'variable': 'No',
                'description': r'population initiale $N(0)$',
                'value': .1,
                'min': 0.,
                'max': 2.,
            },
            {
                'variable': 'b',
                'description': r'taux de naissance $\lambda$',
                'value': 2.,
                'min': 0.,
                'max': 2.,
                'step': 0.1,
            },
            {
                'variable': 'e',
                'description': r'taux de mort $\mu$',
                'value': .25,
                'min': 0.,
                'max': 2,
                'step': 0.1,
            },
        ]

        self.p_sim = {'Tf': 2, 'Nx': 100,}
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
        k = 0
        while self.p_model[k]['variable'] != 'No':
            k += 1
        self.fig = self.viewer.Fig(x_range=(0, self.p_sim['Tf']),
                                   y_range=(0, 2*self.p_model[k]['max']),
                                   x_label='temps', y_label='population')
        self.fig.title('Modèle de Malthus',
                       title_color = 'navy',
                       title_align = 'center')
        self._compute_solution(self._dico_default)
        self.plt = self.fig.line(self.t, self.N,
                                 line_width = 2,
                                 line_color = self.color,
                                 line_alpha = 0.5)
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        self.plt.update(self.t, self.N)
        self.plt.line_color(self.color)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_solution(self, args):
        No = args['No']
        b = args['b']
        e = args['e']
        self.t = np.linspace(0, self.p_sim['Tf'], self.p_sim['Nx'])
        self.N = No*np.exp((b-e)*self.t)
        if b>e:
            self.color = 'navy'
        elif b<e:
            self.color = 'orange'
        else:
            self.color = 'black'

def static_plot(No, b, e, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(No = No, b = b, e = e, savefig = savefig)

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()
