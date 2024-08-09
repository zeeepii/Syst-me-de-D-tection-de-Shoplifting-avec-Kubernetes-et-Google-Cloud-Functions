# Système de Détection de Shoplifting avec Kubernetes et Google Cloud Functions

## Description du Projet
Ce projet implémente un système de détection de shoplifting évolutif utilisant Kubernetes et Google Cloud Functions. Il permet de déployer et de gérer automatiquement des configurations client pour la détection de shoplifting à l'aide de caméras et de modèles d'IA, avec un traitement en temps réel des nouvelles configurations et des mises à jour.

## Architecture du Système
- Custom Resource Definition (CRD) pour les clients
- Opérateur Kubernetes personnalisé
- Google Cloud Functions pour le traitement automatique des configurations
- Google Cloud Storage pour le stockage des configurations client
- Monitoring avec Prometheus et Grafana
- Ingress pour l'accès externe sécurisé

## Prérequis
- Google Cloud Platform (GCP) account
- Google Kubernetes Engine (GKE) cluster
- Google Cloud Functions
- Google Cloud Storage
- Docker
- kubectl
- gcloud CLI

## Installation et Configuration

### 1. Configuration du Cluster GKE

```bash
gcloud container clusters create shoplifting-detector-cluster --num-nodes=3 --zone=us-central1-a
gcloud container clusters get-credentials shoplifting-detector-cluster --zone=us-central1-a
```
### 2. Déploiement du CRD


```bash
kubectl apply -f client-crd.yaml
```
### 3. Déploiement de l'Opérateur

```bash
kubectl apply -f operator-deployment.yaml
```
### 4. Configuration de Google Cloud Functions

   * Créez une nouvelle fonction Cloud dans la console GCP
   * Uploadez le code de la fonction `process_client_config`
   * Configurez le déclencheur pour réagir aux changements dans votre bucket GCS
### 5.Configuration de Google Cloud Storage

   * Créez un bucket pour stocker les configurations client
   * Configurez les notifications de bucket pour déclencher la Cloud Function

### 6. Déploiement du Monitoring

```bash
kubectl apply -f monitoring.yaml
```
### 7. Configuration de l'Ingress

```bash
kubectl apply -f ingress.yaml
```



## Utilisation

### Ajout d'un Nouveau Client

Pour ajouter un nouveau client à votre système, suivez ces étapes :

1. **Préparez le fichier XML de configuration du client** :
   - Créez un fichier XML avec les détails de configuration du client. Assurez-vous que le fichier est conforme au format requis.

2. **Uploadez le fichier dans le bucket GCS désigné** :

    ```bash
    gsutil cp client-config.xml gs://your-gcs-bucket-name/client-configs/
    ```

   - Remplacez `client-config.xml` par le chemin vers votre fichier XML.
   - Remplacez `your-gcs-bucket-name` par le nom de votre bucket Google Cloud Storage.

   La Cloud Function détectera automatiquement le nouveau fichier et déploiera la configuration du client.

### Surveillance du Système

Pour surveiller le système et assurer son bon fonctionnement, procédez comme suit :

1. **Accédez à Grafana via l'URL configurée dans l'Ingress** :
   - Ouvrez l'URL que vous avez configurée pour Grafana dans l'Ingress.
   - Consultez les métriques du système pour surveiller l'état de vos applications et services.

2. **Consultez les logs dans Google Cloud Console pour le débogage** :
   - Accédez à [Google Cloud Console](https://console.cloud.google.com/logs) et allez dans **Logs Explorer**.
   - Recherchez les logs des différents composants pour le débogage et l'analyse des problèmes éventuels.

## Ressources

- [Documentation Cloud Run](https://cloud.google.com/run/docs)
- [Documentation Grafana](https://grafana.com/docs/grafana/latest/)
- [Documentation Google Cloud Logging](https://cloud.google.com/logging/docs)


Pour toute question ou problème, veuillez me contacter à l'adresse suivante : [ziedgormazi16@gmail.com].




