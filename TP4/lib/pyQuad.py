import numpy as np
from scipy.interpolate import lagrange

def quad(method, f, a, b, N):
    x = np.linspace(a, b, N+1)
    Q = method(x)
    return Q.quad(f)

def quad_list():
    return quad_NC.__subclasses__()

color = {
    'blue': 'lightblue',
    'green': 'lightgreen',
    'pink': 'lightpink',
    'red': 'indianred',
    'orange': 'orange',
}

class quad_NC():
    _name = "generic Newton-Cotes method"
    def __init__(self, x):
        self._weight(x[:-1], x[1:])
    def quad(self, f):
        return np.sum(self.w * f(self.xi))
    def approx(self,f):
        T = []
        if self.xi.ndim > 1:
            for i in range(self.xi.shape[0]):
                T.append(lagrange(self.xi[i,:],f(self.xi[i,:])))
        else:
            for i in range(self.xi.size):
                T.append(np.poly1d([f(self.xi[i])]))            
        return T

class left_rectangle(quad_NC):
    _name = "Left rect"
    _color = color['blue']
    def _weight(self, a, b):
        self.w = np.asanyarray(b) - np.asanyarray(a)
        self.xi = np.asanyarray(a)

class right_rectangle(quad_NC):
    _name = "Right rect"
    _color = color['green']
    def _weight(self, a, b):
        self.w = np.asanyarray(b) - np.asanyarray(a)
        self.xi = np.asanyarray(b)

class midpoint(quad_NC):
    _name = "Midpoint"
    _color = color['pink']
    def _weight(self, a, b):
        self.w = np.asanyarray(b) - np.asanyarray(a)
        self.xi = np.asanyarray(.5*(a+b))

#def NC4(f,a,b):
#    return (b-a)/8*(f(a)+3*f(a+(b-a)/3)+3*f(a+2*(b-a)/3)+f(b))
#def NC5(f,a,b): #boole-villarceau
#    return (b-a)/90*(7*f(a)+32*f(a+(b-a)/4)+12*f(a+(b-a)/2)+32*f(a+3*(b-a)/4)+7*f(b))


class trapeze(quad_NC):
    _name = "Trapeze"
    _color = color['red']
    def _weight(self, a, b):
        a, b = np.asanyarray(a), np.asanyarray(b)
        self.w = np.zeros((a.size, 2))
        self.w[:, 0] = .5*(b-a)
        self.w[:, 1] = .5*(b-a)
        self.xi = np.zeros((a.size, 2))
        self.xi[:, 0] = a
        self.xi[:, 1] = b

class Simpson(quad_NC):
    _name = "Simpson"
    _color = color['orange']
    def _weight(self, a, b):
        a, b = np.asanyarray(a), np.asanyarray(b)
        self.w = np.zeros((a.size, 3))
        self.w[:, 0] = (b-a)/6
        self.w[:, 1] = 2*(b-a)/3
        self.w[:, 2] = (b-a)/6
        self.xi = np.zeros((a.size, 3))
        self.xi[:, 0] = a
        self.xi[:, 1] = .5*(a+b)
        self.xi[:, 2] = b
