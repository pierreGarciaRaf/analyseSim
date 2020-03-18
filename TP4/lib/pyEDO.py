import copy
import numpy as np
from scipy.integrate import odeint

def solver_list():
    return ode_solver.__subclasses__()

color = {
    'blue': (0.06, 0.62, 0.91),
    'green': (0.01, 0.84, 0.35),
    'pink': (1., 0., 0.5),
    'red': (0.97, 0.14, 0.05),
}

class ode_solver():
    _name = "generic ode solver"
    _color = (0., 0., 0.)
    def __init__(self, f, args = ()):
        self.f = f
        self.args = args
    def __str__(self):
        return self._name
    def integrate(self, yo, t):
        yo = np.array(yo)
        self.shape_yo = yo.shape
        self.y = np.zeros((t.size, *self.shape_yo))
        self.y[0] = copy.copy(yo)
        for k in range(len(t)-1):
            self.y[k+1] = self._onetimestep(self.y[k], t[k], t[k+1]-t[k])
        return self.y

class ode_solver_Euler(ode_solver):
    _name = "Euler"
    _color = color['blue']
    def _onetimestep(self, yo, t, dt):
        return yo + dt * self.f(yo, t, *self.args)

class ode_solver_Heun(ode_solver):
    _name = "Heun"
    _color = color['green']
    def _onetimestep(self, yo, t, dt):
        p0 = self.f(yo, t, *self.args)
        y1 = yo + dt * p0
        p1 = self.f(y1, t + dt, *self.args)
        return yo + .5 * dt * (p0 + p1)

class ode_solver_MiddlePoint(ode_solver):
    _name = "point milieu"
    _color = color['green']
    def _onetimestep(self, yo, t, dt):
        p0 = self.f(yo, t, *self.args)
        y1 = yo + 0.5 * dt * p0
        p1 = self.f(y1, t + 0.5*dt, *self.args)
        return yo + dt * p1

class ode_solver_RK4(ode_solver):
    _name = "RK4"
    _color = color['pink']
    def _onetimestep(self, yo, t, dt):
        p0 = self.f(yo, t, *self.args)
        y1 = yo + .5 * dt * p0
        p1 = self.f(y1, t + .5 * dt, *self.args)
        y2 = yo + 0.5 * dt * p1
        p2 = self.f(y2, t + .5 * dt, *self.args)
        y3 = yo + dt * p2
        p3 = self.f(y3, t + dt, *self.args)
        return yo + dt * (p0 + 2*p1 + 2*p2 + p3)/6

class ode_solver_odeint(ode_solver):
    _name = "odeint"
    _color = color['red']
    def integrate(self, yo, t):
        return odeint(self.f, np.array(yo), t, args = self.args)
