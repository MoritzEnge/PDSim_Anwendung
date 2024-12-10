import numpy as np
import pandas as pd

from src.CompressorModels.SimpleCompressor import simulate_Compressor
from src.CompressorModels import h5reader
from pathlib import Path

from CoolProp.CoolProp import PropsSI

from matplotlib import pyplot as plt

dataname = "comp.h5"
result_filepath = Path(__file__).parent.parent.joinpath("res")

def simulate(T0,TC,dtSH=5,fluid="WATER"):

    import os,sys

    p0 = PropsSI("P","T",T0,"Q",0,fluid)
    pc = PropsSI("P","T",TC,"Q",0,fluid)

    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    simulate_Compressor(pe=p0/1e5,pc=pc/1e5,T0=T0+dtSH,datapath = result_filepath.joinpath(dataname))
    sys.stdout = old_stdout

    sim_res = h5reader.import_h5_as_dict(result_filepath.joinpath(dataname))[2]


    p = sim_res["p"][0]
    T = sim_res["T"][0]
    h = sim_res["h"][0]
    V = sim_res["V"][0]
    m = sim_res["m"][0]
    theta = sim_res["t"]
    eff_adiabatic = float(sim_res["eta_a"])
    eff_volumetric = float(sim_res["eta_v"])

    return eff_volumetric,eff_adiabatic

if __name__ == "__main__":
    from tqdm import tqdm
    arr_eff_v = []
    arr_eff_a = []
    arr_T = np.linspace(80,100,5)
    for i in tqdm(arr_T):
        eff_v,eff_a = simulate(273.15+i,273.15+120,5,"WATER")
        arr_eff_v.append(eff_v)
        arr_eff_a.append(eff_a)
    plt.plot(arr_T,arr_eff_a,label="Gütegrad")
    plt.plot(arr_T,arr_eff_v,label="Liefegrad")
    plt.legend()
    plt.show()

"""print(eff_adiabatic, eff_volumetric)"""


"""df = pd.DataFrame()
df["p"] = p
df["T"] = T
df["h"] = h
df["V"] = V
df["m"] = m
df["theta"] = theta
df.to_csv(result_filepath.joinpath(dataname.replace(".h5", ".csv")))"""
