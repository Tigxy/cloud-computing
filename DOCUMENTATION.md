# Vertical scaling of individual microservice

Each microservice deployment has an accompanying Vertical Pod Autoscaler (vpa) configured. The vpa's are set to automatically update the pods based on the load. 

Example:  
```
apiVersion: "autoscaling.k8s.io/v1"
kind: VerticalPodAutoscaler
metadata:
  name: stress-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: python-stress-service
  updatePolicy: 
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
      - containerName: '*'
        controlledResources: 
          - cpu
```

The update mode is set to 'Auto', which enables the VPA updater to terminate and spin up new pods with the recommended CPU values set. 

## Deployment configuration notes:
* Each deployment requires its own VPA configuration. There is no support for selectors that would allow one VPA for multiple deployments.
* At least 3 replicas are required in the deployment to support automatic updating of pods.
* For trying it out locally, it is recommended to set the `cpu` value to `1m`. The service is set up as a web service that will only execute load when requests are generated. Usually, when trying this out locally, it can take a bit to start up everything and also execute requests. If one sets the value too high, it might be the case that VPA does not update in the first run and then refrains from updating for many hours as the upper bound is set too high. More on that later in the **Findings** section.

## Local setup notes:
* **Note for `minikube` users:** VPA is not part of minikube by default, therefore one needs to manually install it by following the instructions [here](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler#installation).
* **Note for `minikube` users:** The VPA relies on the metric server to get recent CPU and memory values. The metric server is disabled by default in minikube. You can enable it with ```minikube addons enable metrics-server```.


## Trying it out locally
We advise for a local test with only the `stress` microservice, as it is hard to show quick reactions of the VPA in a running environment.

1. Switch to the `microservices/stress` directory.
2. Apply the deployment with `kubectl apply -f deployment.yaml`.
3. Apply the load balancer with `kubectl apply -f local_lb.yaml`.
4. **Note for `minikube` users:** Start a tunnel with `minikube tunnel`.
5. **Note for `minikube` users:** Expose the load balancer in minikube with `minikube service micro-lb`. Then, copy the local URL for later use, e.g. 'http://127.0.0.1:60771'.
6. Generate some load by accessing this URL with a request, e.g. `http://127.0.0.1:60771/--stress%2010m%208p`. Do this in a few tabs, e.g. 5, to make sure that all replicas get some load.
7. Execute `kubectl top pods` and wait for the metric server to get recent metrics for all pods that show that they execute load.
8. Apply the `vpa.yaml` with `kubectl apply -f vpa.yaml`.
9. Look at one of the pods that is returned with `kubectl get pods` with `kubectl describe pod <pod>` and check the assigned CPU resources. It should be `1m`.
10. Execute `kubectl get pods` a few times until you see pods being terminated and new ones spun up.
11. Execute `kubectl describe pod <pod>` for one of the new ones. You should see a higher CPU value now.


## Findings 
Initially, we believed that we can use the VPA as a quick remediation action against spikes in load, but the VPA is not designed for fast actions and therefore not well-suited to react to spikes in load quickly. 

A pod is only updated, if the recommended CPU and memory values are below the lower bound or greater than the upper bound. These bounds are implemented to scale with time, so the shorter a pod is running, the less eager the VPA is with updating the pods with new recommended values. This can be seen in the [implementation](https://github.com/kubernetes/autoscaler/blob/d81bdb87ce5d6801d0030f02c2e96080b53a209e/vertical-pod-autoscaler/pkg/recommender/logic/recommender.go#L28) of the recommender.
Especially, when trying to showcase VPA for a low-request web-service - which we have in our project, this can be a hassle.

This behavior can also be noticed with the logs that one can see by checking the logs for the vpa-updater pod, e.g.:  
```I0102 23:45:23.825037       1 update_priority_calculator.go:133] not updating a short-lived pod default/python-stress-service-6cbbcb9477-c2878, request within recommended range```


