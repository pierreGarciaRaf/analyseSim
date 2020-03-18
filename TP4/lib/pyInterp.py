import numpy as np
import scipy.interpolate as interp
import warnings
import sys
import copy
import itertools as it

warnings.simplefilter('ignore', np.RankWarning)


def interp_list():
    return Lagrange_interpolator.__subclasses__()

color = {
    'blue': (0.06, 0.62, 0.91),
    'green': (0.01, 0.84, 0.35),
    'pink': (1., 0., 0.5),
    'red': (0.97, 0.14, 0.05),
}

class Lagrange_interpolator():
    _name = "generic Lagrange interpolator"
    _color = (0., 0., 0.)
    def __init__(self, x, y, args = ()):
        self.x = np.asanyarray(x, dtype = 'float64')
        self.y = np.asanyarray(y, dtype = 'float64')
        if self.x.size != self.y.size:
            print("Error: wrong parameters (x and y must have the same length !)")
            sys.exit()
        self.n = self.x.size
        self.args = args
        self._build()
    def __str__(self):
        return self._name


class scipy_Lagrange(Lagrange_interpolator):
    """
    Interpolation with the scipy module
    """
    _name = "scipy"
    _color = color['blue']
    def _build(self):
        #self.p = np.poly1d(np.polyfit(self.x, self.y, self.n))
        self.p = interp.lagrange(self.x, self.y)
    def eval(self, xx):
        return self.p(xx)


class vdm(Lagrange_interpolator):
    """
    Interpolation with the Vandermonde matrices
    the polynomial is written in the canonical basis
    """
    _name = "vandermonde"
    _color = color['red']
    def _build(self):
        # build the Vandermonde matrix
        A = np.ones((self.n, self.n))
        for k in range(1, self.n):
            A[:, k] = A[:, k-1] * self.x
        # solve the linear system
        self.p = np.linalg.solve(A, self.y)
    def eval(self, xx):
        # evaluate the polynomial with the Horner algorithm
        xx = np.asanyarray(xx, dtype = 'float64')
        yy = np.zeros(xx.shape)
        for k in range(self.n-1,-1,-1):
            yy *= xx
            yy += self.p[k]
        return yy if xx.size != 1 else np.asscalar(yy)


class Lagrange(Lagrange_interpolator):
    """
    Interpolation with the Lagrange formula
    the polynomial is written in the dual basis of the interpolation points

    P(x) = \sum_{i=1}^n y_i/((x-x_i)\omega'_n(x_i)) / \sum_{i=1}^n 1/((x-x_i)\omega'_n(x_i))
    """
    _name = "Lagrange"
    _color = color['pink']
    def _build(self):
        # build the omega'_n(x_i)
        w = np.ones((self.n, ))
        for i in range(self.n):
            for j in it.chain(range(i), range(i+1, self.n)):
                w[i] *= (self.x[i] - self.x[j])
        self.weight = 1./w
    def eval(self, xx):
        # evaluate the polynomial
        if xx.size == 1:
            N, D = 0., 0.
            for i in range(self.n):
                if xx == self.x[i]:
                    return self.y[i]
                dxi = self.weight[i] / (xx-self.x[i])
                N += self.y[i] * dxi
                D += dxi
        else:
            N, D = np.zeros(xx.shape), np.zeros(xx.shape)
            ind = []
            for i in range(self.n):
                ind.append(np.where(xx == self.x[i]))      # indices where P(xi) = yi
                indloc = np.where(xx != self.x[i])
                dxi = self.weight[i] / (xx[indloc] - self.x[i]) # avoid divide by 0
                N[indloc] += self.y[i] * dxi
                D[indloc] += dxi
            for i in range(self.n): # fix yi in xi
                N[ind[i]], D[ind[i]] = self.y[i], 1.
        return N / D


class divided_differences(Lagrange_interpolator):
    """
    Interpolation using the divided differences method
    the polynomial is written in the basis of the omega_k

    omega_0 = 1
    omega_j = (X-x_1)...(X-x_j), 1 \leq j \leq n

    P = \sum_{k=0}^{n-1} d_{k,k} omega_k
    """
    _name = "divided differences"
    _color = color['green']
    def _build(self):
        # build the divided differences
        self.d = copy.copy(self.y)
        for i in range(1, self.n):
            self.d[i:] = (self.d[i:] - self.d[i-1:-1]) / (self.x[i:] - self.x[:self.n-i])
    def eval(self, xx):
        xx = np.asanyarray(xx, dtype = 'float64')
        yy = self.d[-1] * np.ones(xx.shape)
        for k in range(self.n-2, -1, -1):
            yy *= xx - self.x[k]
            yy += self.d[k]
        return yy if xx.size != 1 else np.asscalar(yy)
