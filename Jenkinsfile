// Jenkinsfile
pipeline {
    agent any

    environment {
        // Replace with your GCP Project ID
        GCP_PROJECT_ID = 'cts08-avadhootb-projs'
        // Replace with your desired Docker image repository (e.g., us-central1-docker.pkg.dev/your-gcp-project-id/my-flask-images)
       
        GCR_IMAGE_REPO = "us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/my-flask-images"

        IMAGE_NAME = "simple-login-app"
        IMAGE_TAG = "${env.BUILD_NUMBER}" // Use Jenkins build number for unique tags
        FULL_IMAGE_NAME = "${GCR_IMAGE_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
        KUBE_DEPLOYMENT_FILE = "kubernetes/deployment.yaml"
        KUBE_SERVICE_FILE = "kubernetes/service.yaml"
        GKE_CLUSTER_NAME = "my-flask-cluster" // Your GKE cluster name
        GKE_CLUSTER_ZONE = "us-central1-a" // Zone where your GKE cluster is located
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: '0442d698-3345-48d7-89ad-fc48b5cbc43b',  url: 'https://github.com/AvadhootB99/test2-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Authenticate Docker to GCR/Artifact Registry using the service account
                    // Assuming you have 'gcp-service-account' credential ID set up
                    withCredentials([file(credentialsId: 'new-service-id', variable: 'MY_KEY')]) {
                        sh "gcloud auth activate-service-account --key-file=${MY_KEY}"
                        sh "gcloud auth configure-docker ${GCR_IMAGE_REPO.split('/')[0]}" // Authenticate the correct registry hostname
                    }
                    sh "docker build -t ${FULL_IMAGE_NAME} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh "docker push ${FULL_IMAGE_NAME}"
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                script {
                    // Authenticate kubectl to the GKE cluster using the service account
                    withCredentials([file(credentialsId: 'new-service-id', variable: 'MY_KEY')]) {
                        sh "gcloud auth activate-service-account --key-file=${MY_KEY}"
                        sh "gcloud config set project ${GCP_PROJECT_ID}"
                        sh "gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --zone ${GKE_CLUSTER_ZONE} --project ${GCP_PROJECT_ID}"
                    }

                    // Replace the image tag in the deployment file
                    sh "sed -i 's|us-central1-docker.pkg.dev/cts08-avadhootb-projs/my-flask-images/simple-login-app:latest|${FULL_IMAGE_NAME}|g' ${KUBE_DEPLOYMENT_FILE}"

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

