import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyInterp

class graphique():
    """
    plot \sum \abs L_i(x)
    where L_i is the interpolator polynomial associated to the canonical basis of R^N

    We compare the points of Interpolation
    * uniformly distributed in [-1,1]
    * the zeros of the Tchebychev polynomials
    """
    def __init__(self, viewer = 'matplotlib'):
        self.viewer = viewers.list_viewers.get(viewer, None)
        if self.viewer is None:
            print("Unknown viewer (matplotlib by default)")
            print("The allowed viewers are:")
            for v in viewers.list_viewers.keys():
                print("\t{0}".format(v))
            self.viewer = viewers.list_viewers['matplotlib']
        self.method = pyInterp.divided_differences
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
            {
                'type': 'checkbox',
                'variable': 'is_uni',
                'description': 'points uniformément répartis',
                'value': True,
            },
            {
                'type': 'checkbox',
                'variable': 'is_Tche',
                'description': 'points de Tchebychev',
                'value': False,
            },
        ]
        self.p_sim = {
            'xmin': -1.,
            'xmax': 1.,
            'ymin': -1,
            'ymax': 11,
            'NN': 2001,
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
        xmin, xmax = self.p_sim['xmin'], self.p_sim['xmax']
        ymin, ymax = self.p_sim['ymin'], self.p_sim['ymax']
        self.xx = np.linspace(xmin, xmax, self.p_sim['NN'])
        self.L_uni = np.zeros(self.xx.shape)
        self.L_tch = np.zeros(self.xx.shape)
        self.fig = self.viewer.Fig(x_range=(xmin, xmax),
                                   y_range=(ymin, ymax),
                                   width=600, height=400)
        if self.viewer.LaTeX:
            title = r'$\Psi(x)$'
        else:
            title = 'Psi(x)'
        self.fig.title(title,
                       title_color = 'navy',
                       title_align = 'center')
        self._compute_solution(self._dico_default)
        self.points_uni = self.fig.scatter(self.x_uni, np.zeros((self.N,)), color = 'orange')
        self.points_uni.visible(self._dico_default['is_uni'])
        self.points_tch = self.fig.scatter(self.x_tch, np.zeros((self.N,)), color = 'navy')
        self.points_tch.visible(self._dico_default['is_Tche'])
        self.plot_uni = self.fig.line(self.xx, self.L_uni,
                                      line_width = 2,
                                      line_color = 'orange',
                                      line_alpha = 0.5,
                                      label = 'uniforme')
        self.plot_uni.visible(self._dico_default['is_uni'])
        self.plot_tch = self.fig.line(self.xx, self.L_tch,
                                      line_width = 2,
                                      line_color = 'navy',
                                      line_alpha = 0.5,
                                      label = 'Tchebychev')
        self.plot_tch.visible(self._dico_default['is_Tche'])
        self.fig.legend(location = "top center", orientation = 'vertical', click_policy = "hide")
        self.fig.plot()

    def _compute_solution(self, args):
        self.N = args['N']
        self.x_uni = np.linspace(self.p_sim['xmin'], self.p_sim['xmax'], self.N)
        self.x_tch = 0.5 * (self.p_sim['xmax']+self.p_sim['xmin']) + 0.5 * (self.p_sim['xmax']-self.p_sim['xmin']) * np.cos((2*np.arange(self.N)+1)/(2*self.N)*np.pi)
        self._compute_Lebesgue(self.x_uni, self.xx, self.L_uni)
        self._compute_Lebesgue(self.x_tch, self.xx, self.L_tch)

    def _compute_Lebesgue(self, x, xx, yy):
        yy[:] = 0.
        y = np.zeros(x.size)
        for i in range(x.size):
            y[:] = 0.
            y[i] = 1.
            P = self.method(x, y)
            yy += np.absolute(P.eval(xx))

    def update(self, **args):
        self._compute_solution(args)
        self.points_uni.update(self.x_uni, np.zeros((self.N,)))
        self.points_uni.visible(args['is_uni'])
        self.points_tch.update(self.x_tch, np.zeros((self.N,)))
        self.points_tch.visible(args['is_Tche'])
        self.plot_uni.update(self.xx, self.L_uni)
        self.plot_uni.visible(args['is_uni'])
        self.plot_tch.update(self.xx, self.L_tch)
        self.plot_tch.visible(args['is_Tche'])
        self.fig.update()

def interactive_plot(viewer = 'bokeh'):
    graph = graphique(viewer)
    graph.g.build(graph.update)
    graph.g.plot()

def Lebesgue_constant(viewer = 'bokeh'):
    viewer = viewers.list_viewers.get(viewer, None)
    if viewer is None:
        print("Unknown viewer (matplotlib by default)")
        print("The allowed viewers are:")
        for v in viewers.list_viewers.keys():
            print("\t{0}".format(v))
        viewer = viewers.list_viewers['matplotlib']
    method = pyInterp.divided_differences

    N = np.arange(2, 46)
    A = np.zeros(N.shape)
    B = np.zeros(N.shape)
    xx = np.linspace(-1, 1, 1001)
    yy = np.zeros(xx.shape)

    def cpte_L(x, xx, yy):
        yy[:] = 0.
        y = np.zeros(x.size)
        for i in range(x.size):
            y[:] = 0.
            y[i] = 1.
            P = method(x, y)
            yy += np.absolute(P.eval(xx))
        return np.max(yy)

    for i, n in enumerate(N):
        x = np.linspace(-1, 1, n)
        A[i] = cpte_L(x, xx, yy)
        x = np.cos((2*np.arange(n)+1)/(2*n)*np.pi)
        B[i] = cpte_L(x, xx, yy)

    fig = viewer.Fig(x_range=(1, np.max(N)),
                     width=600, height=400, y_axis_type = 'log')
    fig.title('Lebesgue constant', title_color = 'navy', title_align = 'center')
    fig.line(N, A,
             line_color = 'orange',
             line_width = 1,
             line_marker = 'square',
             label = 'uniforme')
    fig.line(N, B,
          line_color = 'navy',
          line_width = 1,
          line_marker = 'circle',
          label = 'Tchebychev')
    fig.legend(location = "top left", click_policy = "hide")
    fig.plot()
