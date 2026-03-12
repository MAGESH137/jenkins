pipeline {

  agent none

  options {
    timeout(time: 30, unit: 'MINUTES')
    timestamps()
  }

  environment {
    APP_NAME = 'task-manager'
    VERSION  = "1.0.${BUILD_NUMBER}"
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
        echo "Commit: ${env.SHORT_SHA}"
      }
    }

    stage('Parallel Build') {

      parallel {

        stage('Java Backend') {
          agent {
            docker {
              image 'maven:3.9-eclipse-temurin-17'
            }
          }

          steps {
            dir('backend') {
              sh 'mvn clean package -DskipTests'
              archiveArtifacts artifacts: 'target/*.jar'
            }
          }
        }

        stage('React Frontend') {
          agent {
            docker {
              image 'node:20-alpine'
            }
          }

          steps {
            dir('frontend') {

              sh '''
                mkdir -p $WORKSPACE/.npm
                npm config set cache $WORKSPACE/.npm
                npm install
                npm run build
              '''

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
              sh 'pip install --break-system-packages -r requirements.txt'
              sh 'pytest tests || true'
            }
          }
        }

      }

    }

    stage('Docker Build') {
      agent { label 'docker' }

      steps {

        sh "docker build -t ${REGISTRY}/${APP_NAME}-api:${VERSION} backend"
        sh "docker build -t ${REGISTRY}/${APP_NAME}-ui:${VERSION} frontend"
        sh "docker build -t ${REGISTRY}/${APP_NAME}-analytics:${VERSION} python-service"

      }
    }

  }

  post {

    success {
      echo "PIPELINE SUCCESS"
    }

    failure {
      echo "PIPELINE FAILED"
    }

  }

}
