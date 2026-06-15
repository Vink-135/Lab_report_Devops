pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'lab-portal'
        DOCKER_TAG = "build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker Image..."
                    sh "/usr/local/bin/docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Verify Build') {
            steps {
                script {
                    echo "Verifying Docker Image..."
                    // Simple validation to ensure python files compile successfully inside the container
                    sh "/usr/local/bin/docker run --rm ${DOCKER_IMAGE}:latest python -m py_compile app.py models.py"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully. Image ${DOCKER_IMAGE}:${DOCKER_TAG} is ready!"
        }
        failure {
            echo "Pipeline failed! Please check the build logs."
        }
    }
}
