from finsim import ui
from finsim.simulation import Simulation
from finsim.sim_data import SimData

ui.initialise()
sim_data = SimData()
simulation = Simulation(sim_data)

ui.begin()
simulation.simulate()
