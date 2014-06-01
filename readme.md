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

* **Python 2.7.*.** Most parts of the simulator are written in python. Higher versions of python are not supported since [Gevent](http://www.gevent.org/), which is used
to support web sockets does not work well in higher Python versions
* **Celery.** Asynchronous task job used to run simulations without blocking the server or the web app. It can be installed via pip `pip install celery`. More information
 about Celery can be found [here](http://www.celeryproject.org/).
* **Redis.** Download and install [Redis](http://redis.io). The simulator uses redis as data store and as message broker to run background tasks in Celery workers.
* **Bower.** [Bower](http://bower.io/) is a package manager for the web. It is used to manage all the web app dependencies (jQuery, Backbone, lodash,...). In order
to install it you need to have [Node](http://nodejs.org/) and [Npm](https://www.npmjs.org/) up and running. `npm install -g bower`
* **Brunch.** [Brunch](http://brunch.io/) is the build tool used to create the web app. As with bower, just run `npm install -g brunch`

##Getting started

In order to run the simulator we need to have a redis server running.

    cd redis-2.8.x/src
    ./redis-server

**All the following commands must be run in the project root folder.**

Install all python dependencies defined in `requirements.txt`.

    pip install -r requirements.txt

Install all bower dependencies.

    bower install

Compile the web app using `brunch`.

    brunch b

Run the Celery worker.

    celery -A run_server.celery worker --loglevel=info &

Run the web server.

    python run_server.py

By default server will listen on port `5000`, so just open a browser and type [http://localhost:5000](http://localhost:5000).
If all went fine, the welcome screen should appear.

##Structure
This project consists on three main modules:

* A [Backbone.js](http://backbonejs.org) webapp which controls simulation and displays data visualizations using [D3](http://d3js.org).
* A web server that exposes a REST API with all the simulation information stored in Redis. This server is also in charge of launching simulations
through the Celery worker and notifies any change of state to the web app using web sockets.
* A python library that drives the simulation and stores every single piece of data or communication between nodes in redis for further analysis.
 The simulation is run under [SimPy](http://simpy.readthedocs.com), a discrete-event simulation framework.

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
