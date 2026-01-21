# Docker file

A docker file is like a recipe. We use it to build an image. The docker file used is as follows:

FROM python:3.14.2-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hotel_bookings.csv .
COPY clean_data.py .
CMD [ "python", "clean_data.py" ]

FROM pulls python from the docker hub. Slim is chosen because it is light weight but still has enough to support the dependancies needed eg: Pandas.
WORKDIR -> cd's into the container directory creating it first if it does not exist.
COPY -> This is used to copy files from local machine to container.

A 2 step COPY is used because of caching. We do not want a full rebuild if only contents of clean_data.py change.
We use --no-cache-dir to navigate around pip's behaviour of saving library install files. This cuts down on space.
CMD -> This is used to define the deafult start up command that can be overwritten.

## Build

To build the image run:

docker build -t image_name:image_tag


## Run

To run it is important to mount local machine's directory so that you can obtain the output from the machine.

That would look like:

docker run --rm -it -v $(pwd):/app hotel-bookings-cleaner:1.0 

Note: the --rm flag removes the container once the run is complete.
-it runs the container in interactive mode so that it can accept command line user inputs
-v: used to mount in our case $(pwd) the current directory to the output directory of the container (/app) 



# Docker compose
Docker compose automates what was done above. Also, we need to have a postgres instance so ensuring they are in the same network is 
also important for us.

The 'way' to start up docker compose is usually docker compose up, the only issue here is we are expecting user input so, instead of
starting it as we would do a server we should use: docker compose run 

Before this we need to docker compose build to build the image because run expects a container name ie:
docker compose run --rm cleaner 

Note. When running compose we can start individual services as we need in this case using the service name what I mean is:

services:
  cleaner:             # This is just a name you give the service
    build: .           # <--- THIS replaces 'docker build .'
    image: hotel-bookings-cleaner:2.0-compose  # Optional: names the image
    volumes:
      - .:/app         # Replaces '-v $(pwd):/app'
    stdin_open: true   # Replaces '-i' (Interactive)
    tty: true          # Replaces '-t' (Terminal)


In this case we would not use the image name rather, docker compose run --rm cleaner


# Python
The binary version of psycopg2 is used. This is not recommended for production environments. This is because of update purposes,
you can end up being stuck with a security vulnerability. Our app is low stakes I don't care.

# Kubernetes (k8s)
Kubernetes is used in deployment and management of containers. 

Kubernetes heirarchy (top down):
- Cluster
- Node
- Pod
- Container

The command to start a minikube cluster is: 
minikube start --driver=podman --container-runtime=containerd

By default this command creates a cluster named minikube. You can change this using: minikube start -p my-second-cluster\

--driver=podman is a Fedora thing. containerd is stable and prevents the api server crashing otherwise.


The default take down is delete service if it is exposed, delete deployement then stop the cluster.
If you need to restart the cluster use the command: minikube start -p <profile-name>


Kubernetes is replaces Docker Compose. Well, not replace but the use cases are different. Docker compose is used for single machine
whereas Kubernetes is to be used on top of a fleet of computers.

Kubernetes knows nothing about custom images. Kubernetes has images but those are completely different to docker images.
We can export image from docker and import it into kubernetes using the following command: docker save hotel-bookings-cleaner:2.0-compose | minikube image load -

We can list images on kubernetes using the commmand: minikube image ls

Kubernetes uses confige maps and secrets to store configs. The only difference is secrets are used to store confidential pieces of data.

We use yaml files to eliminate the need for use of the command line.

Once you are done writing the deployment, config map and secrets you can apply them individually in order as follows:

1. Configuration & Secrets
kubectl apply -f 02-db-secret.yaml
kubectl apply -f 03-etl-config.yaml

2. Networking
kubectl apply -f 01-db-service.yaml

3. Workloads (Database first, then App)
kubectl apply -f 04-postgres-deployment.yaml
kubectl apply -f 05-etl-deployment.yaml

or all together using:
kubectl apply -f directory-name


kubectl is used to interact with KUbernetes cluster via the command line. 
Sample commands include:
  - kubectl get deployments
  - kubectl get services
  - kubectl logs deployment-name
  - kubectl get pods

Use case example. A pod is crashing to get the logs you would run 
  - run kubectl get pods. 
  - copy pod name
  - run kubectl logs copied pod name



You can copy over data from pods to your local machine as follows:
kubectl cp etl-manager-xx-xxxxx:/app/hotel_bookings_duplicates.csv ./my_duplicates.csv

You can list items as follows:
kubectl exec etl-manager-xx-xxxxx -- ls -l /app



