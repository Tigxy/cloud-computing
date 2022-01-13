# Using an ingress controller for routing rules
TODO: needs some rewording

In order to decouple the routing from our main service, we decided to use an ingress controller for mapping commands to specific routing rules.

For our architecture we decided to combine ingress, multiple cluster-ip services to expose the deployments to the ingress controller and therefore to our main application.

Due to the usage of ingress-dns we enable our microservices to address their REST calls to a central host (e.g. http://discord.test/) and all the needed routing is handled by the ingress.

Additional notes:

Ingress: the rewrite option can be quite useful for simplicity, we omitted this for our use case

Service: the specified targetPort must match the port of the corresponding deployment.

Example ingress.yaml
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: discord-ingress
  namespace: k8s-discord  
  annotations:
     nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: discord.test
      http:
        paths:
          - path: /register
            pathType: Prefix
            backend:
              service:
                name: k8s-service-main
                port:
                  number: 7000 
          - path: /echo
            pathType: Prefix
            backend:
              service:
                name: k8s-service-echo 
                port:
                  number: 8080
          - path: /math
            pathType: Prefix
            backend:
              service:
                name: k8s-service-math 
                port:
                  number: 8080
          - path: /time
            pathType: Prefix
            backend:
              service:
                name: k8s-service-time
                port:
                  number: 8080
```

## Trying it out locally with minikube:
1. enable the ingress addon with: minikube addons enable ingress
2. enable the ingress-dns addon with: minikube addons enable ingress-dns
3. setup ingress-dns by following this guide: https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/ 
4. configure in-cluster dns for enabling services to reach others using ingress https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/
5. apply the deployment.yaml for each microservice
6. apply the service.yaml for each microservice
7. apply the ingress.yaml

Note: steps 4-6 can be applied by using ``./local_deployment.sh``

## Trying it out in gcloud
TODO: point out differences
TODO: make script easier and set up GitHub workflow


note: HttpLoadBalancing must be enabled on your cluster
gcloud container clusters update cluster --update-addons=HttpLoadBalancing=ENABLED



In order to expose our ingress externally we have to create an address within gcloud:
gcloud compute addresses create ingress-address     --region europe-west4

The actual registered address can then later be listed in the following way:
gcloud compute addresses list

The corresponding ingress-address should later be used in our github actions workflow or deployment script.

We decided to use ingress-gce instead of nginx-ingress for the deployment in the gcloud GKE kubernetes cluster as the initial setup is easier.
Unfortunately, this decision lead to many drawbacks as ingress-gce is not as straight-forward and doesn't provide an easy setup for features like path rewrite.
Another drawback is the documentation which in its size is quite good however it lacks a clear structure which resulted in many hours wasted to find out why something does not work as its intended.
A particular good example for this would be that nginx-ingress expects that the wired/linked service defined in its configuration
provide a health check by offering a health resource as it's creating LoadBalancers (called backend services) for each of them.
If the health resource is not returning an HTTP 200 status code GKE considers the backend service as unhealthy and the ingress routing does not work.
The preferred setup is still unclear to us, however we got it working by specifying readinessProbes for our deployments as described at https://github.com/kubernetes/kubernetes/issues/20555#issuecomment-326058311.\
Currently, we deployed our ingress-gce in an external way (meaning it is publicly accessible) as stated at https://cloud.google.com/kubernetes-engine/docs/concepts/ingress-xlb.
There is also a way of setting it up for internal usage only, which would be more appropriate for our use case as only cluster internal services (command-microservices) should have access.
However, the setup of an internal ingress is quite complex as custom subnets have to be created/specified within gcloud.
After some hours of tinkering we gave up on setting it up internally as it had become to time-consuming for the scope of this project.
For reference, we still want to link the according documentation on setting up an internal ingress: https://cloud.google.com/kubernetes-engine/docs/concepts/ingress-ilb.\


```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: discord-ingress
  namespace: k8s-discord  
  annotations:
    kubernetes.io/ingress.class : "gce"
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
