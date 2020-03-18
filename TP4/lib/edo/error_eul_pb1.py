import numpy as np
import bqplot as bp

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
    tmp  = np.abs(tmp0 - np.array([schema(a,h) for h in dt]))
    return np.array([tmp,tmp/tmp0])

#xs = bp.LinearScale()
#ys = bp.LinearScale()

xs = bp.LogScale()
ys = bp.LogScale()

dt = np.arange(10)
dt = 10.**(-dt)
a=0.1
y = get_error(a,dt)

xax = bp.Axis(scale=xs,tick_format='2.0e', label='pas de temps', grid_lines='solid')
yax = bp.Axis(scale=ys,tick_format='2.0e', orientation='vertical', label='erreur', grid_lines='solid')

line = bp.Lines(x=dt, y=y, scales={'x': xs, 'y': ys}, colors=['red','green'], labels=['erreur (EE)','erreur relative (EE)'],display_legend=True)
bp.Figure(marks=[line], axes=[xax, yax], animation_duration=1000)

y2 = get_error(a,dt,schema=approx_milieu)
line2 = bp.Lines(x=dt, y=y2, scales={'x': xs, 'y': ys}, colors=['blue','black'], labels=['erreur (PM)','erreur relative (PM)'],display_legend=True)