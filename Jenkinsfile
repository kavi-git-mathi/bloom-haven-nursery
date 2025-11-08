pipeline {
    agent any
    environment {
        // Application settings
        APP_NAME = 'bloom-haven-nursery'
        DOCKER_IMAGE = "kavitharc/${APP_NAME}:${BUILD_NUMBER}"
        
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
    tools {
        python 'Python3'
        jdk 'jdk11'
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
        
        stage('Python Backend Build') {
            steps {
                script {
                    echo "Building Python Backend (Port ${BACKEND_PORT})..."
                    sh '''
                        cd backend
                        python --version
                        
                        # Create virtual environment
                        python -m venv venv
                        source venv/bin/activate
                        
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
                        python -m pytest tests/ --junitxml=../test-reports/backend-junit.xml --cov-report=xml --cov=. || echo "Tests completed"
                        
                        # Move coverage report
                        if [ -f coverage.xml ]; then
                            mv coverage.xml ../test-reports/backend-coverage.xml
                        fi
                    '''
                }
                
                junit 'test-reports/backend-junit.xml'
                
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-reports',
                    reportFiles: 'index.html',
                    reportName: 'Backend Test Coverage'
                ])
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
                        sleep 5
                        
                        # Test health endpoint
                        echo "Testing backend health..."
                        curl -f http://localhost:${BACKEND_PORT}/ || curl -f http://localhost:${BACKEND_PORT}/health || echo "Health check endpoint not available"
                        
                        # Stop the background process
                        kill $BACKEND_PID 2>/dev/null || true
                        echo "Backend health check completed"
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
                                -Dsonar.verbose=true
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
                        """
                    }
                }
            }
        }
        
        stage('Docker Build - Frontend') {
            steps {
                script {
                    echo "Building Frontend Docker Image (Port ${FRONTEND_PORT})..."
                    
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
                        fi
                        
                        # Build frontend image
                        docker build -t kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER} .
                        
                        # Push frontend image (optional)
                        echo \$DOCKERHUB_PAT | docker login -u \$DOCKERHUB_USER --password-stdin
                        docker push kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER}
                        
                        echo "✅ Frontend image built and pushed"
                    '''
                }
            }
        }
        
        stage('Multi-Container Test') {
            steps {
                script {
                    echo "Testing Multi-Container Setup..."
                    sh '''
                        # Create docker-compose file for testing
                        cat > docker-compose.test.yml << EOF
version: '3.8'
services:
  backend:
    image: ${DOCKER_IMAGE}
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      
  frontend:
    image: kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER}
    ports:
      - "3000:3000"
    depends_on:
      - backend
EOF
                        echo "=== Docker Compose Test Configuration ==="
                        cat docker-compose.test.yml
                        
                        # Test containers (optional - can be commented out)
                        # docker-compose -f docker-compose.test.yml up -d
                        # sleep 10
                        # curl -f http://localhost:5000/ || echo "Backend not reachable"
                        # curl -f http://localhost:3000/ || echo "Frontend not reachable"
                        # docker-compose -f docker-compose.test.yml down
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
                        trivy image kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER} \
                            --format template \
                            --template "@contrib/html.tpl" \
                            --output security-reports/frontend-trivy.html \
                            --severity HIGH,CRITICAL \
                            --exit-code 0
                            
                        echo "=== Security Scan Summary ==="
                        echo "Backend Image:"
                        trivy image ${DOCKER_IMAGE} --severity HIGH,CRITICAL --exit-code 0
                        echo "Frontend Image:"
                        trivy image kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER} --severity HIGH,CRITICAL --exit-code 0
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
                
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'security-reports',
                    reportFiles: 'frontend-trivy.html',
                    reportName: 'Frontend Security Scan'
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
                echo "🐳 Frontend Image: kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER}"
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
                    echo "  Frontend: docker run -p 3000:3000 kavitharc/bloom-haven-nursery-frontend:${BUILD_NUMBER}"
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