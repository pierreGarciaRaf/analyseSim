import numpy as np
from scipy.integrate import quad
from .. import pyQuad

def test(f, a, b):
    Ie = quad(f, a, b, epsabs = 1e-15)[0]
    print("*"*70)
    print("accurate value of the integral obtained by scipy.integrate.quad")
    print(Ie)
    list_methods = pyQuad.quad_list()
    n_methods = len(list_methods)
    vN = 2**np.arange(12)
    A = np.zeros((vN.size, n_methods))
    for i in range(n_methods):
        L = list_methods[i]
        for k in range(vN.size):
            N = vN[k]
            q = L(np.linspace(a, b, N+1))
            A[k, i] = q.quad(f)
    print("*"*70)
    print("Numerical approximation for several quadrature formula")
    print("-"*70)
    print("    ", end=' ')
    for i in range(n_methods):
        print("{:>10s}".format(list_methods[i]._name), end=' ')
    print()
    for k in range(vN.size):
        print("{0:4d}".format(vN[k]), end=' ')
        for i in range(n_methods):
            print("{0:10.3e}".format(A[k, i]), end=' ')
        print()
    print("-"*70)
    print("Error")
    print("-"*70)
    print("    ", end=' ')
    for i in range(n_methods):
        print("{:>10s}".format(list_methods[i]._name), end=' ')
    print()
    for k in range(vN.size):
        print("{0:4d}".format(vN[k]), end=' ')
        for i in range(n_methods):
            print("{0:10.3e}".format(A[k, i] - Ie), end=' ')
        print()
    print("*"*70)
