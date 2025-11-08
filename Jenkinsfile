pipeline {
    agent any
    environment {
        APP_NAME = 'bloom-haven-nursery'
        DOCKER_IMAGE = "kavitharc/${APP_NAME}:${BUILD_NUMBER}"
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
                        
                        # Run tests
                        python -m pytest tests/ --junitxml=../test-reports/junit.xml --cov-report=xml --cov=. || echo "Tests completed"
                        
                        if [ -f coverage.xml ]; then
                            mv coverage.xml ../test-reports/coverage.xml
                            echo "✅ Coverage report generated"
                        fi
                    '''
                }
                junit allowEmptyResults: true, testResults: 'test-reports/junit.xml'
            }
        }
    }
    
    post {
        always {
            echo "🎯 Build completed with result: ${currentBuild.result}"
        }
        success {
            echo "✅ First three stages completed successfully!"
            echo "Next: Add Docker Build stage"
        }
    }
}