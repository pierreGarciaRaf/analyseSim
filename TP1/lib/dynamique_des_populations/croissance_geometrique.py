import numpy as np
from .. import viewers
from .. import pyWiGL

"""

Malthus model

N(t+dt) - N(t) = r dt N(t)

solution : N(n dt) = N(0) (1 + r dt)^n

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
                'type': 'intslider',
                'variable': 'No',
                'description': r'population initiale $N(0)$',
                'value': 1,
                'min': 0,
                'max': 100,
            },
            {
                'variable': 'r',
                'description': r'taux de croissance $r$',
                'value': .07,
                'min': -.1,
                'max': 0.3,
                'step': 0.01,
            },
            {
                'type': 'intslider',
                'variable': 'dt',
                'description': r'pas de temps $\Delta t$',
                'value': 1,
                'min': 0,
                'max': 10,
            },
            {
                'type': 'checkbox',
                'variable': 'is_int',
                'value': False,
                'description': 'Individus indivisibles',
            },
            {
                'type': 'checkbox',
                'variable': 'view_lim',
                'value': False,
                'description': 'Limite visible',
            },
        ]

        self.p_sim = {'Tf': 100, 'Nx': 1000,}
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
        self.fig.title('Modèle de croissance géométrique', title_color = 'navy', title_align = 'center')
        self._compute_suite(self._dico_default)
        self.plt_lim = self.fig.line(self.tlim, self.Nlim,
                                     line_width = 2,
                                     line_color = "orange",
                                     line_alpha = 0.5)
        self.plt_lim.visible(self._dico_default['view_lim'])
        self.plt = self.fig.line(self.t, self.N,
                                 line_width = 2,
                                 line_color = "navy",
                                 line_alpha = 0.5)
        self.fig.plot()

    def update(self, **args):
        self._compute_suite(args)
        self.plt_lim.update(self.tlim, self.Nlim)
        self.plt_lim.visible(args['view_lim'])
        self.plt.update(self.t, self.N)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_suite(self, args):
        No = args['No']
        r = args['r']
        dt = args['dt']
        is_int = args['is_int']
        self.tlim = np.linspace(0, self.p_sim['Tf'], self.p_sim['Nx'])
        self.Nlim = No*np.exp(r*self.tlim)
        if dt > 0:
            nb = int(self.p_sim['Tf']/dt)
            t = np.zeros((2*nb,))
            N = np.zeros(t.shape)
            N[0] = No
            t[1] = dt
            N[1] = No
            if is_int:
                for k in range(1,nb):
                    t[2*k] = t[2*k-1]
                    t[2*k+1] = t[2*k] + dt
                    N[2*k] = int(N[2*k-1] * (1+r*dt))
                    N[2*k+1] = N[2*k]
            else:
                sN = np.arange(nb)
                t[::2] = dt*sN
                t[1::2] = dt*(sN+1)
                N[::2] = No * (1+r*dt)**sN
                N[1::2] = No * (1+r*dt)**sN
            self.t = t
            self.N = N

def static_plot(No, r, dt, view_lim, is_int, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(No = No, r = r, dt = dt, is_int = is_int, view_lim = view_lim, savefig = savefig)

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()
