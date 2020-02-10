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
                'variable': 'a',
                'description': r'coefficient $\tau_L$',
                'value': 2.,
                'min': -10.,
                'max': 5.,
                'step': 0.5,
            },
            {
                'variable': 'dt',
                'description': r'pas de temps $\Delta t$',
                'value': .25,
                'min': 0.0001,
                'max': 0.5,
            },
        ]

        self.p_sim = {'Tf': 1,}
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
        while self.p_model[k]['variable'] != 'a':
            k += 1
        self.fig = self.viewer.Fig(x_range=(0, self.p_sim['Tf']),
                                   y_range=(-4, 20),
                                   x_label='temps', y_label='y(t)')
        self.fig.title("Résolution approchée de $y'=ay$",
                       title_color = 'navy',
                       title_align = 'center')
        self.t0 = np.linspace(0, self.p_sim['Tf'])
        self._compute_solution(self._dico_default)
        self.plt1 = self.fig.line(self.t0, self.exact,
                                 line_width = 2,
                                 line_color = 'black',
                                 line_alpha = 0.5,
                                 label="solution exacte")
        self.plt2 = self.fig.line(self.t, self.approx,
                                 line_width = 2,
                                 line_color = self.color,
                                 line_alpha = 0.5,
                                 label="schéma d'Euler")
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        self.plt1.update(self.t0, self.exact)
        self.plt2.update(self.t, self.approx)
        self.plt2.line_color(self.color)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_solution(self, args):
        No = 1
        a = args['a']
        dt = args['dt']
        self.t = np.arange(0, self.p_sim['Tf']+dt, dt)
        self.exact = No*np.exp(a*self.t0)
        if a*dt>0.1:
            self.color = 'navy'
        elif a*dt<-1:
            self.color = 'orange'
        else:
            self.color = 'black'
        self.approx = np.empty(self.t.shape)
        self.approx[0] = 1
        for i in range(1,self.t.size):
            self.approx[i] = (1+a*dt)*self.approx[i-1]
            

def static_plot(No, b, e, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(a = a, dt = dt, savefig = savefig)

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()
