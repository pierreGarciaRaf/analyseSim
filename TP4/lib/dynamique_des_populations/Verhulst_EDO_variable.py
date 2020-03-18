import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyEDO

def K(t, Kmin, Kmax, omega):
    return .5*(Kmin+Kmax) + .5*(Kmax-Kmin)*np.cos(omega*t)

def f(x, t, r, Kmin, Kmax, omega):
    Kt = .5*(Kmin+Kmax) + .5*(Kmax-Kmin)*np.cos(omega*t)
    return r*x*(1-x/Kt)

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
                'variable': 'r',
                'description': r'taux de croissance $r$',
                'value': 5,
                'min': 1.,
                'max': 10,
                'step': 0.1,
            },
            {
                'type': 'rangeslider',
                'variable': 'rK',
                'description': r'capacité biotique $K$',
                'value': [1., 1.5],
                'min': 0.1,
                'max': 2.,
                'step': 0.1,
            },
            {
                'type': 'slider',
                'variable': 'omega',
                'description': r'fréquence $\omega$',
                'value': 1.,
                'min': 0.5,
                'max': 2,
            },
            {
                'type': 'dropdown',
                'variable': 'solvers',
                'description': 'Solveurs',
                'options':[solveur._name for solveur in pyEDO.solver_list()],
                'value':'odeint',
            },
        ]
        self.p_sim = {'Tf': 25, 'yo': .1, 'dt': 1.e-2}
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
        k = 0
        while self.p_model[k]['variable'] != 'rK':
            k += 1
        self.fig = self.viewer.Fig(x_range=(0, self.p_sim['Tf']),
                                   y_range=(0, 1.2*self.p_model[k]['max']),
                                   x_label='temps', y_label='population')
        self.fig.title('Modèle de Verhulst',
                       title_color = 'navy',
                       title_align = 'center')
        self._compute_solution(self._dico_default)
        self.plt = self.fig.line(self.t, self.y[:,0],
                                 line_width = 2,
                                 line_color = self.color,
                                 line_alpha = 0.5,
                                 label = 'N(t)')
        self.plt_K = self.fig.line(self.tt, self.yy,
                                 line_width = 2,
                                 line_color = 'black',
                                 line_alpha = 0.5,
                                 label = 'K(t)')
        self.fig.legend(location = "top_center", orientation = 'horizontal')
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        self.plt.update(self.t, self.y)
        self.plt.line_color(self.color)
        self.plt_K.update(self.tt, self.yy)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _compute_solution(self, args):
        Tf = self.p_sim['Tf']
        yo = self.p_sim['yo']
        dt = self.p_sim['dt']
        r = args['r']
        rK = args['rK']
        omega = args['omega']
        solver_name = args['solvers']
        self.t = np.arange(0, Tf+dt, dt)
        solver = self._dico_solvers[solver_name](f, args = (r, rK[0], rK[1], omega))
        self.y = solver.integrate(yo, self.t)
        self.color=solver._color
        self.tt = np.linspace(0, Tf, 1000)
        self.yy = K(self.tt, rK[0], rK[1], omega)


def static_plot(r, rK, omega, solvers, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(r = r, rK = rK, omega = omega, solvers = solvers, savefig = savefig)

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()

"""
# parameters
p_model = [
    {
        'variable': 'r',
        'description': r'taux de croissance $r$',
        'value': 5,
        'min': 1.,
        'max': 10,
        'step': 0.1,
    },
    {
        'type': 'rangeslider',
        'variable': 'rK',
        'description': r'capacité biotique $K$',
        'value': [1., 1.5],
        'min': 0.1,
        'max': 2.,
        'step': 0.1,
    },
    {
        'type': 'slider',
        'variable': 'omega',
        'description': r'fréquence $\omega$',
        'value': 1.,
        'min': 0.5,
        'max': 2,
    },
]

p_sim = {'Tf': 25, 'yo': .1, 'dt': 1.e-2}

def K(t, Kmin, Kmax, omega):
    return .5*(Kmin+Kmax) + .5*(Kmax-Kmin)*np.cos(omega*t)

def f(x, t, r, Kmin, Kmax, omega):
    Kt = .5*(Kmin+Kmax) + .5*(Kmax-Kmin)*np.cos(omega*t)
    return r*x*(1-x/Kt)

def f_plot(r, rK, omega):
    Tf = p_sim['Tf']
    yo = p_sim['yo']
    dt = p_sim['dt']
    fig, ax = plt.subplots(figsize = (6, 4), dpi=100)
    t = np.arange(0, Tf+dt, dt)
    solver = pyEDO.ode_solver_odeint(f, args = (r, rK[0], rK[1], omega))
    y = solver.integrate(yo, t)
    ax.plot(t, y, label = r'$N$', color=solver._color, lw=2, alpha=0.5)
    tt = np.linspace(0, Tf, 1000)
    yy = K(tt, rK[0], rK[1], omega)
    ax.plot(tt, yy, 'k', lw=2, label=r'$K$')
    ax.set_title('Modèle de Verhulst')
    ax.set_xlim(0, p_sim['Tf'])
    k = 0
    while p_model[k]['variable'] != 'rK':
        k += 1
    ax.set_ylim(0, 1.2*p_model[k]['max'])
    ax.legend(loc = 'upper left')
"""
