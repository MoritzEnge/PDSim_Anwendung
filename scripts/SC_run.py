import numpy as np
import pandas as pd

from src.CompressorModels.SimpleCompressor import simulate_Compressor
from src.CompressorModels import h5reader
from pathlib import Path

from CoolProp.CoolProp import PropsSI

from matplotlib import pyplot as plt
from tqdm import tqdm

dataname = "comp.h5"
result_filepath = Path(__file__).parent.parent.joinpath("res")

def simulate(T0,TC,dtSH=5,fluid="WATER",output=True):

    import os,sys

    p0 = PropsSI("P","T",T0,"Q",0,fluid)
    pc = PropsSI("P","T",TC,"Q",0,fluid)

    if not output:
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
    simulate_Compressor(pe=p0/1e5,pc=pc/1e5,T0=T0+dtSH,datapath = result_filepath.joinpath(dataname))
    if not output : sys.stdout = old_stdout

    sim_res = h5reader.import_h5_as_dict(result_filepath.joinpath(dataname))[2]


    p = sim_res["p"][0]
    T = sim_res["T"][0]
    h = sim_res["h"][0]
    V = sim_res["V"][0]
    m = sim_res["m"][0]
    theta = sim_res["t"]
    eff_adiabatic = float(sim_res["eta_a"])
    eff_volumetric = float(sim_res["eta_v"])

    return p,T,h,V,m,theta,eff_volumetric,eff_adiabatic

def sim_T0_range(T0_start = 80, T0_End = 110, N = 5, TC = 120, dTSH = 5):
    arr_eff_v = []
    arr_eff_a = []
    arr_T0 = np.linspace(T0_start, T0_End, N)

    for i in arr_T0:
        p, T, h, V, m, theta, eff_volumetric, eff_adiabatic = simulate(273.15 + i, 273.15 + TC, dTSH, "WATER", False)
        arr_eff_v.append(eff_volumetric)
        arr_eff_a.append(eff_adiabatic)

    return arr_eff_v, arr_eff_a


def sim_Kennfeld(T0_start=80,T0_End=100,TC_Start=105,TC_End=150,N=5,dTSH=5):
    arr_TC = np.linspace(TC_Start, TC_End, N)
    arr_T0 = np.linspace(T0_start, T0_End, N)

    X,Y,Z1,Z2 = [],[],[],[]
    k = 1

    for j in arr_TC:
        arr_eff_v = []
        arr_eff_a = []
        for i in tqdm(arr_T0):
            p, T, h, V, m, theta, eff_volumetric, eff_adiabatic = simulate(273.15 + i, 273.15 + j, dTSH, "WATER",
                                                                           False)
            arr_eff_v.append(eff_volumetric)
            arr_eff_a.append(eff_adiabatic)
            X.append(i)
            Y.append(j)
            Z1.append(eff_volumetric)
            Z2.append(eff_adiabatic)
        if k>=2:
            CS = plt.tricontour(X, Y, Z1)
            plt.clabel(CS)
            plt.title("Liefergrad")
            plt.show()
            plt.close()

            CS = plt.tricontour(X, Y, Z2)
            plt.clabel(CS)
            plt.title("Gütegrad")
            plt.show()
            plt.close()
        k+=1

    return X,Y,Z1,Z2

if __name__ == "__main__":
    X,Y,Z1,Z2 = sim_Kennfeld(T0_start=80,T0_End=100,TC_Start=105,TC_End=125,N=20,dTSH=5)

    """CS = plt.tricontour(X,Y,Z2)
    plt.clabel(CS)
    plt.title("Gütegrad")
    plt.show()
    plt.close()

    CS = plt.tricontour(X, Y, Z1)
    plt.clabel(CS)
    plt.title("Liefergrad")
    plt.show()
    plt.close()"""
