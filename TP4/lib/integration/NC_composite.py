import numpy as np
from .. import viewers
from .. import pyWiGL
from .. import pyQuad

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
                'description': 'nombre de subdivisions',
                'value': 2,
                'min': 2,
                'max': 20,
                'step': 1,
            },
        ]
        for method in pyQuad.quad_list():
            self.p_model.append({
                'type': 'checkbox',
                'variable': 'is_' + method._name,
                'description': method._name,
                'value': False,
            })
        self.p_sim = {'xmin': xmin, 'xmax': xmax, 'NN': 11}
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
        N = self._dico_default['N']
        xx = np.linspace(xmin,xmax,401)
        yy = self.f(xx)
        ymin, ymax = np.min(yy), np.max(yy)
        dy = .5*(ymax - ymin)
        ymin -= dy
        ymax += dy
        self.fig = self.viewer.Fig(x_range=(xmin, xmax),
                                   y_range=(ymin, ymax),
                                   width=600,
                                   height=400)
        self.fig.title('Composite Newton-Cotes methods',
                       title_color = 'navy',
                       title_align = 'center')
        self._compute_solution(self._dico_default)

        self.fig.fill(xx, yy)
        self.list_plot = {}
        for method in pyQuad.quad_list():
            nom = method._name
            self.list_plot[nom] = self.fig.fill(self.xx, self.list_quad[nom],
                                                line_width = 3,
                                                line_color =  method._color,
                                                fill_color =  method._color,
                                                fill_alpha = 0.5)
        for method in pyQuad.quad_list():
            nom = method._name
            self.list_plot[nom].visible(self._dico_default['is_' + nom])
        self.fig.plot()

    def update(self, **args):
        self._compute_solution(args)
        for method in pyQuad.quad_list():
            nom = method._name
            self.list_plot[nom].update(self.xx, self.list_quad[nom])
            self.list_plot[nom].visible(args['is_' + nom])
        self.fig.update()

    def _compute_solution(self, args):
        self.N = args['N']
        xmin, xmax = self.p_sim['xmin'], self.p_sim['xmax']
        #h = (xmax-xmin)/self.N
        #x = np.arange(xmin,xmax+h,h)
        x = np.linspace(xmin, xmax, self.N+1)
        h = x[1] - x[0]
        self.list_quad = {}
        for method in pyQuad.quad_list():
            Q = method(x)
            polylist = Q.approx(self.f)
            txx, tyy = [], []
            for i, u in enumerate(x[:-1]):
                txx.append(np.linspace(u, u+h, self.p_sim['NN']))
                tyy.append(polylist[i](txx[-1]))
            self.xx = np.hstack(txx)
            self.list_quad[method._name] = np.hstack(tyy)


def interactive_plot(myf = f, xmin = 0., xmax = 1., viewer = 'bokeh'):
    graph = graphique(myf, xmin, xmax, viewer)
    graph.g.build(graph.update)
    graph.g.plot()
