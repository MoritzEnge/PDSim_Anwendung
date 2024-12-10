from __future__ import division, print_function


from numpy import pi,cos,sin,asin,tan
import os,sys

from PDSim.flow.flow import FlowPath
from PDSim.flow import flow_models
from PDSim.misc.datatypes import arraym
from PDSim.core.containers import ControlVolume, Tube
from PDSim.core.core import PDSimCore

from CoolProp import State
from CoolProp import CoolProp as CP
from pathlib import Path


class RollingPiston(PDSimCore):
    def __init__(self):
        PDSimCore.__init__(self)

    def V_dV(self,theta):

        def sec(x) : return 1/cos(x)

        Rc = self.Rc
        Hc = self.Hc
        Rr = self.Rr
        e = Rc-Rr
        Rv = self.Rv
        b = self.b

        alpha = asin((e/(Rr+Rv))*sin(theta))
        xi = Rc+Rv-(Rr+Rv)*cos(alpha)-e*cos(theta)

        Vt = pi*(Rc**2 - Rr**2)*Hc
        dalphadtheta = ((e*self.omega*cos(theta))/(Rr+Rv))*(1-(((e)/(Rr+Rv))*sin(theta)))**(-0.5)
        dxidtheta = (Rr+Rv)*sin(alpha)+e*self.omega*sin(theta)


        V = Vt-0.5*Rc**2*Hc*theta +0.5*Rr**2*Hc*(theta+alpha)+0.5*e*Hc*(Rr+Rv)*sin(theta+alpha)-0.5*Rv**2*Hc*tan(alpha)-0.5*b*Hc*xi
        dVdtheta = 0.5 * (Rr**2-Rc**2) * Hc * self.omega + 0.5 * Rr ** 2 * Hc * dalphadtheta + 0.5 * e * Hc * (Rr + Rv) * cos(alpha) * (theta + alpha) * (self.omega + dalphadtheta) - 0.5 * Rv ** 2 * Hc * sec(alpha) ** 2 * dalphadtheta - 0.5 * b * Hc * dxidtheta
        return V,dVdtheta

    def Suction(self,FlowPath,**kwargs):
        if FlowPath.key_up =='A':
            return 0
        else:
            try:
                FlowPath.A = self.A_suction
                mdot = flow_models.IsentropicNozzle(FlowPath.A,FlowPath.State_up,FlowPath.State_down)
                return mdot
            except ZeroDivisionError:
                return 0

    def Discharge(self,FlowPath,**kwargs):
        if FlowPath.key_down =='A':
            return 0
        else:
            try:
                FlowPath.A = self.A_discharge
                mdot = flow_models.IsentropicNozzle(FlowPath.A,FlowPath.State_up,FlowPath.State_down)
                return mdot
            except ZeroDivisionError:
                return 0

    def TubeCode(self,Tube):
        Tube.Q = flow_models.IsothermalWallTube(Tube.mdot,Tube.State1,Tube.State2,Tube.fixed,Tube.L,Tube.ID,T_wall = self.Tlumps[0])

    def heat_transfer_callback(self,theta):
        return arraym([0.0]*self.CVs.N)

    def mechanical_losses(self):
        return self.Wdot_parasitic

    def ambient_heat_transfer(self):
        return self.h_shell*self.A_shell*(self.Tamb-self.Tlumps[0])

    def lump_energy_balance_callback(self):
        self.Wdot_mechanical = self.mechanical_losses()
        self.Qamb = self.ambient_heat_transfer()
        return self.Wdot_mechanical +self.Qamb

def simulate_RollingPiston(pe,pc,T0,datapath):


    comp = RollingPiston()
    comp.Rc = 7/1000
    comp.Hc = 2/1000
    comp.Rr = 5/1000
    comp.Rv = 0.5/1000
    comp.b = 0.5/1000

    Vt = pi * (comp.Rc ** 2 - comp.Rr ** 2) * comp.Hc

    comp.omega = 300

    comp.d_discharge = 0.001
    comp.d_suction = 0.002
    comp.A_discharge = pi * 0.25 * comp.d_discharge ** 2
    comp.A_suction = pi * 0.25 * comp.d_suction ** 2

    comp.h_shell = 0.01
    comp.A_shell = 10
    comp.Tamb = 300

    comp.Wdot_parasitic = 0.01
    Ref = 'Water'
    inletState = State.State(Ref,dict(T=T0 ,P=pe*100),phase='gas')

    T2s = comp.guess_outlet_temp(inletState, pc*100)
    outletState = State.State(Ref, {'T': T2s, 'P': pc*100}, phase='gas')

    mdot_guess = inletState.rho*Vt*comp.omega/(2*pi)

    comp.add_CV(ControlVolume(key="A",
                              initialState = outletState.copy(),
                              VdVFcn = comp.V_dV,
                              becomes = "A"))

    comp.add_tube(Tube(key1="inlet.1",key2="inlet.2",L=0.03,ID=0.01,mdot=mdot_guess,State1=inletState.copy(),fixed=1,TubeFcn = comp.TubeCode))
    comp.add_tube(Tube(key1="outlet.1",key2="outlet.2",L=0.03,ID=0.01,mdot=mdot_guess,State2=outletState.copy(),fixed=2,TubeFcn = comp.TubeCode))

    comp.add_flow(FlowPath(key1="inlet.2",key2="A",MdotFcn=comp.Suction))
    comp.add_flow(FlowPath(key1="outlet.1",key2="A",MdotFcn=comp.Discharge))

    comp.connect_callbacks(endcycle_callback=comp.endcycle_callback,
                           heat_transfer_callback=comp.heat_transfer_callback,
                           lumps_energy_balance_callback=comp.lump_energy_balance_callback)

    comp.solve(key_inlet="inlet.1",
               key_outlet="outlet.2",
               solver_method="Euler",
               OneCycle=False,
               UseNR=True,
               plot_every_cycle=False)

    del comp.FlowStorage
    from PDSim.misc.hdf5 import HDF5Writer
    h5 = HDF5Writer()
    h5.write_to_file(comp, datapath)


