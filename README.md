# cloud-computing
Repository for cloud computing project.

## Project proposal
Idea: Discord bot which has a main service that listens to discord servers for commands. Multiple microservices are responsible for executing the commands. 
Each microservice is responsible for a dedicated command pattern, e.g., message starts with "--ttt" (tic-tac-toe game), "--math"(calculator), "--tl" (translator).

We spawn and delete pods / microservice instances based on the current usage of the service. (Vertical / horizontal scaling?)

We don't need any data storage. However, we may want additional logging which services were used in which amount. 
Note: for tic-tac-toe we would need state management.

## Mile stones
- Proof of concept: 
  - check whether discord api works
  - automatic deployment when pushed on Github, Discord listener, maybe some dummy microservice without any functionality
- Actual microservices
