// Jenkinsfile
pipeline {
    agent any

    environment {
        // Replace with your GCP Project ID
        GCP_PROJECT_ID = 'cts08-avadhootb-projs' // CORRECTED: Use your actual Project ID
        // Replace with your desired Artifact Registry repository (e.g., us-central1-docker.pkg.dev/your-gcp-project-id/my-flask-images)
        GCR_IMAGE_REPO = "us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/my-flask-images" // Using Artifact Registry
        // For Google Container Registry (GCR), it would be:
        // GCR_IMAGE_REPO = "gcr.io/${GCP_PROJECT_ID}"

        IMAGE_NAME = "simple-login-app"
        IMAGE_TAG = "${env.BUILD_NUMBER}" // Use Jenkins build number for unique tags
        FULL_IMAGE_NAME = "${GCR_IMAGE_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
        KUBE_DEPLOYMENT_FILE = "kubernetes/deployment.yaml"
        KUBE_SERVICE_FILE = "kubernetes/service.yaml"
        GKE_CLUSTER_NAME = "my-flask-cluster" // Your GKE cluster name
        GKE_CLUSTER_ZONE = "us-central1-a" // Zone where your GKE cluster is located
        GKE_CLUSTER_REGION = "us-central1" // Region for regional clusters, or often inferrable from zone
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Ensure this credential ID is correctly configured in Jenkins with access to your GitHub repo
                git branch: 'main', credentialsId: '0442d698-3345-48d7-89ad-fc48b5cbc43b', url: 'https://github.com/AvadhootB99/test2-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Authenticate Docker to GCR/Artifact Registry using the service account
                    // 'gke-serviceaccount-jenkins' should be the ID of your Google Service Account Key credential in Jenkins.
                    withCredentials([googleServiceAccountKey('gke-serviceaccount-jenkins')]) {
                        // The GOOGLE_APPLICATION_CREDENTIALS environment variable is automatically set by withCredentials
                        // gcloud auth activate-service-account is not typically needed here as `gcloud auth configure-docker`
                        // will use the application default credentials established by the Google Cloud Oauth plugin via withCredentials.
                        // However, if you explicitly need it for other gcloud commands, it can be useful.
                        // sh "gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}"

                        // Authenticate Docker for Artifact Registry.
                        // For Artifact Registry, the hostname needs to be extracted correctly.
                        // Example: us-central1-docker.pkg.dev
                        def registryHostname = GCR_IMAGE_REPO.split('/')[0] // Extracts "us-central1-docker.pkg.dev" or "gcr.io"
                        sh "gcloud auth configure-docker ${registryHostname}"
                    }
                    // Ensure the Docker daemon is running and the Jenkins user has permissions to run docker commands.
                    // This often means the Jenkins user needs to be part of the 'docker' group.
                    sh "docker build -t ${FULL_IMAGE_NAME} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Docker push also requires authentication, which was done in the previous stage.
                    sh "docker push ${FULL_IMAGE_NAME}"
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                script {
                    // Authenticate kubectl to the GKE cluster using the service account
                    withCredentials([googleServiceAccountKey('gke-serviceaccount-jenkins')]) {
                        // gcloud auth activate-service-account is not typically needed here.
                        // The get-credentials command handles authentication using the established credentials.
                        // sh "gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}"

                        sh "gcloud config set project ${GCP_PROJECT_ID}"
                        // Using --zone for zonal clusters, or --region for regional clusters
                        sh "gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --zone ${GKE_CLUSTER_ZONE} --project ${GCP_PROJECT_ID}"
                    }

                    // IMPORTANT: The sed command for replacing the image tag
                    // Make sure the original image path in your deployment.yaml exactly matches what you are searching for.
                    // If your deployment.yaml has `simple-login-app:latest` initially, the sed command needs to reflect that.
                    // It's safer to use a placeholder in your YAML and replace it dynamically.
                    // For example, in your deployment.yaml, use: image: us-central1-docker.pkg.dev/YOUR_PROJECT_ID/my-flask-images/simple-login-app:BUILD_IMAGE_TAG
                    // Then you would replace BUILD_IMAGE_TAG.
                    // For now, assuming your current deployment.yaml has a fixed latest tag you want to replace:
                    sh "sed -i 's|us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/my-flask-images/simple-login-app:latest|${FULL_IMAGE_NAME}|g' ${KUBE_DEPLOYMENT_FILE}"

                    // Apply Kubernetes manifests
                    sh "kubectl apply -f ${KUBE_DEPLOYMENT_FILE}"
                    sh "kubectl apply -f ${KUBE_SERVICE_FILE}"
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    // Optional: Clean up local Docker images if needed
                    sh "docker rmi ${FULL_IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            // Optional: Send notifications (e.g., Slack, email)
            echo "Pipeline finished for build ${env.BUILD_NUMBER}"
        }
        success {
            echo "Deployment successful!"
        }
        failure {
            echo "Deployment failed! Check logs."
        }
    }
}