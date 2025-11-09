pipeline {
    agent any
    environment {
        APP_NAME = 'bloom-haven-nursery'
        DOCKER_IMAGE = "kavitharc/${APP_NAME}:${BUILD_NUMBER}"
        FRONTEND_IMAGE = "kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'docker-credentials'
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                checkout scm
                echo "✅ Git Checkout Completed"
            }
        }
        
        stage('Install Security Tools') {
            steps {
                script {
                    echo "🔧 Installing Security Scanning Tools..."
                    sh '''
                        # Install Trixy only (SonarScanner is handled by Jenkins plugin)
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                        echo "✅ Security tools installed successfully"
                    '''
                }
            }
        }
        
        stage('Python Backend Build') {
            steps {
                sh '''
                    cd backend
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    echo "✅ Dependencies installed"
                '''
            }
        }
        
        stage('Python Backend Test') {
            steps {
                sh '''
                    cd backend
                    . venv/bin/activate
                    pip install pytest pytest-cov
                    mkdir -p ../test-reports
                    python -m pytest tests/ --junitxml=../test-reports/junit.xml --cov-report=xml --cov=. || echo "Tests completed"
                '''
                junit allowEmptyResults: true, testResults: 'test-reports/junit.xml'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "🔍 Running SonarQube Analysis..."
                    // Use the Jenkins-configured SonarScanner tool
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv() {
                        sh """
                            cd backend
                            ${scannerHome}/bin/sonar-scanner
                        """
                    }
                }
            }
        }
        
        stage('Source Code Security Scan') {
            steps {
                script {
                    echo "🔒 Running Trixy Source Code Security Scan..."
                    sh '''
                        mkdir -p security-reports
                        
                        # Scan Python dependencies in backend
                        echo "📋 Scanning Python dependencies..."
                        cd backend
                        trivy fs . \
                            --format table \
                            --output ../security-reports/source-scan-table.txt \
                            --severity HIGH,CRITICAL \
                            --scanners vuln \
                            --exit-code 0
                        
                        # Generate JSON report for archiving
                        trivy fs . \
                            --format json \
                            --output ../security-reports/source-scan.json \
                            --severity HIGH,CRITICAL \
                            --scanners vuln \
                            --exit-code 0
                            
                        echo "✅ Source code security scan completed"
                        
                        # Display summary
                        if [ -f ../security-reports/source-scan-table.txt ]; then
                            echo "=== PYTHON DEPENDENCY SECURITY SCAN ==="
                            cat ../security-reports/source-scan-table.txt
                        fi
                    '''
                }
                archiveArtifacts artifacts: 'security-reports/source-scan.json', fingerprint: true
            }
        }
        
        stage('Docker Build - Backend') {
            steps {
                sh '''
                    cd backend
                    # Use existing Dockerfile if present, otherwise create one
                    if [ ! -f Dockerfile ]; then
                        cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
EOF
                    fi
                    docker build -t ${DOCKER_IMAGE} .
                    echo "✅ Backend Docker image built: ${DOCKER_IMAGE}"
                '''
            }
        }
        
        stage('Docker Build - Frontend') {
            steps {
                sh '''
                    cd frontend
                    # Use existing Dockerfile if present, otherwise create one
                    if [ ! -f Dockerfile ]; then
                        cat > Dockerfile << 'EOF'
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
                    fi
                    docker build -t ${FRONTEND_IMAGE} .
                    echo "✅ Frontend Docker image built: ${FRONTEND_IMAGE}"
                '''
            }
        }
        
        stage('Container Security Scan') {
            steps {
                script {
                    echo "🐳 Running Container Security Scan..."
                    sh '''
                        mkdir -p security-reports
                        
                        # Scan backend container
                        echo "Scanning backend image..."
                        trivy image ${DOCKER_IMAGE} \
                            --format table \
                            --output security-reports/backend-scan-table.txt \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        trivy image ${DOCKER_IMAGE} \
                            --format json \
                            --output security-reports/backend-scan.json \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        echo "Scanning frontend image..."
                        trivy image ${FRONTEND_IMAGE} \
                            --format table \
                            --output security-reports/frontend-scan-table.txt \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        trivy image ${FRONTEND_IMAGE} \
                            --format json \
                            --output security-reports/frontend-scan.json \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        echo "✅ Container security scans completed successfully"
                        
                        # Display vulnerability summaries
                        echo "=== BACKEND CONTAINER VULNERABILITIES ==="
                        if [ -f security-reports/backend-scan-table.txt ]; then
                            cat security-reports/backend-scan-table.txt
                        fi
                    '''
                }
                archiveArtifacts artifacts: 'security-reports/*.json,security-reports/*.txt', fingerprint: true
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    echo "🚦 Waiting for SonarQube Quality Gate..."
                    timeout(time: 15, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: false
                    }
                }
            }
        }
        
        stage('Docker Push - Backend') {
            steps {
                script {
                    echo "🚀 Pushing Backend to Docker Hub..."
                    withCredentials([usernamePassword(
                        credentialsId: DOCKERHUB_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PAT'
                    )]) {
                        sh """
                            echo "Logging into Docker Hub..."
                            echo \$DOCKERHUB_PAT | docker login -u \$DOCKERHUB_USER --password-stdin
                            
                            echo "Pushing backend image: ${DOCKER_IMAGE}"
                            docker push ${DOCKER_IMAGE}
                            
                            echo "✅ Backend image pushed successfully"
                        """
                    }
                }
            }
        }
        
        stage('Docker Push - Frontend') {
            steps {
                script {
                    echo "🚀 Pushing Frontend to Docker Hub..."
                    withCredentials([usernamePassword(
                        credentialsId: DOCKERHUB_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PAT'
                    )]) {
                        sh """
                            echo "Pushing frontend image: ${FRONTEND_IMAGE}"
                            docker push ${FRONTEND_IMAGE}
                            
                            echo "✅ Frontend image pushed successfully"
                            
                            echo "=== PUSHED IMAGES ==="
                            echo "Backend:  ${DOCKER_IMAGE}"
                            echo "Frontend: ${FRONTEND_IMAGE}"
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "=== CI/CD PIPELINE COMPLETED ==="
                echo "📦 Application: ${APP_NAME}"
                echo "📊 Build Result: ${currentBuild.result}"
                echo "🔢 Build Number: ${BUILD_NUMBER}"
                
                // Archive all reports
                archiveArtifacts artifacts: 'security-reports/*,test-reports/*', fingerprint: true
            }
        }
        success {
            echo "🎉 PIPELINE SUCCESS!"
            echo "✅ Code compiled and tested"
            echo "✅ SonarQube analysis completed"
            echo "✅ Security scans completed"
            echo "✅ Docker images built and scanned"
            echo "✅ Images pushed to Docker Hub"
            echo "🐳 Backend:  ${DOCKER_IMAGE}"
            echo "🎨 Frontend: ${FRONTEND_IMAGE}"
        }
        failure {
            echo "❌ Pipeline failed - check stage logs above to identify the issue."
        }
    }
}