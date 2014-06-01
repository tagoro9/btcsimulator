__author__ = 'victor'
from .core import celery
from simulator.btcsimulator import Simulator

@celery.task(name="tasks.add")
def start_simulation_task(miners, days):
    print "Running task..."
    Simulator.standard(1, 1)
