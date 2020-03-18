import numpy as np
from .. import viewers
from .. import pyWiGL

"""

Erreur numérique, pour différents schémas, sur le modèle de Malthus :

N'(t) = (b - e) N(t)

solution : N(t) = N(0) e^((b-e)t)

"""

class graphique():
    def __init__(self, viewer = 'matplotlib',nb_schema=1):
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
                'value': .1,
                'min': -1.,
                'max': 10.,
                'step': .1,
            },
        ]

        self.p_sim = {'Tf': 1,}
        self.g = pyWiGL.interactive_graph()
        for d in self.p_model:
            self.g.add_parameter(d)
        self._create_dico_default()
        self._init_graph(nb_schema)

    def _create_dico_default(self):
        self._dico_default = {}
        for dk in self.p_model:
            self._dico_default[dk['variable']] = dk['value']

    def _init_graph(self,nb_schema=1):
        k = 0
        while self.p_model[k]['variable'] != 'a':
            k += 1
        self.nb_schema=nb_schema
        self.dt = np.arange(7)
        self.dt = 10.**(-self.dt)
        self.fig = self.viewer.Fig(x_label='pas de temps', y_label='erreur',
                                   x_axis_type="log",y_axis_type="log",
                                   x_range=(self.dt[-1],self.dt[0]))
        self.fig.title("Convergence de la méthode",
                       title_color = 'navy',
                       title_align = 'center')
        self._get_error(self._dico_default)
        self.plt1 = self.fig.line(self.dt, self.error,
                                 line_width = 2,
                                 line_color = 'red',
                                 line_alpha = 0.5,
                                 label="erreur (EE)")
        self.plt2 = self.fig.line(self.dt, self.error/self.max,
                                 line_width = 2,
                                 line_color = 'green',
                                 line_alpha = 0.5,
                                 label="erreur relative (EE)")
        if (self.nb_schema==2) :
            self.plt3 = self.fig.line(self.dt, self.error2,
                                 line_width = 2,
                                 line_color = 'blue',
                                 line_alpha = 0.5,
                                 label="erreur (PM)")
            self.plt4 = self.fig.line(self.dt, self.error2/self.max,
                                 line_width = 2,
                                 line_color = 'black',
                                 line_alpha = 0.5,
                                 label="erreur relative (PM)")
        self.fig.plot()

    def update(self, **args):
        self._get_error(args)
        self.plt1.update(self.dt, self.error)
        self.plt2.update(self.dt, self.error/self.max)
        if (self.nb_schema==2) :
            self.plt3.update(self.dt, self.error2)
            self.plt4.update(self.dt, self.error2/self.max)
        self.fig.update()
        if 'savefig' in args:
            self.fig.savefig(args['savefig'])

    def _get_error(self, args):
        a = args['a']
        self.max=np.exp(a)
        self.error = get_error(a,self.dt)  
        if (self.nb_schema==2) :
            self.error2 = get_error(a,self.dt,schema=approx_milieu)

def static_plot(No, b, e, savefig = None, viewer = 'matplotlib'):
    graph = graphique(viewer = viewer)
    graph.update(a = a, dt = dt, savefig = savefig)

def interactive_plot(viewer = 'bokeh',nb_schema=1):
    graph = graphique(viewer,nb_schema)
    graph.g.build(graph.update)
    graph.g.plot()


def approx_EE(a,h):
    ''' Approximation en t=1 par le schéma d'Euler explicite '''
    N = int(1//h)
    res = (1+a*h)**N
    # res = res + h*a*res = res(1+a*h)
    return (res+a*(1-N*h)*res)

def approx_milieu(a,h):
    ''' Approximation en t=1 par le schéma du point du milieu '''
    N = int(1//h)
    # tmp = res*(1+0.5*h*a)
    # res += h*a*tmp   
    # res += h*a*res*(1+h2*a)
    # res = res + h*a*res*(1+0.5*h*a)
    # res = res*(1+h*a*(1+a*0.5*h))
    res =(1+h*a*(1+a*0.5*h))**N
    hb = 1-N*h
    res *=(1+hb*a*(1+a*0.5*hb))
    return res

def get_error(a,dt,schema=approx_EE):
    tmp0 = np.exp(a)
    return np.abs(tmp0 - np.array([schema(a,h) for h in dt]))

#xs = bp.LinearScale()
#ys = bp.LinearScale()

#xs = bp.LogScale()
#ys = bp.LogScale()

#dt = np.arange(10)
#dt = 10.**(-dt)
#a=0.1
#y = get_error(a,dt)

#xax = bp.Axis(scale=xs,tick_format='2.0e', label='pas de temps', grid_lines='solid')
#yax = bp.Axis(scale=ys,tick_format='2.0e', orientation='vertical', label='erreur', grid_lines='solid')

#line = bp.Lines(x=dt, y=y, scales={'x': xs, 'y': ys}, colors=['red','green'], labels=['erreur (EE)','erreur relative (EE)'],display_legend=True)
#bp.Figure(marks=[line], axes=[xax, yax], animation_duration=1000)

#y2 = get_error(a,dt,schema=approx_milieu)
#line2 = bp.Lines(x=dt, y=y2, scales={'x': xs, 'y': ys}, colors=['blue','black'], labels=['erreur (PM)','erreur relative (PM)'],display_legend=True)