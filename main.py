from finsim.ui import UI
from finsim.simulation import Simulation
from finsim.sim_data import SimData

UI.initialise()
sim_data = SimData()
simulation = Simulation(sim_data)

UI.begin()
simulation.simulate()
