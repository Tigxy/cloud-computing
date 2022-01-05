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

## Trying it out in google cloud
TODO:Setting it up in the google cloud
