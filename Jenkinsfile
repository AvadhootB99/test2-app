// Jenkinsfile
pipeline {
    agent any // Consider 'agent { docker { image 'your-custom-build-image' } }' for isolated builds with pre-installed tools

    environment {
        // --- GCP Configuration ---
        // Replace with your actual GCP Project ID
        GCP_PROJECT_ID = 'project_id' // <--- **IMPORTANT: REPLACE WITH YOUR ACTUAL PROJECT ID**
        
        // Artifact Registry Repository URL. This should point to your Docker repository.
        // Format: <LOCATION>-docker.pkg.dev/<PROJECT_ID>/<REPOSITORY_NAME>
        // Make sure 'my-flask-images' is the actual name of your Artifact Registry Docker repository
        ARTIFACT_REGISTRY_REPO_URL = "us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/my-flask-images"

        // GKE Cluster details
        GKE_CLUSTER_NAME = "my-flask-cluster" // Your GKE cluster name
        GKE_CLUSTER_ZONE = "us-central1-a"   // Zone where your GKE cluster is located (for zonal clusters)
        // GKE_CLUSTER_REGION = "us-central1" // Use this for regional clusters instead of GKE_CLUSTER_ZONE

        // --- Application & Image Configuration ---
        IMAGE_NAME = "simple-login-app"
        IMAGE_TAG = "${env.BUILD_NUMBER}" // Use Jenkins build number for unique tags
        FULL_IMAGE_NAME = "${ARTIFACT_REGISTRY_REPO_URL}/${IMAGE_NAME}:${IMAGE_TAG}"

        // Kubernetes Manifests paths (relative to your repository root)
        KUBE_DEPLOYMENT_FILE = "kubernetes/deployment.yaml"
        KUBE_SERVICE_FILE = "kubernetes/service.yaml"
        
        // --- Jenkins Credential IDs ---
        // Credential ID for your GitHub repository (e.g., Personal Access Token or SSH key)
        GITHUB_CREDENTIALS_ID = '0442d698-3345-48d7-89ad-fc48b5cbc43b' 
        // Credential ID for your Google Service Account Key (Type: Google Service Account from private key)
        GCP_SERVICE_ACCOUNT_CREDENTIALS_ID = 'my-jenkins-sa' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Ensure the credential ID is correctly configured in Jenkins with access to your GitHub repo
                // Always use the defined variable for URL and credentials for clarity and easier updates.
                git branch: 'main', credentialsId: "${GITHUB_CREDENTIALS_ID}", url: 'https://github.com/AvadhootB99/test2-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Authenticate Docker to Artifact Registry using the Google Service Account
                    // The 'googleServiceAccountKey' binding automatically sets GOOGLE_APPLICATION_CREDENTIALS
                    withCredentials([googleServiceAccountKey("${GCP_SERVICE_ACCOUNT_CREDENTIALS_ID}")]) {
                        // Extract just the hostname for `gcloud auth configure-docker`
                        def registryHostname = ARTIFACT_REGISTRY_REPO_URL.split('/')[0]
                        sh "gcloud auth configure-docker ${registryHostname}"
                        
                        // Build the Docker image. Ensure your Dockerfile is in the current context ('.')
                        sh "docker build -t ${FULL_IMAGE_NAME} ."
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Docker push will use the authentication established in the previous stage.
                    sh "docker push ${FULL_IMAGE_NAME}"
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                script {
                    // Authenticate kubectl to the GKE cluster using the service account
                    withCredentials([googleServiceAccountKey("${GCP_SERVICE_ACCOUNT_CREDENTIALS_ID}")]) {
                        sh "gcloud config set project ${GCP_PROJECT_ID}"
                        
                        // Get Kubeconfig credentials for the cluster.
                        // Use --zone for zonal clusters, or --region for regional clusters.
                        // Based on your GKE_CLUSTER_ZONE, it's a zonal cluster, so --zone is correct.
                        sh "gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --zone ${GKE_CLUSTER_ZONE} --project ${GCP_PROJECT_ID}"
                    }

                    // --- Dynamic Image Tag Replacement ---
                    // IMPORTANT: Create a placeholder in your deployment.yaml for the image tag.
                    // Example in kubernetes/deployment.yaml:
                    // image: us-central1-docker.pkg.dev/project_id/my-flask-images/simple-login-app:BUILD_TAG_PLACEHOLDER
                    // Then the sed command will replace this placeholder.
                    // This is more robust than replacing a fixed 'latest' tag.
                    // Ensure your deployment.yaml is committed with this placeholder.
                    
                    // sed -i requires a backup suffix on some systems (like macOS). For Linux, '' is fine.
                    // Using `.` after -i is a common trick to make it work on both.
                    sh "sed -i.bak 's|BUILD_TAG_PLACEHOLDER|${IMAGE_TAG}|g' ${KUBE_DEPLOYMENT_FILE}"
                    
                    // Apply Kubernetes manifests.
                    // Ensure the 'kubectl' command is available on your Jenkins agent.
                    sh "kubectl apply -f ${KUBE_DEPLOYMENT_FILE}"
                    sh "kubectl apply -f ${KUBE_SERVICE_FILE}"
                }
            }
        }

        stage('Clean Up Local Docker Image') {
            steps {
                script {
                    // Clean up the local Docker image to free up space on the Jenkins agent.
                    sh "docker rmi ${FULL_IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
            // Clean up the workspace to ensure a fresh start for the next build.
            cleanWs()
            echo "Pipeline finished for build ${env.BUILD_NUMBER}"
        }
        success {
            echo "Deployment successful!"
        }
        failure {
            echo "Deployment failed! Check logs."
        }
        unstable {
            echo "Pipeline was unstable, check test results."
        }
        aborted {
            echo "Pipeline was aborted."
        }
    }
}