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


# Using an ingress controller for service communication
For our architecture we decided to combine an ingress controller (for routing) with multiple
cluster-ip services to expose the microservice deployments to our main service. This way we can map bot commands
to corresponding microservices by specifying path rules in our ingress.yaml.

TODO: general way service set up, deployment, ingress


## Trying it out locally with minikube:

1. Start minikube

```bash
minikube start
```

2. Enable the ingress addon

```bash
minikube addons enable ingress
```
4. Apply the services and deployment YAML for each microservice 

```bash
kubectl apply -f /micorservices/echo/deployment.yaml
...
```
5. Apply the ingress for local deployment 
```bash
kubectl apply -f ingress_local.yaml
```
6. Open the cluster IP combined with a service path (e.g. 192.168.49.2/time) to see if the service work properly.

Automation: We automated steps 4-5 to make the deployment task less tedious.
Local deployment for minikube can be applied by using the ``./deployment.sh``
script by setting the TARGET to 'local'. This way it is not necessary to replace
all the placeholders set in the different YAMLs.

Note: at first it was our intention that ingress needs a specified host that's
why we set up ingress-dns by following this guide: [Ingress DNS](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/).
We configured our in-cluster dns to enable our enabling services to reach others
using ingress routing: [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/).
Later we found out that by dropping the 'host' entry in the ingress.yaml we can
just use the default cluster IP of minikube.
To get this IP you can run the following command:

```bash
minikube ip
```

Ingress for local deployment (ingress_local.yaml):
```yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
  name: discord-ingress
  namespace: k8s-discord
spec:
  rules:
  - http:
      paths:
      - backend:
          service:
            name: k8s-service-main
            port:
              number: 7000
        path: /register
        pathType: Prefix
      - backend:
          service:
            name: k8s-service-echo
            port:
              number: 8080
        path: /echo
        pathType: Prefix
      - backend:
          service:
            name: k8s-service-math
            port:
              number: 8080
        path: /math
        pathType: Prefix
      - backend:
          service:
            name: k8s-service-time
            port:
              number: 8080
        path: /time
        pathType: Prefix
      - backend:
          service:
            name: k8s-service-binary
            port:
              number: 8080
        path: /binary
        pathType: Prefix
```
Looking at the above YAMl it can be noticed that we defined a path and a backend service for
and the corresponding port for each microservice that we want to access via our ingress controller.

Microservice deployment/service YAML:
```yml
apiVersion: v1
kind: Service
metadata:
  name: k8s-service-time
  namespace: k8s-discord
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
spec:
  selector:
    app: microservice-time
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 7002
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservice-time
  namespace: k8s-discord
spec:
  replicas: 1
  selector:
    matchLabels: 
      app: microservice-time

  template:
    metadata:
      labels:
        app: microservice-time
    spec:
      containers:              
        - name: microservice-time
          image: <DOCKER_USER>/microservices-time:<TAG>
          env:
            - name: INGRESS_HOST
              value: "http://<INGRESS_IP>/"
            - name: MICROSERVICE_PORT
              value: "7002"
          ports: 
            - containerPort: 7002
          readinessProbe:
            httpGet:
              path: /time/health
              port: 7002
            initialDelaySeconds: 5
            periodSeconds: 5
```
As you can see in the above yaml we created a (ClusterIP) service with a specific selector to identify the correct
deployment of the actual application. The deployment itself has a label that corresponds to the selector of the service.
For reference, we link to the [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
in the kubernetes documentation.

Two additional points of interest are the service annotation "cloud.google.com/neg: '{"ingress": true}'" and the
definition of a readinessProbe within our deployment. As both of them are more important for the deployment in gcloud
we will discuss this points in more detail within the next section.

# Deploying our architecture to gcloud

We decided to use ingress-gce instead of nginx-ingress for the deployment in the
gcloud GKE kubernetes cluster as the initial setup is easier.

Unfortunately, this decision lead to many drawbacks as ingress-gce is not as
straight-forward and doesn't provide an easy setup for features like path
rewrite. Another drawback is the documentation which in its size is quite good
however it lacks a clear structure which resulted in many hours wasted to find
out why something does not work as its intended. A particular good example for
this would be that nginx-ingress expects that the wired/linked service defined
in its configuration.

Provide a health check by offering a health resource as it's creating LoadBalancers (called backend services) for each of them.
If the health resource is not returning an HTTP 200 status code GKE considers the backend service as unhealthy and the ingress routing does not work.
The preferred setup is still unclear to us, however we got it working by
specifying readinessProbes for our deployments as described at
[ISSUE-20555](https://github.com/kubernetes/kubernetes/issues/20555#issuecomment-326058311).
First, we deployed our ingress-gce in an external manner (meaning it is publicly
accessible) as stated at
[Ingress for External HTTP(S) Load Balancing](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress-xlb).
However, this was inappropriate approach as there is also the option of setting
up an internal ingress, is a more concise for our use case as only
cluster-internal services (bot-command microservices) should have access.
However, the setup of an internal ingress is quite tricky as custom subnets have
to be specified within gcloud.
After some hours of tinkering we finally could manage to set it up internally as
 described at [Ingress for Internal HTTP(S) Load Balancing](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress-ilb).

## Setting up the environment for an internal ingress

1. create network:

```bash
gcloud compute networks create lb-network --subnet-mode=custom
```

2. create subnet for service backends:

```bash
gcloud compute networks subnets create backend-subnet \
    --network=lb-network \
    --range=10.1.2.0/24 \
    --region=europe-west4
```

3. create proxy-only-subnet for INTERNAL_HTTPS_LOAD_BALANCER:

```bash
gcloud compute networks subnets create proxy-only-subnet \
  --purpose=INTERNAL_HTTPS_LOAD_BALANCER \
  --role=ACTIVE \
  --region=us-west1 \
  --network=lb-network \
  --range=10.129.0.0/23
```

4. set up firewall rules:

```bash
gcloud compute firewall-rules create fw-allow-ssh \
    --network=lb-network \
    --action=allow \
    --direction=ingress \
    --target-tags=allow-ssh \
    --rules=tcp:22
```

```bash
gcloud compute firewall-rules create fw-allow-health-check \
    --network=lb-network \
    --action=allow \
    --direction=ingress \
    --source-ranges=130.211.0.0/22,35.191.0.0/16 \
    --target-tags=load-balanced-backend \
    --rules=tcp

```

```bash
gcloud compute firewall-rules create fw-allow-proxies \
  --network=lb-network \
  --action=allow \
  --direction=ingress \
  --source-ranges=source-range \
  --target-tags=load-balanced-backend \
  --rules=tcp:80,tcp:443,tcp:8080
```

5. set up cluster

```bash
gcloud container clusters create discord-cluster \
    --enable-ip-alias \
    --zone=europe-west4-b \
    --network=lb-network \
    --subnetwork=backend-subnet
```

6. setup of a static IP for the ingress (Reference: 
[Reserving a static internal IP address](https://cloud.google.com/compute/docs/ip-addresses/reserve-static-internal-ip-address)):
```
gcloud compute addresses create static-ingress-ip --region europe-west4 --subnet backend-subnet --addresses 10.1.2.10
```
NOTE: the static-ip name (in the above case static-ingress-ip) must be set as  the value of the 'kubernetes.io/ingress.regional-static-ip-name' within the ingress.yaml to ensure that the ip is actually set for the internal ingress. if the value contains a value the ingress will still be deployed but of course will not work.


## Deploying the internal ingress
The deployment steps for gcloud are similar to those of
1. Apply deployment/service YAMLs
2. Apply ingress YAML

We recommend using the deployment.sh script for gcloud as it prompts
for parameters that it set automatically in all the YAMLs.
It should also be noted that it is possible to deploy our architecture
by using GitHub Workflow.
Ingress for gcloud deployment (ingress_gcloud.yaml):
```yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: discord-ingress
  namespace: k8s-discord  
  annotations:
    kubernetes.io/ingress.class : "gce-internal"
    kubernetes.io/ingress.regional-static-ip-name: "static-ingress-ip" 
spec:
  rules:
    - http:
        paths:
          - path: /register
            pathType: ImplementationSpecific
            backend:
              service:
                name: k8s-service-main
                port:
                  number: 7000 
          - path: /echo
            pathType: ImplementationSpecific
            backend:
              service:
                name: k8s-service-echo 
                port:
                  number: 8080
          - path: /math
            pathType: ImplementationSpecific
            backend:
              service:
                name: k8s-service-math 
                port:
                  number: 8080
          - path: /time
            pathType: ImplementationSpecific
            backend:
              service:
                name: k8s-service-time
                port:
                  number: 8080
          - path: /binary
            pathType: ImplementationSpecific
            backend:
              service:
                name: k8s-service-binary
                port:
                  number: 8080
```
As we already did in the first section we want to provide a deeper understanding of the ingress yaml above.
In contrast to the YAML for the minikube deployment we can notice that the ingress metadata contains
two additional annotations:
- kubernetes.io/ingress.class : "gce-internal"
- kubernetes.io/ingress.regional-static-ip-name: "static-ingress-ip"

The 'ingress.class' annotations states that GKE should create an ingress controller for cluster internal usage and the 
'ingress.regional-static-ip-name' annotation specifies which gcloud address should be used as a static address for the ingress instance.

In addition, also the PathType of the defined paths changed from Prefix to ImplementationSpecific this is a must-have
if you want to use the gce-ingress.

We also want to refer to the deployment/service yaml of the first section and go into more detail about the following subjects:
- cloud.google.com/neg annotation
- readinessProbe

As a gce-internal requires the service backends to be NEGs the following annotation is needed in the deployment/serivce YAML:
```yml
  ...
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
  ...
```
For more detail on why this is necessary we want to refer to the following documentation: [Deploying a Service as a Network End Group](https://cloud.google.com/kubernetes-engine/docs/how-to/internal-load-balance-ingress#deploy-service)

As already stated in the introduction of this section GKE is in the need of a health endpoint for each service/application.
For more information have a look on this page of the kubernetes documentation: [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)