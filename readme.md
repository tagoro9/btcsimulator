#Bitcoin network protocol simulator
The goal of this project is to build a Bitcoin simulator, that is, a piece of software that allows
to reproduce the behavior of the Bitcoin system. The simulator may be used to study how
different user behaviors impact on system performance, and if certain theoretical attacks to the network
are feasible to perform on a real scenario.

**Inspired by rbrune's [btcsim](https://github.com/rbrune/btcsim).**


## Features

* Block mining simulation.
* Bandwidth, latency and other network handicaps.
* Data and event recording for further analysis.

##Prerequisites

* Python 2.7.*. Most parts of the simulator are written in python.
* Redis. Download and install [Redis](http://redis.io). The simulator uses redis as data store. In order to work properly the application must
connect to a redis server instance.
* Brunch
* Bower
* Celery

##Getting started

In order to run the simulator we need to have a redis server running.

    cd redis-2.8.x/src
    ./redis-server

Install all python dependencies defined in `requirements.txt`

    pip install

Compile the angular webapp using `grunt`.

    cd btcsimulator/app
    grunt

Run the web server

    python server.py

By default server will listen on port `3000`, so just open a browser and type [http://localhost:3000](http://localhost:3000)

##Structure
This project consists on three main modules

* An Angularjs webapp which controls simulation and displays data visualizations.
* A webserver that communicates both with the app using websockets to send the data stored in redis and with the simulator
using the redis pubsub messsage system in order to control the simulation.
* A python library that drives the simulation using a [SimPy](http://simpy.readthedocs.com), a discrete-event simulation
framework and stores every single piece of data or communication between nodes in redis for further analysis.

##Getting to know Bitcoin
If you're new to Bitcoin and don't know much about that cryptocurrency that seems to be the talk of the town, here there
are a few useful links.

* [Bitcoin Me](http://bitcoinme.com)
* [Bitcoin in Plain English](http://codinginmysleep.com/bitcoin-in-plain-english/)
* [Bitcoin mining in Plain English](http://codinginmysleep.com/bitcoin-mining-in-plain-english/)
* [Bitcoin wiki](https://en.bitcoin.it/wiki/Main_Page)

##Acknowledgements
This simulator has been developed as part of my Master's Degree in Security of the Information
and Communication Technologies final project at [UOC](http://www.uoc.edu/).
