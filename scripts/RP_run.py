from src.CompressorModels.RollingPiston import simulate_RollingPiston
from pathlib import Path

dataname = "RollingPiston.h5"
result_filepath = Path(__file__).parent.parent.joinpath("res")
simulate_RollingPiston(pe=0.5,pc=2,T0=370,datapath=result_filepath.joinpath(dataname))
