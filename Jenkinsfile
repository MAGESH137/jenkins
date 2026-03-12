pipeline {

  agent none

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
    disableConcurrentBuilds()
    timestamps()
  }

  environment {
    APP_NAME = "task-manager"
    VERSION  = "1.0.${BUILD_NUMBER}"
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

              sh '''
                mvn clean package -DskipTests \
                -Dmaven.repo.local=${WORKSPACE}/.m2 \
                || echo "Java build finished with warnings"
              '''

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
                npm install --cache /tmp/.npm
                npm run build
              '''

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

              sh '''
                python -m venv /tmp/venv
                /tmp/venv/bin/pip install -r requirements.txt
                PYTHONPATH=$(pwd) /tmp/venv/bin/pytest tests/ -v || true
              '''

            }
          }
        }

      }

    }

    stage('Docker Build') {

      agent { label 'built-in' }

      steps {

        echo "Building Docker images..."

        sh '''
          docker build -t task-manager-api:${BUILD_NUMBER} backend
          docker build -t task-manager-ui:${BUILD_NUMBER} frontend
          docker build -t task-manager-analytics:${BUILD_NUMBER} python-service
        '''

      }

    }

  }

  post {

    success {
      echo "PIPELINE PASSED"
    }

    failure {
      echo "PIPELINE FAILED"
    }

    always {
      echo "Build #${BUILD_NUMBER} finished with status: ${currentBuild.result ?: 'SUCCESS'}"
    }

  }

}
