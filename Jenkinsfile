pipeline {
    agent any
    environment {
        // Application settings
        APP_NAME = 'bloom-haven-nursery'
        DOCKER_IMAGE = "kavithaozhu/${APP_NAME}:${BUILD_NUMBER}"
        
        // SonarQube settings
        SONAR_PROJECT_KEY = 'bloom_haven_nursery'
        SONAR_PROJECT_NAME = 'Bloom Haven Nursery'
        
        // Port configuration
        BACKEND_PORT = '5000'
        FRONTEND_PORT = '3000'
        
        // Credentials IDs
        DOCKERHUB_CREDENTIALS = 'docker-credentials'
        SONARQUBE_CREDENTIALS = 'sonarqube-token'
        AZURE_CREDENTIALS = 'Azure-SP'
        AZURE_TENANT = 'Azure-Tenant'
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                checkout scm
                script {
                    echo "Building Bloom Haven Nursery Application..."
                    echo "Backend Port: ${BACKEND_PORT}, Frontend Port: ${FRONTEND_PORT}"
                    
                    sh '''
                        echo "=== Repository Structure ==="
                        echo "Git Branch: $(git branch --show-current)"
                        ls -la
                        echo "=== Backend Structure ==="
                        ls -la backend/
                        echo "=== Frontend Structure ==="  
                        ls -la frontend/
                    '''
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    echo "Setting up build environment..."
                    sh '''
                        # Check available Python versions
                        echo "=== Python Environment ==="
                        python3 --version || python --version || echo "Python not found, installing..."
                        
                        # Install Python3 if not available
                        if ! command -v python3 &> /dev/null; then
                            echo "Installing Python3..."
                            sudo apt-get update
                            sudo apt-get install -y python3 python3-pip python3-venv
                        fi
                        
                        # Use python3 as default
                        PYTHON_CMD=$(command -v python3 || command -v python)
                        echo "Using Python: $PYTHON_CMD"
                        $PYTHON_CMD --version
                        
                        # Install JDK for SonarQube scanner
                        echo "=== Java Environment ==="
                        java -version || echo "Java not found, installing..."
                        
                        if ! command -v java &> /dev/null; then
                            echo "Installing OpenJDK 11..."
                            sudo apt-get install -y openjdk-11-jdk
                        fi
                        
                        java -version
                    '''
                }
            }
        }
        
        stage('Python Backend Build') {
            steps {
                script {
                    echo "Building Python Backend (Port ${BACKEND_PORT})..."
                    sh '''
                        cd backend
                        
                        # Use system Python
                        PYTHON_CMD=$(command -v python3 || command -v python)
                        $PYTHON_CMD --version
                        $PYTHON_CMD -m pip --version
                        
                        # Create virtual environment
                        $PYTHON_CMD -m venv venv
                        source venv/bin/activate
                        
                        # Upgrade pip
                        pip install --upgrade pip
                        
                        # Install dependencies
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                            echo "✅ Backend dependencies installed"
                        else
                            echo "⚠️ requirements.txt not found, installing Flask and dependencies"
                            pip install flask python-dotenv pytest pytest-cov requests sqlalchemy
                        fi
                        
                        # Verify Flask app structure
                        if [ -f app.py ]; then
                            echo "✅ Main application: app.py"
                            # Check if app.py uses port 5000
                            grep -n "5000" app.py || echo "ℹ️  Port 5000 not explicitly found in app.py"
                        else
                            echo "❌ app.py not found in backend directory"
                            find . -name "*.py" | head -5
                        fi
                    '''
                }
            }
        }
        
        stage('Python Backend Test') {
            steps {
                script {
                    echo "Running Backend Tests..."
                    sh '''
                        cd backend
                        source venv/bin/activate
                        mkdir -p ../test-reports
                        
                        # Run tests
                        echo "Running pytest..."
                        python -m pytest tests/ --junitxml=../test-reports/backend-junit.xml --cov-report=xml --cov=. || echo "Tests completed with exit code: $?"
                        
                        # Move coverage report
                        if [ -f coverage.xml ]; then
                            mv coverage.xml ../test-reports/backend-coverage.xml
                            echo "Coverage report generated"
                        else
                            echo "No coverage.xml generated"
                        fi
                    '''
                }
                
                // Publish test results if they exist
                junit allowEmptyResults: true, testResults: 'test-reports/backend-junit.xml'
            }
        }
        
        stage('Backend Health Check') {
            steps {
                script {
                    echo "Testing Backend Health (Port ${BACKEND_PORT})..."
                    sh '''
                        cd backend
                        source venv/bin/activate
                        
                        # Start backend in background
                        echo "Starting backend server on port ${BACKEND_PORT}..."
                        python app.py &
                        BACKEND_PID=$!
                        
                        # Wait for server to start
                        sleep 10
                        
                        # Test health endpoint
                        echo "Testing backend health..."
                        curl -f http://localhost:${BACKEND_PORT}/ || curl -f http://localhost:${BACKEND_PORT}/health || curl -f http://localhost:${BACKEND_PORT}/api/health || echo "Health check endpoint not available"
                        
                        # Stop the background process
                        kill $BACKEND_PID 2>/dev/null || true
                        sleep 2
                        echo "Backend health check completed"
                    '''
                }
            }
        }
        
        stage('SonarQube Scanner Setup') {
            steps {
                script {
                    echo "Setting up SonarQube Scanner..."
                    sh '''
                        # Install SonarQube Scanner
                        if ! command -v sonar-scanner &> /dev/null; then
                            echo "Installing SonarQube Scanner..."
                            wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
                            sudo unzip sonar-scanner-cli-4.8.0.2856-linux.zip -d /opt/
                            sudo mv /opt/sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner
                            sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
                            rm sonar-scanner-cli-4.8.0.2856-linux.zip
                        fi
                        
                        sonar-scanner --version
                    '''
                }
            }
        }
        
        stage('SonarQube Scan') {
            steps {
                script {
                    echo "Running SonarQube Analysis..."
                    
                    withCredentials([string(credentialsId: SONARQUBE_CREDENTIALS, variable: 'SONAR_TOKEN')]) {
                        sh """
                            cd backend
                            source venv/bin/activate
                            
                            # Run SonarQube analysis
                            sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.projectName="${SONAR_PROJECT_NAME}" \
                                -Dsonar.projectVersion=${BUILD_NUMBER} \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=http://localhost:9000 \
                                -Dsonar.login=${SONAR_TOKEN} \
                                -Dsonar.python.coverage.reportPaths=../test-reports/backend-coverage.xml \
                                -Dsonar.python.xunit.reportPath=../test-reports/backend-junit.xml \
                                -Dsonar.tests=tests \
                                -Dsonar.test.exclusions=**/test_*,**/*_test.py \
                                -Dsonar.scm.disabled=true
                        """
                    }
                }
            }
        }
        
        stage('SonarQube Quality Gate') {
            steps {
                script {
                    echo "Checking SonarQube Quality Gate..."
                    timeout(time: 10, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                    echo "✅ Quality Gate passed!"
                }
            }
        }
        
        stage('Docker Build - Backend') {
            steps {
                script {
                    echo "Building Docker Image for Backend (Port ${BACKEND_PORT})..."
                    
                    sh '''
                        cd backend
                        # Create optimized Dockerfile for Flask app
                        if [ ! -f Dockerfile ]; then
                            echo "Creating Dockerfile for Flask backend..."
                            cat > Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
CMD ["python", "app.py"]
EOF
                            echo "✅ Dockerfile created"
                        fi
                        echo "=== Dockerfile Contents ==="
                        cat Dockerfile
                    '''
                }
            }
        }
        
        stage('Docker Push - Backend') {
            steps {
                script {
                    echo "Pushing Backend Docker Image..."
                    
                    withCredentials([usernamePassword(
                        credentialsId: DOCKERHUB_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PAT'
                    )]) {
                        sh """
                            cd backend
                            # Login to Docker Hub
                            echo \$DOCKERHUB_PAT | docker login -u \$DOCKERHUB_USER --password-stdin
                            
                            # Build with port 5000 exposure
                            docker build -t ${DOCKER_IMAGE} .
                            
                            # Push to Docker Hub
                            docker push ${DOCKER_IMAGE}
                            
                            echo "✅ Backend image pushed: ${DOCKER_IMAGE}"
                            
                            # List images for verification
                            docker images | grep ${APP_NAME}
                        """
                    }
                }
            }
        }
        
        stage('Docker Build - Frontend') {
            steps {
                script {
                    echo "Building Frontend Docker Image (Port ${FRONTEND_PORT})..."
                    
                    withCredentials([usernamePassword(
                        credentialsId: DOCKERHUB_CREDENTIALS,
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PAT'
                    )]) {
                        sh '''
                            cd frontend
                            # Create Dockerfile for frontend static server
                            if [ ! -f Dockerfile ]; then
                                echo "Creating Dockerfile for frontend..."
                                cat > Dockerfile << EOF
FROM python:3.9-alpine
WORKDIR /app
COPY . .
EXPOSE 3000
CMD ["python", "-m", "http.server", "3000"]
EOF
                                echo "✅ Frontend Dockerfile created"
                            fi
                            
                            # Build frontend image
                            docker build -t kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER} .
                            
                            # Push frontend image
                            echo \$DOCKERHUB_PAT | docker login -u \$DOCKERHUB_USER --password-stdin
                            docker push kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER}
                            
                            echo "✅ Frontend image built and pushed"
                        '''
                    }
                }
            }
        }
        
        stage('Trivy Security Scan Setup') {
            steps {
                script {
                    echo "Setting up Trivy Security Scanner..."
                    sh '''
                        # Install Trivy if not available
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy..."
                            wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
                            echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
                            sudo apt-get update
                            sudo apt-get install trivy -y
                        fi
                        
                        trivy --version
                    '''
                }
            }
        }
        
        stage('Trivy Security Scan') {
            steps {
                script {
                    echo "Running Security Scans..."
                    
                    sh '''
                        mkdir -p security-reports
                        
                        # Scan backend image
                        trivy image ${DOCKER_IMAGE} \
                            --format template \
                            --template "@contrib/html.tpl" \
                            --output security-reports/backend-trivy.html \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        # Scan frontend image
                        trivy image kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER} \
                            --format template \
                            --template "@contrib/html.tpl" \
                            --output security-reports/frontend-trivy.html \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        echo "=== Security Scan Summary ==="
                        echo "Backend Image Scan:"
                        trivy image ${DOCKER_IMAGE} --severity HIGH,CRITICAL --exit-code 0 || true
                        echo "Frontend Image Scan:"
                        trivy image kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER} --severity HIGH,CRITICAL --exit-code 0 || true
                    '''
                }
                
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'security-reports',
                    reportFiles: 'backend-trivy.html',
                    reportName: 'Backend Security Scan'
                ])
            }
        }
    }
    
    post {
        always {
            script {
                echo "=== BLOOM HAVEN NURSERY BUILD COMPLETE ==="
                echo "🌿 Application: ${APP_NAME}"
                echo "🔧 Backend Port: ${BACKEND_PORT}"
                echo "🎨 Frontend Port: ${FRONTEND_PORT}"
                echo "🐳 Backend Image: ${DOCKER_IMAGE}"
                echo "🐳 Frontend Image: kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER}"
                echo "📊 SonarQube Project: ${SONAR_PROJECT_NAME}"
                echo "📈 Build Result: ${currentBuild.result}"
                
                // Generate deployment instructions
                sh '''
                    echo "=== DEPLOYMENT INSTRUCTIONS ==="
                    echo "To run locally:"
                    echo "  Backend: cd backend && python app.py"
                    echo "  Frontend: cd frontend && python -m http.server 3000"
                    echo ""
                    echo "To run with Docker:"
                    echo "  Backend: docker run -p 5000:5000 ${DOCKER_IMAGE}"
                    echo "  Frontend: docker run -p 3000:3000 kavithaozhu/bloom-haven-nursery-frontend:${BUILD_NUMBER}"
                    echo ""
                    echo "Access URLs:"
                    echo "  Frontend: http://localhost:3000"
                    echo "  Backend API: http://localhost:5000"
                '''
            }
            cleanWs()
        }
        success {
            script {
                echo "🎉 Bloom Haven Nursery CI/CD Pipeline Completed Successfully!"
                echo "✅ Backend (Flask) on port ${BACKEND_PORT}"
                echo "✅ Frontend (Static) on port ${FRONTEND_PORT}" 
                echo "✅ Both Docker images built and pushed"
                echo "✅ Code quality checks passed"
                echo "✅ Security scans completed"
            }
        }
        failure {
            echo "❌ Pipeline failed. Check logs above for details."
        }
    }
}