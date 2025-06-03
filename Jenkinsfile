// Jenkinsfile (modified to use Secret File credential for GCP and address security warning)
pipeline {
    agent any

    environment {
        // --- GCP Configuration ---
        // Replace with your actual GCP Project ID
        GCP_PROJECT_ID = 'cts08-avadhootb-projs' // <--- **IMPORTANT: REPLACE WITH YOUR ACTUAL PROJECT ID**
        
        // Artifact Registry Repository URL.
        ARTIFACT_REGISTRY_REPO_URL = "us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/my-flask-images"

        // GKE Cluster details
        GKE_CLUSTER_NAME = "my-flask-cluster"
        GKE_CLUSTER_ZONE = "us-central1-a"

        // --- Application & Image Configuration ---
        IMAGE_NAME = "simple-login-app"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        FULL_IMAGE_NAME = "${ARTIFACT_REGISTRY_REPO_URL}/${IMAGE_NAME}:${IMAGE_TAG}"

        // Kubernetes Manifests paths
        KUBE_DEPLOYMENT_FILE = "kubernetes/deployment.yaml"
        KUBE_SERVICE_FILE = "kubernetes/service.yaml"
        
        // --- Jenkins Credential IDs ---
        GITHUB_CREDENTIALS_ID = '0442d698-3345-48d7-89ad-fc48b5cbc43b' 
        // Credential ID for your Google Service Account JSON Key (Type: Secret File)
        GCP_SERVICE_ACCOUNT_JSON_KEY_ID = 'gcp-service-account-json-key' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: "${GITHUB_CREDENTIALS_ID}", url: 'https://github.com/AvadhootB99/test2-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Use 'file()' binding for the Secret File credential
                    // Use a new, secure variable name for clarity and security.
                    withCredentials([file(credentialsId: "${GCP_SERVICE_ACCOUNT_JSON_KEY_ID}", variable: 'GCP_SA_KEY_FILE_PATH_SECURE')]) {
                        // Activate the service account using the path to the temporary file
                        // The variable is now securely passed and properly referenced.
                        sh "gcloud auth activate-service-account --key-file=\"${GCP_SA_KEY_FILE_PATH_SECURE}\""
                        
                        // Configure Docker to use gcloud credentials for Artifact Registry
                        def registryHostname = ARTIFACT_REGISTRY_REPO_URL.split('/')[0]
                        sh "gcloud auth configure-docker ${registryHostname}"
                        
                        // Build the Docker image
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
                    // Authenticate kubectl to the GKE cluster using the service account key file
                    withCredentials([file(credentialsId: "${GCP_SERVICE_ACCOUNT_JSON_KEY_ID}", variable: 'GCP_SA_KEY_FILE_PATH_SECURE_GKE')]) {
                        // Use a different variable name here if preferred, or reuse if scope allows.
                        // For clarity, I've used a slightly different one, but it's optional.
                        sh "gcloud config set project ${GCP_PROJECT_ID}"
                        
                        // Ensure gcloud uses the activated service account for cluster auth
                        sh "gcloud auth activate-service-account --key-file=\"${GCP_SA_KEY_FILE_PATH_SECURE_GKE}\""
                        sh "gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --zone ${GKE_CLUSTER_ZONE} --project ${GCP_PROJECT_ID}"
                    }

                    // Dynamic Image Tag Replacement
                    sh "sed -i.bak 's|${ARTIFACT_REGISTRY_REPO_URL}/${IMAGE_NAME}:9|${FULL_IMAGE_NAME}|g' ${KUBE_DEPLOYMENT_FILE}"
                    
                    // Apply Kubernetes manifests
                    sh "kubectl apply -f ${KUBE_DEPLOYMENT_FILE}"
                    sh "kubectl apply -f ${KUBE_SERVICE_FILE}"
                }
            }
        }

        stage('Clean Up Local Docker Image') {
            steps {
                script {
                    sh "docker rmi ${FULL_IMAGE_NAME}"
                }
            }
        }
    }

    post {
        always {
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