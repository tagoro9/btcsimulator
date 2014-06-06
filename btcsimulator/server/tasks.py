__author__ = 'victor'
from .core import celery
from simulator.btcsimulator import Simulator

@celery.task(name="tasks.simulation")
def start_simulation_task(miners, days, type):
    if type == 'standard':
        Simulator.standard(miners, days)
    elif type == 'fifty-one':
        Simulator.fifty_one(miners, days)
