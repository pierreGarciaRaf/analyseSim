import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyEDO

def f(x, t):
    return x*(1-x)

def solution(t, yo):
    return 1./(1 + (1./yo - 1.)*np.exp(-t))

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
                'type': 'slider',
                'variable': 'dt',
                'description': r'pas de temps $\Delta t$',
                'value': 1.,
                'min': 0.01,
                'max': 2.5,
                'step': 0.01,
            },
            {
                'type': 'dropdown',
                'variable': 'solvers',
                'description': 'Solveurs',
                'options':[solveur._name for solveur in pyEDO.solver_list()],
                'value':'odeint',
            },
        ]
        self.p_sim = {'Tf': 25, 'yo': 1.e-5,}
        self.g = pyWiGL.interactive_graph()
        for d in self.p_model:
            self.g.add_parameter(d)
        self._create_dico_default()
        self._create_dico_solvers()
        self._init_graph()

    def _create_dico_default(self):
        self._dico_default = {}
        for dk in self.p_model:
            self._dico_default[dk['variable']] = dk['value']

    def _create_dico_solvers(self):
        self._dico_solvers = {}
        for EDO_solver in pyEDO.solver_list():
            self._dico_solvers[EDO_solver._name] = EDO_solver

    def _init_graph(self):
        self.fig = self.viewer.Fig(x_range=(0, self.p_sim['Tf']),
                                   y_range=(0, 1.2),
                                   x_label='temps', y_label='population')
        dt = self._dico_default['dt']
        if self.viewer.LaTeX:
            titre = r'Modèle de Verhulst $\Delta t$={0:4.2f}'.format(dt)
        else:
            titre = 'Modèle de Verhulst dt = {0:4.2f}'.format(dt)
        self.fig.title(titre,
                       title_color = 'navy',
                       title_align = 'center')
        self._compute_solution(self._dico_default)
        self.plt = self.fig.line(self.t, self.y[:,0],
                                 line_width = 2,
                                 line_color = self.color,
                                 line_alpha = 0.5,
                                 label = 'numérique')
        tt = np.linspace(0, self.p_sim['Tf'], 1000)
        yy = solution(tt, self.p_sim['yo'])
        self.plt_exacte = self.fig.line(tt, yy,
                                        line_width = 2,
                                        line_color = 'black',
                                        line_alpha = 0.5,
                                        label = 'exacte')
        self.fig.legend(location = "top_left", orientation = 'vertical')
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        self.plt.update(self.t, self.y)
        self.plt.line_color(self.color)
        if self.viewer.LaTeX:
            titre = r'Modèle de Verhulst $\Delta t$={0:4.2f}'.format(args['dt'])
        else:
            titre = 'Modèle de Verhulst dt = {0:4.2f}'.format(args['dt'])
        self.fig.title(titre)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_solution(self, args):
        Tf = self.p_sim['Tf']
        yo = self.p_sim['yo']
        dt = args['dt']
        solver_name = args['solvers']
        self.t = np.arange(0, Tf+dt, dt)
        solver = self._dico_solvers[solver_name](f)
        self.y = solver.integrate(yo, self.t)
        self.color=solver._color
        self.solver = solver._name


def static_plot(dt, solvers, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(dt = dt, solvers = solvers, savefig = savefig)

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()
