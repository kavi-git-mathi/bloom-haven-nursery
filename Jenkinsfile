pipeline{   
    agent any
    stages {
        stage('Git Checkout') {
            steps {
                script {
                    echo "Checking out code from repository..."
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[url: 'https://github.com/kavi-git-mathi/bloom-haven-nursery.git']]
                    )
                    sh '''
                        echo "Git Branch: $(git branch --show-current)"
                        echo "Git Commit: $(git log -1 --pretty=%H)"
                    '''
                }
            }
        }
}
}