__author__ = 'victor'
from .core import celery
from simulator.btcsimulator import Simulator

@celery.task(name="tasks.add")
def start_simulation_task(miners, days):
    Simulator.standard(miners, days)
