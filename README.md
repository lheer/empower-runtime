EmPOWER: Mobile Networks Operating System
=========================================

### What is EmPOWER?
EmPOWER is a new network operating system designed for heterogeneous mobile networks.

### Top-Level Features
* Supports both LTE and WiFi radio access networks
* Northbound abstractions for a global network view, network graph, and
  application intents.
* REST API and native (Python) API for accessing the Northbound abstractions
* Support for Click-based Lightweight Virtual Networks Functions
* Declarative VNF chaning on precise portion of the flowspace
* Flexible southbound interface supporting WiFi APs LTE eNBs

Checkout out our [website](http://empower.create-net.org/) and our [wiki](https://github.com/5g-empower/empower-runtime/wiki)

This repository includes the reference controller implementation and the associated SDK.

### Changes
This fork adds the WTP/controller discovery feature via UDP broadcasts: The agent sends a broadcast packet to the local network and the controller replies to notify the agent about its presence.
It also returns the EmPOWER hello packets sent by the agent in order to implement a bidirectional heartbeat and therefore extend the error management.

Code is released under the Apache License, Version 2.0.
