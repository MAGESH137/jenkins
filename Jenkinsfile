pipeline {

  agent none

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
    disableConcurrentBuilds()
    timestamps()
  }

  environment {
    APP_NAME = 'task-manager'
    VERSION  = "1.0.${env.BUILD_NUMBER}"
    REGISTRY = 'docker.io/magesh137'
  }

  stages {

    stage('Checkout') {
      agent any
      steps {
        checkout scm
        script {
          env.SHORT_SHA = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        }
        echo "Branch: ${env.BRANCH_NAME} Commit: ${env.SHORT_SHA}"
      }
    }

    stage('Parallel Build') {
      parallel {

        stage('Java Backend') {
          agent {
            docker {
              image 'maven:3.9-eclipse-temurin-17'
              args '-v $HOME/.m2:/root/.m2'
            }
          }
          steps {
            dir('backend') {
              sh 'mvn clean compile'
              sh 'mvn test'
              sh 'mvn package -DskipTests'
              archiveArtifacts artifacts: 'target/*.jar'
              junit 'target/surefire-reports/*.xml'
            }
          }
        }

        stage('React Frontend') {
          agent {
            docker {
              image 'node:20-alpine'
              args '-v $HOME/.npm:/root/.npm'
            }
          }
          steps {
            dir('frontend') {

              echo "Building React App"

              sh 'npm install'
              sh 'npm run build'

              archiveArtifacts artifacts: 'build/**', allowEmptyArchive: true
            }
          }
        }

        stage('Python Tests') {
          agent {
            docker {
              image 'python:3.11-slim'
            }
          }
          steps {
            dir('python-service') {

              sh 'pip install -r requirements.txt'

              sh '''
                pytest tests/ \
                --junitxml=pytest-results.xml
              '''

              junit 'pytest-results.xml'
            }
          }
        }

      }
    }

    stage('Docker Build') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
        }
      }

      parallel {

        stage('Backend Image') {
          agent { label 'docker' }
          steps {
            dir('backend') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-api:${VERSION} ."
            }
          }
        }

        stage('Frontend Image') {
          agent { label 'docker' }
          steps {
            dir('frontend') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-ui:${VERSION} ."
            }
          }
        }

        stage('Python Image') {
          agent { label 'docker' }
          steps {
            dir('python-service') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-analytics:${VERSION} ."
            }
          }
        }

      }
    }

    stage('Integration Test') {
      agent { label 'docker' }
      steps {
        sh 'docker compose -f docker-compose.test.yml up -d'
        sh 'sleep 10'
        sh 'curl -f http://localhost:8080 || true'
      }
      post {
        always {
          sh 'docker compose -f docker-compose.test.yml down'
        }
      }
    }

    stage('Push Images') {
      agent { label 'docker' }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {

          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'

          sh "docker push ${REGISTRY}/${APP_NAME}-api:${VERSION}"
          sh "docker push ${REGISTRY}/${APP_NAME}-ui:${VERSION}"
          sh "docker push ${REGISTRY}/${APP_NAME}-analytics:${VERSION}"

          sh 'docker logout'
        }
      }
    }

  }

  post {
    success {
      echo "Pipeline SUCCESS - Version ${VERSION}"
    }

    failure {
      echo "Pipeline FAILED"
    }

    always {
      echo "Build Finished"
    }
  }

}
