## Project proposal
Idea: Discord Bot which has a main service that listens to discord servers for commands. Multiple microservices are responsible for executing the commands. 
Each microservice is responsible for a dedicated command pattern, e.g., message starts with "--ttt" (tic-tac-toe game), "--math"(calculator), "--tl" (translator).

We spawn and delete pods / microservice instances based on the current usage of the service. (Vertical / horizontal scaling?)

We don't need any data storage. However, we may want additional logging which services were used in which amount. 

Note: for tic-tac-toe we would need state management.

## Mile stones
- Proof of concept: 
  - Check whether Discord Bot works locally (using Discord API)
  - Automatic deployment using Github actions
    - Kubernetes
      - for availability we would select one of the non-self-hosted services such as Google Cloud
  - Discord message listener in main service with some dummy microservice without any functionality
- Actual microservices
  - Create microservice architecture that allows dynamic registration / deregistration of microservices on main service
  - A few very simple microservices for demonstration and their automatic deployment
  - Ensuring that endpoints are not globally accessible
- Vertical scaling (more processes on a server)
  - Load simulation with microservice
- Optional: Support multiple server instances

## Responsibilities
Christian:
- Local Discord bot + initial deployment

Raphael:
- Vertical scaling

Christoph:
- Automatic deployment of microservices

Everyone should create simple microservices.
