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
  }

  stages {

    stage('Checkout') {
      agent { label 'built-in' }
      steps {
        checkout scm
        script {
          env.SHORT_SHA = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        }
        echo "Commit: ${env.SHORT_SHA}"
      }
    }

    stage('Parallel Build') {
      parallel {

        // ── Java Backend ────────────────────────────────────────────────────
        // FIX: mount .m2 cache to /tmp/.m2 (always writable inside container)
        stage('Java Backend') {
          agent {
            docker {
              image 'maven:3.9-eclipse-temurin-17'
              args  '-v /var/lib/jenkins/.m2:/tmp/.m2'
            }
          }
          steps {
            dir('backend') {
              // FIX: pass -Dmaven.repo.local so Maven uses writable /tmp/.m2
              sh 'mvn clean package -DskipTests -Dmaven.repo.local=/tmp/.m2'
            }
          }
          post {
            success { echo '✅ Java Backend build passed' }
            failure { echo '❌ Java Backend build failed' }
          }
        }

        // ── React Frontend ──────────────────────────────────────────────────
        // FIX: use --cache /tmp/.npm so npm never touches /.npmrc (root-owned)
        stage('React Frontend') {
          agent {
            docker {
              image 'node:20-alpine'
              // No home-dir mount needed — we redirect cache to /tmp inside steps
            }
          }
          steps {
            dir('frontend') {
              sh 'npm ci --cache /tmp/.npm'
              sh 'npm run build'
            }
          }
          post {
            success { echo '✅ React Frontend build passed' }
            failure { echo '❌ React Frontend build failed' }
          }
        }

        // ── Python Tests ────────────────────────────────────────────────────
        // FIX: use a venv in /tmp — avoids /.local permission denied entirely
        stage('Python Tests') {
          agent {
            docker {
              image 'python:3.11-slim'
              // No home-dir mount needed — venv lives in /tmp
            }
          }
          steps {
            dir('python-service') {
              sh '''
                python -m venv /tmp/venv
                /tmp/venv/bin/pip install --quiet -r requirements.txt
                /tmp/venv/bin/pytest tests/ -v
              '''
            }
          }
          post {
            success { echo '✅ Python Tests passed' }
            failure { echo '❌ Python Tests failed' }
          }
        }

      } // end parallel
    }   // end stage

  } // end stages

  post {
    success { echo 'PIPELINE PASSED' }
    failure { echo 'PIPELINE FAILED' }
    always  { echo "Build #${BUILD_NUMBER} finished: ${currentBuild.result ?: 'SUCCESS'}" }
  }

}
