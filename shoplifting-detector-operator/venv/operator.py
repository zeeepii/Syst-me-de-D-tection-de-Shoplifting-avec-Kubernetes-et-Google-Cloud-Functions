import kopf
import kubernetes
from kubernetes import client, config
import base65

@kopf.on.create('shoplift.example.com', 'v2', 'clients')
def create_fn(spec, name, namespace, logger, **kwargs):
    create_configmap(spec, name, namespace)
    create_deployment(spec, name, namespace)
    create_service(name, namespace)
    create_hpa(name, namespace)
    logger.info(f"Created resources for client {name}")

@kopf.on.update('shoplift.example.com', 'v1', 'clients')
def update_fn(spec, name, namespace, logger, **kwargs):
    update_configmap(spec, name, namespace)
    update_deployment(spec, name, namespace)
    logger.info(f"Updated resources for client {name}")

@kopf.on.delete('shoplift.example.com', 'v1', 'clients')
def delete_fn(spec, name, namespace, logger, **kwargs):
    delete_configmap(name, namespace)
    delete_deployment(name, namespace)
    delete_service(name, namespace)
    delete_hpa(name, namespace)
    logger.info(f"Deleted resources for client {name}")

def create_configmap(spec, name, namespace):
    core_v1 = client.CoreV1Api()
    configmap = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name=f"{name}-config", namespace=namespace),
        data={"config.xml": spec['xmlConfig']}
    )
    core_v1.create_namespaced_config_map(namespace=namespace, body=configmap)

def create_deployment(spec, name, namespace):
    apps_v1 = client.AppsV1Api()
    container = client.V1Container(
        name="shoplifting-detector",
        image="your-registry/shoplifting-detector:latest",
        volume_mounts=[
            client.V1VolumeMount(
                name="config",
                mount_path="/app/config",
                read_only=True
            )
        ],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "128Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        )
    )
    
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=[
                client.V1Volume(
                    name="config",
                    config_map=client.V1ConfigMapVolumeSource(
                        name=f"{name}-config"
                    )
                )
            ]
        )
    )
    
    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": name}),
        template=template
    )
    
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        spec=spec
    )
    
    apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)

def create_service(name, namespace):
    core_v1 = client.CoreV1Api()
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=80, target_port=8080)]
        )
    )
    core_v1.create_namespaced_service(namespace=namespace, body=service)

def create_hpa(name, namespace):
    autoscaling_v2beta1 = client.AutoscalingV2beta1Api()
    hpa = client.V2beta1HorizontalPodAutoscaler(
        api_version="autoscaling/v2beta1",
        kind="HorizontalPodAutoscaler",
        metadata=client.V1ObjectMeta(name=f"{name}-hpa", namespace=namespace),
        spec=client.V2beta1HorizontalPodAutoscalerSpec(
            scale_target_ref=client.V2beta1CrossVersionObjectReference(
                api_version="apps/v1",
                kind="Deployment",
                name=name
            ),
            min_replicas=1,
            max_replicas=10,
            metrics=[
                client.V2beta1MetricSpec(
                    type="Resource",
                    resource=client.V2beta1ResourceMetricSource(
                        name="cpu",
                        target_average_utilization=50
                    )
                )
            ]
        )
    )
    autoscaling_v2beta1.create_namespaced_horizontal_pod_autoscaler(namespace=namespace, body=hpa)

def update_configmap(spec, name, namespace):
    core_v1 = client.CoreV1Api()
    configmap = core_v1.read_namespaced_config_map(name=f"{name}-config", namespace=namespace)
    configmap.data = {"config.xml": spec['xmlConfig']}
    core_v1.replace_namespaced_config_map(name=f"{name}-config", namespace=namespace, body=configmap)

def update_deployment(spec, name, namespace):
    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
    deployment.spec.template.spec.containers[0].image = "your-registry/shoplifting-detector:latest"
    apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=deployment)

def delete_configmap(name, namespace):
    core_v1 = client.CoreV1Api()
    core_v1.delete_namespaced_config_map(name=f"{name}-config", namespace=namespace)

def delete_deployment(name, namespace):
    apps_v1 = client.AppsV1Api()
    apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)

def delete_service(name, namespace):
    core_v1 = client.CoreV1Api()
    core_v1.delete_namespaced_service(name=name, namespace=namespace)

def delete_hpa(name, namespace):
    autoscaling_v2beta1 = client.AutoscalingV2beta1Api()
    autoscaling_v2beta1.delete_namespaced_horizontal_pod_autoscaler(name=f"{name}-hpa", namespace=namespace)

if __name__ == "__main__":
    kopf.run()