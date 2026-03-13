pipeline {
  agent none

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
    disableConcurrentBuilds()
    timestamps()
  }

  environment {
    APP_NAME    = 'task-manager'
    VERSION     = "1.0.${env.BUILD_NUMBER}"
    DOCKER_USER = 'luhider'   // ← change this to your Docker Hub username
  }

  stages {

    // ── Stage 1: Checkout ──────────────────────────────────────────────────
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

    // ── Stage 2: Parallel Build & Test ─────────────────────────────────────
    stage('Parallel Build') {
      parallel {

        // ── Java Backend ───────────────────────────────────────────────────
        stage('Java Backend') {
          agent {
            docker { image 'maven:3.9-eclipse-temurin-17' }
          }
          steps {
            dir('backend') {
              sh '''
                echo "=== Patching TaskController.java type bug ==="
                sed -i 's/taskService.getAllTasks().size()/(long) taskService.getAllTasks().size()/g' \
                  src/main/java/com/devops/practice/controller/TaskController.java
                echo "=== Running Maven build ==="
                mvn clean package -DskipTests -Dmaven.repo.local=${WORKSPACE}/.m2
              '''
            }
          }
          post {
            success { echo '✅ Java Backend build passed' }
            failure { echo '❌ Java Backend build failed' }
          }
        }

        // ── React Frontend ─────────────────────────────────────────────────
        stage('React Frontend') {
          agent {
            docker { image 'node:20-alpine' }
          }
          steps {
            dir('frontend') {
              sh 'npm install --cache /tmp/.npm'
              sh 'npm run build'
            }
          }
          post {
            success { echo '✅ React Frontend build passed' }
            failure { echo '❌ React Frontend build failed' }
          }
        }

        // ── Python Tests ───────────────────────────────────────────────────
        stage('Python Tests') {
          agent {
            docker { image 'python:3.11-slim' }
          }
          steps {
            dir('python-service') {
              sh '''
                python -m venv /tmp/venv
                /tmp/venv/bin/pip install --quiet -r requirements.txt
                PYTHONPATH=$(pwd) /tmp/venv/bin/pytest tests/ -v --no-cov
              '''
            }
          }
          post {
            success { echo '✅ Python Tests passed' }
            failure { echo '❌ Python Tests failed' }
          }
        }

      } // end parallel
    }   // end Parallel Build

    // ── Stage 3: Docker Build ──────────────────────────────────────────────
    // Patches broken source files BEFORE docker build runs them.
    // Two known issues in source Dockerfiles:
    //   1. backend/Dockerfile  → runs mvn without the (long) cast fix
    //   2. frontend/Dockerfile → uses "npm ci --frozen-lockfile" but no package-lock.json
    // Both are fixed here with sed before the docker build command runs.
    stage('Docker Build') {
      agent { label 'built-in' }
      steps {
        script {
          echo "🐳 Building Docker images — version: ${VERSION}"

          parallel(

            'backend-image': {
              dir('backend') {
                // Patch the Long/Integer type bug in the source before docker build
                sh '''
                  sed -i 's/taskService.getAllTasks().size()/(long) taskService.getAllTasks().size()/g' \
                    src/main/java/com/devops/practice/controller/TaskController.java
                '''
                def img = docker.build("${DOCKER_USER}/${APP_NAME}-api:${VERSION}")
                img.tag("latest")
                echo "✅ Backend image built: ${DOCKER_USER}/${APP_NAME}-api:${VERSION}"
              }
            },

            'frontend-image': {
              dir('frontend') {
                // FIX: frontend/Dockerfile uses "npm ci --frozen-lockfile" but the
                // repo has no package-lock.json. Patch it to "npm install" instead.
                sh '''
                  sed -i 's/npm ci --frozen-lockfile/npm install/g' Dockerfile
                '''
                def img = docker.build("${DOCKER_USER}/${APP_NAME}-ui:${VERSION}")
                img.tag("latest")
                echo "✅ Frontend image built: ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}"
              }
            },

            'analytics-image': {
              dir('python-service') {
                def img = docker.build("${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}")
                img.tag("latest")
                echo "✅ Analytics image built: ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}"
              }
            }

          ) // end parallel
        }
      }
      post {
        success {
          echo """
          ✅ All Docker images built:
             ${DOCKER_USER}/${APP_NAME}-api:${VERSION}
             ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}
             ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}
          """
        }
        failure { echo '❌ Docker Build stage failed' }
      }
    } // end Docker Build

    // ── Stage 4: Docker Push ───────────────────────────────────────────────
    // Pre-requisite: Add a Jenkins credential with ID 'dockerhub-creds'
    //   Dashboard → Manage Jenkins → Credentials → Global → Add Credentials
    //   Kind: Username with password
    //   ID:   dockerhub-creds
    stage('Docker Push') {
      agent { label 'built-in' }
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
            docker.image("${DOCKER_USER}/${APP_NAME}-api:${VERSION}").push("${VERSION}")
            docker.image("${DOCKER_USER}/${APP_NAME}-api:${VERSION}").push("latest")

            docker.image("${DOCKER_USER}/${APP_NAME}-ui:${VERSION}").push("${VERSION}")
            docker.image("${DOCKER_USER}/${APP_NAME}-ui:${VERSION}").push("latest")

            docker.image("${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}").push("${VERSION}")
            docker.image("${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}").push("latest")
          }
        }
      }
      post {
        success { echo "✅ All images pushed to Docker Hub as version ${VERSION} and latest" }
        failure { echo '❌ Docker Push failed — check dockerhub-creds credential in Jenkins' }
      }
    } // end Docker Push

  } // end stages

  post {
    success {
      echo """
      ╔══════════════════════════════════════════════════╗
      ║  ✅  PIPELINE PASSED — Build #${BUILD_NUMBER}
      ║  Images pushed:
      ║    ${DOCKER_USER}/${APP_NAME}-api:${VERSION}
      ║    ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}
      ║    ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}
      ╚══════════════════════════════════════════════════╝
      """
    }
    failure { echo 'PIPELINE FAILED' }
    always  { echo "Build #${BUILD_NUMBER} finished: ${currentBuild.result ?: 'SUCCESS'}" }
  }

}
