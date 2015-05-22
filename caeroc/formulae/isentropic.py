import numpy as np
from caeroc.formulae.base import FormulaeBase


class Isentropic(FormulaeBase):
    """Isentropic flow relations for quasi 1D flows"""
    def __init__(self):
        self.keys = ['M','p_p0', 'rho_rho0', 't_t0', 'a_a0', 'A_At']
        super(Isentropic, self).__init__()

    def p_p0(self,M, gamma=1.4):
        ans = self.t_t0(M, gamma,False) ** (gamma / (gamma - 1))
        self.store('p_p0', ans)
        return ans
        
    def rho_rho0(self,M, gamma=1.4):
        ans = self.t_t0(M, gamma,False) ** (1 / (gamma - 1))
        self.store('rho_rho0', ans)
        return ans

    def t_t0(self,M,gamma=1.4,store=True):
        ans = (1+(gamma-1)/2 * M**2) ** -1
        if store:
            self.store('t_t0', ans)
        return ans

    def M(self, p_p0=None, rho_rho0=None, t_t0=None,
            a_a0=None, A_At=None, pm=None, gamma=None):
        if gamma is None:
            g = self.gamma
        else:
            g = gamma

        if p_p0 is not None:
            self.store('p_p0', p_p0) 
            M = np.sqrt(2. * ((1./np.power(p_p0, (g-1.)/g)) - 1.) / (g-1.))

        elif rho_rho0 is not None:
            self.store('rho_rho0', rho_rho0) 
            M = np.sqrt(2. * ((1./np.power(rho_rho0, (g-1.))) - 1.) / (g-1.))

        elif t_t0 is not None:
            self.store('t_t0', t_t0) 
            M = np.sqrt(2. * ((1./t_t0)-1.)/(g-1.))

        elif A_At is not None:
            self.store('A_At', A_At) 
            if self.data['M'] is None:
                mnew = 1e-4
            else:
                mnew=self.data['M']
            m=0.0
            while( abs(mnew-m) > 1e-6):
              m=mnew
              phi=self.a_as(m,g)
              s=(3. - g) / (1. + g)
              mnew=m - (phi - v) / (np.power(phi * m,s) - phi / m)
            M = m
        elif pm is not None:
            self.store('pm', pm) 
            mnew=2.0
            m=0.0
            while( abs(mnew-m) > 1e-5):
              m=mnew
              fm=(self.pm(m,g)-v)#*3.14159265359/180.
              fdm=np.sqrt(m**2 - 1.) / (1 + 0.5*(g-1.) * m**2)/m
              mnew=m-fm/fdm
        else:
            raise ValueError('Insufficient data to calculate Mach number')

        self.store('M', M)
        return M



class Expansion(Isentropic):
    """Isentropic expansion fan flow relations"""

    def __init__(self):
        super(Isentropic, self).__init__()
        self.keys.append('pm')


    def M2(self, M1, theta, gamma=1.4):
        if M1<0:
            raise ValueError('Subsonic flow.')
        if theta < 0 or theta > np.pi/2:
            raise ValueError('Incorrect deflection angle. Cannot calculate!')
        pm1 = self.pm(M1, gamma)
        pm2 = pm1 + theta

        mnew = 2.0
        m = 0.0
        while(np.abs(mnew - m) > 0.00001):
          m=mnew
          fm=(self.pm(m,gamma)-pm2)#*np.pi/180.
          fdm=np.sqrt(m**2 - 1.)/(1. + 0.5*(gamma-1.)*m**2)/m
          mnew=m-fm/fdm
          
        M2 = m
        return M2
       
    def pm(self,M1, gamma=1.4):
        if M1>1.:
            g = gamma
            m = M1
            n = (np.sqrt((g + 1.) / (g - 1.)) *
                 np.arctan(np.sqrt((g - 1.) / (g + 1.) * (m * m - 1.))))
            n = n - np.arctan(np.sqrt(m * m - 1.))
        elif M1==1:
            n = 0.
        else:
            n = None
            
        numax=(np.sqrt((gamma+1.)/(gamma-1.))-1)*90.
        if(n<=0.0 or n>=numax):
            raise ValueError("Prandtl-Meyer angle out of bounds")            
        return n

