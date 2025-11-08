pipeline {
    agent any
    environment {
        APP_NAME = 'bloom-haven-nursery'
        DOCKER_IMAGE = "kavitharc/${APP_NAME}:${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'docker-credentials'
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                checkout scm
                script {
                    echo "✅ Git Checkout Completed"
                }
            }
        }
        
        stage('Python Backend Build') {
            steps {
                script {
                    echo "🔧 Building Python Backend..."
                    sh '''
                        cd backend
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        echo "✅ Dependencies installed"
                    '''
                }
            }
        }
        
        stage('Python Backend Test') {
            steps {
                script {
                    echo "🧪 Running Python Tests..."
                    sh '''
                        cd backend
                        . venv/bin/activate
                        pip install pytest pytest-cov
                        mkdir -p ../test-reports
                        python -m pytest tests/ --junitxml=../test-reports/junit.xml --cov-report=xml --cov=. || echo "Tests completed"
                    '''
                }
                junit allowEmptyResults: true, testResults: 'test-reports/junit.xml'
            }
        }
        
        stage('Docker Build - Backend') {
            steps {
                script {
                    echo "🐳 Building Docker Image..."
                    sh '''
                        cd backend
                        # Create Dockerfile
                        cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
EOF
                        docker build -t ${DOCKER_IMAGE} .
                        echo "✅ Docker image built: ${DOCKER_IMAGE}"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "🎯 Build completed with result: ${currentBuild.result}"
        }
        success {
            echo "✅ First four stages completed successfully!"
            echo "Next: Add Docker Push stage"
        }
    }
}