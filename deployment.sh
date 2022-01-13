# TODO: azure, gke
# TODO: fix sed replacement issue with ingress host string
# add variable CLUSTER_IP
echo "Enter deplyoment TARGET (local|gcloud)"
read TARGET

# SET KUBECTL CONTEXT TO GCLOUD CLUSTER
echo "Enter K8S_CLUSTER_CONTEXT GKE cluster for kubectl:"
read K8s_CLUSTER_CONTEXT

kubectx $K8S_CLUSTER_CONTEXT 

# INIT VARIABLES
echo "Enter docker user:"
read DOCKER_USER

echo "Enter current TAG:"
read TAG

kubectl create namespace k8s-discord


#echo "Enter STATIC_INGRESS_IP:"
#read STATIC_INGRESS_IP

echo "Enter INGRESS_HOST (e.g. http://<INGRESS_HOST>)":
read INGRESS_HOST

echo "Enter DISCORD_TOKEN for your bot":
read DISCORD_TOKEN


echo "Enter BOT_COMMAND_PREFIX for your bot:"
read BOT_COMMAND_PREFIX


# CREATE MICROSERVICE YAML FILES
cd ./microservices
for d in */ ; do
    [ -L "${d%/}" ] && continue
    echo "replace placeholders for $d microservice.."
    sed "s/<TAG>/$TAG/g" "$d/deployment.yaml" > "$d/deployment_$TAG.yaml"
    sed -i "s/<DOCKER_USER>/$DOCKER_USER/g" "$d/deployment_$TAG.yaml"
    sed -i "s/<INGRESS_HOST>/$INGRESS_HOST/g" "$d/deployment_$TAG.yaml"
    sed -i "s/<DISCORD_TOKEN>/$DISCORD_TOKEN/g" "$d/deployment_$TAG.yaml"
    sed -i "s/<BOT_COMMAND_PREFIX>/$BOT_COMMAND_PREFIX/g" "$d/deployment_$TAG.yaml"
done


# CREATE MAIN MICROSERVICE IMAGE
docker image build -f ./main/Dockerfile -t k11810066/discord-bot:$TAG ./main
docker push k11810066/discord-bot:$TAG
# CREATE ECHO MICROSERVICE IMAGE
docker image build -f ./echo/Dockerfile -t k11810066/microservices-echo:$TAG ./echo
docker push k11810066/microservices-echo:$TAG
# CREATE MATH MICROSERVICE IMAGE
docker image build -f ./math/Dockerfile -t k11810066/microservices-math:$TAG ./math
docker push k11810066/microservices-math:$TAG
# CREATE TIME MICROSERVICE IMAGE
docker image build -f ./time/Dockerfile -t k11810066/microservices-time:$TAG ./time
docker push k11810066/microservices-time:$TAG
# CREATE BINARY MICROSERVICE IMAGE
mvn clean package -f ./binary/pom.xml
docker image build -f ./binary/Dockerfile -t k11810066/microservices-binary:$TAG ./binary
docker push k11810066/microservices-binary:$TAG

# DELETE MICROSERVICE DEPLOYMENTS
kubectl delete deployment discord-bot -n k8s-discord
kubectl delete deployment microservice-echo -n k8s-discord
kubectl delete deployment microservice-time -n k8s-discord
kubectl delete deployment microservice-math -n k8s-discord
kubectl delete deployment microservice-binary -n k8s-discord

# APPLY MICROSERVICE DEPLOYMENTS
kubectl apply -f "./main/deployment_$TAG.yaml" -n k8s-discord
sleep 60s # timeout for terminating pods
kubectl apply -f "./echo/deployment_$TAG.yaml" -n k8s-discord
kubectl apply -f "./math/deployment_$TAG.yaml" -n k8s-discord
kubectl apply -f "./time/deployment_$TAG.yaml" -n k8s-discord
kubectl apply -f "./binary/deployment_$TAG.yaml" -n k8s-discord


cd ..
# APPLY INGRESS          
sed "s/<INGRESS_HOST>/$INGRESS_HOST/g" "./ingress_$TARGET.yaml" > "./ingress_$TARGET_$TAG.yaml"
kubectl apply -f "./ingress_$TARGET_$TAG.yaml" -n k8s-discord
# CLEANUP INGRES YAML
rm "./ingress_$TARGET_$TAG.yaml"

kubectl get ingress discord-ingress -n k8s-discord


# CLEANUP YAML FILES

cd ./microservices
for d in */ ; do
    [ -L "${d%/}" ] && continue
    rm "$d/deployment_$TAG.yaml"
done

# OUTPUT INFORMATION
kubectl get pods -n k8s-discord
