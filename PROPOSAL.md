# Project proposal

## Overview

**Idea:** Provide Continuous Deployment of a **Discord bot** to Google Cloud with Github Actions, 
which uses microservices to handle chat queries and allows automatic scaling of those services.
Details are in the milestones.

[Discord](https://discord.com/) is an instant messaging platform. Users can communicate with voice calls, video calls 
and text messaging. It also allows distributing media and files. Everyone can create a Discord server for free 
and provide a custom structure of channels where text messages can be exchanged. Discord provides libraries 
to interact with a Discord server, therefore a bot can be made to join a Discord server and listen and react on chat messages.

The reason that we went for this idea is that all group members use Discord frequently and we all have use-cases for a Discord bot that we would like to implement, sometime. This project would allow us to set up a microservice architecture and deployment model that we could use even after this course.

**Note on engineering:** The code for the Discord bot is not available yet, but we will keep the code implementation to a minimum.
It is pretty easy to set up a Discord bot with a Discord library, and we will only provide very simple 
query implementations, e.g. ```--echo hello```, which would only require a one-liner implementation 
that returns 'hello'. The main work will be to implement the microservice architecture such that communication 
works when deployed in CD fashion on a Google Cloud instance, and scaling.

## Milestones

+ **Proof of concept (main service)**
  - **Architecture:** Set up a Discord client in Python with the library
  [discord.py](https://pypi.org/project/discord.py/) and ensure that communication with a custom 
  Discord server (not publicly exposed for now) works and that it can execute a simple query like ```--echo hello```
  directly on the main service without any microservice.
  - **Continuous deployment:** Configure with GitHub Actions. Upon merge into the main branch, the main service
  should be automatically deployed in a Kubernetes environment in a Google Cloud instance. One container 
  should be started for the main service.
  - **Initial Kubernetes/Google Cloud setup:** Setup a Google Cloud instance with Kubernetes that will be used throughout 
  the project to deploy the code.
  - **Demonstration:** Set up a Discord server and add the bot to it. It should be possible to
  perform queries, which the bot, running in Kubernetes, gives an answer to.
+ **Query/worker microservices:**
  - **Architecture:** Create a configuration setting on the main service that gives it knowledge
                      about which microservices can be called and for which query patterns they need 
                      to be routed to. Each microservice should provide a single REST API method with 
                      the query string as the input, e.g. ```--echo hello```, and the string that should be 
                      written into the chat as a result, e.g. ```hello```.
  - **Architecture advanced (optional):** 
  Use [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
  to configure the microservice routing rules instead of implementing them manually in the 
  main service.
  - **Security**: Ensure that the microservice endpoints are not publicly accessible.
  - **Continuous deployment**: Configure with GitHub Actions. Upon merge into the main branch, all the microservices 
  that are configured to be automatically deployed should be deployed in a Kubernetes environment in a Google
  Cloud instance. One container should be started initially for each microservice - scaling will ensure that we can handle 
  the load later on.
  - **Demonstration:** 
  Provide 3 very simple query worker implementations for the demo in optimally 
  at least two different programming languages, to showcase that the architecture is language agnostic.   
  Examples: ```--add 5 2```, ```--time```, ```--echo hello```.
+ **Vertical scaling of individual microservices**
  - **Configuration:** Configure Kubernetes vertical pod autoscaling to spin up new pods for the query worker
  microservices as soon as a microservice is detected to be under stress.
  - **Demonstration:** Write a microservice that allows to simulate a high load scenario to demo vertical scaling. 
  This microservice should execute for a specific query, e.g. ```--stress 5m```,
  which would cause the 'stress' microservice to simulate high load for 5 minutes.
  We plan to use the Python library [stress](https://pypi.org/project/stress/) or 
  [stresspy](https://pypi.org/project/stressypy/) to simulate high load. It should then be possible 
  to execute further ```stress 5m``` calls that get routed to other pods, 
  even though the initially started pod for the microservice is still under load.
+ **Optional**
  - Support multiple Discord server instances
  - Stateful microservices for e.g. games (tic tac toe?)
  - Logging of microservice usage

## Responsibilities

**Christian:**
- Local Discord bot + initial deployment (mainly milestone 1)

**Christoph:**
- Automatic deployment of microservices (mainly milestone 2)

**Raphael:**
- Vertical scaling (mainly milestone 3)

Everyone should create one simple microservice in a programming language of choice.

## Presentation

1. **Demo - functionality:**
We will showcase our bot's functionality by presenting the supported queries together with its response.
Afterwards, we will invite everyone to join a Discord server where the bot is running on, either with an invitation URL 
or a QR code, so that everyone can try out the bot on their own. 

2. **Demo - Continuous Delivery of a new microservice:** 
We will demonstrate the ease of creating and configuring a new query microservice ready for deployment. By merging the
implementation and changes into the Github branch, CD redeploys the project, making the new microservice accessible 
in Discord. Moreover, we describe what happens in CD (due to Github Actions) and Kubernetes as well.

3. **Demo - Automatic vertical scaling:** 
We will run multiple ```stress``` calls simultaneously to simulate high load. We will then show indicators of high load
in Kubernetes and that new pods are spun up as a response to it.

4. **Overview of implementation/configuration:**
This point might not be standalone but part of the other points in the final presentation.
We will give an overview of our implementation and configuration and explain our reasoning and experience.

