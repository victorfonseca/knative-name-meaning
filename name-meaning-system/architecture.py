from diagrams import Diagram, Cluster
from diagrams.k8s.compute import Pod, Deploy
from diagrams.k8s.network import Service, Ingress
from diagrams.programming.framework import FastAPI
from diagrams.onprem.queue import RabbitMQ

with Diagram("Knative Name Meaning System Architecture", show=False, direction="LR"):
    with Cluster("Kubernetes Cluster"):
        # Knative Layer
        with Cluster("Knative Serving"):
            knative_svc = Service("name-lookup-api")
            ingress = Ingress("Knative Ingress")
            
        # Application Components
        with Cluster("Application Services"):
            api = FastAPI("Name Lookup API")
            api_pod = Pod("API Pod")
            
            with Cluster("RabbitMQ"):
                queue = RabbitMQ("name_meanings")
                rabbitmq_svc = Service("rabbitmq-service")
                rabbitmq_pod = Pod("rabbitmq-pod")
                
                rabbitmq_pod - rabbitmq_svc - queue
            
            with Cluster("Consumer"):
                consumer_deploy = Deploy("name-meaning-consumer")
                consumer_pod = Pod("Consumer Pod")
                
        # Flow
        ingress >> knative_svc >> api >> api_pod
        api_pod >> rabbitmq_svc
        queue >> consumer_pod
        consumer_deploy >> consumer_pod
