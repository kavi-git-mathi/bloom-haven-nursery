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
                    sh '''
                        echo "Repository checked out successfully"
                        ls -la
                        echo "Backend folder:"
                        ls -la backend/
                    '''
                }
            }
        }
        
        stage('Python Backend Build') {
            steps {
                script {
                    echo "🔧 Building Python Backend..."
                    sh '''
                        cd backend
                        echo "=== Installing Dependencies ==="
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        echo "✅ Dependencies installed"
                        
                        # Test if Flask app works
                        echo "=== Testing Flask App ==="
                        python -c "
try:
    from app import app
    print('✅ Flask app imported successfully')
except Exception as e:
    print('❌ Error:', e)
    exit(1)
"
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
            echo "✅ First two stages completed successfully!"
            echo "Next: Add Python Test stage"
        }
        failure {
            echo "❌ Check the specific stage that failed"
        }
    }
}