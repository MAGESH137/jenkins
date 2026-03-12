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
    DOCKER_USER = 'your-dockerhub-username'   // ← change this to your Docker Hub username
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
        // Patches the Long/Integer type bug in TaskController.java using sed
        // before Maven compiles — no source code change needed.
        stage('Java Backend') {
          agent {
            docker {
              image 'maven:3.9-eclipse-temurin-17'
            }
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
            docker {
              image 'node:20-alpine'
            }
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
            docker {
              image 'python:3.11-slim'
            }
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
    // Builds Docker images for all 3 services in parallel.
    // Each image is tagged with both the build version and 'latest'.
    // Runs only after ALL parallel build/test stages pass.
    stage('Docker Build') {
      agent { label 'built-in' }
      steps {
        script {
          echo "🐳 Building Docker images — version: ${VERSION}"

          parallel(

            // ── Backend image ──────────────────────────────────────────────
            'backend-image': {
              dir('backend') {
                // Patch the type bug before docker build (same fix as above)
                sh '''
                  sed -i 's/taskService.getAllTasks().size()/(long) taskService.getAllTasks().size()/g' \
                    src/main/java/com/devops/practice/controller/TaskController.java
                '''
                def backendImage = docker.build("${DOCKER_USER}/${APP_NAME}-api:${VERSION}")
                backendImage.tag("latest")
                echo "✅ Backend image built: ${DOCKER_USER}/${APP_NAME}-api:${VERSION}"
              }
            },

            // ── Frontend image ─────────────────────────────────────────────
            'frontend-image': {
              dir('frontend') {
                def frontendImage = docker.build("${DOCKER_USER}/${APP_NAME}-ui:${VERSION}")
                frontendImage.tag("latest")
                echo "✅ Frontend image built: ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}"
              }
            },

            // ── Python analytics image ─────────────────────────────────────
            'analytics-image': {
              dir('python-service') {
                def analyticsImage = docker.build("${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}")
                analyticsImage.tag("latest")
                echo "✅ Analytics image built: ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}"
              }
            }

          ) // end parallel inside script
        }
      }
      post {
        success {
          echo """
          ✅ Docker images built successfully:
             ${DOCKER_USER}/${APP_NAME}-api:${VERSION}
             ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}
             ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}
          """
        }
        failure { echo '❌ Docker Build stage failed — check Dockerfile syntax or build errors above' }
      }
    } // end Docker Build

    // ── Stage 4: Docker Push ───────────────────────────────────────────────
    // Pushes all 3 images to Docker Hub.
    // Requires a Jenkins credential with ID 'dockerhub-creds'
    //   → Dashboard → Manage Jenkins → Credentials → Add
    //   → Kind: Username with password
    //   → ID:   dockerhub-creds
    //   → Username: your Docker Hub username
    //   → Password: your Docker Hub password or access token
    stage('Docker Push') {
      agent { label 'built-in' }
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
            // Push backend
            def backendImage = docker.image("${DOCKER_USER}/${APP_NAME}-api:${VERSION}")
            backendImage.push("${VERSION}")
            backendImage.push("latest")

            // Push frontend
            def frontendImage = docker.image("${DOCKER_USER}/${APP_NAME}-ui:${VERSION}")
            frontendImage.push("${VERSION}")
            frontendImage.push("latest")

            // Push analytics
            def analyticsImage = docker.image("${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}")
            analyticsImage.push("${VERSION}")
            analyticsImage.push("latest")
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
      ║  Images: ${DOCKER_USER}/${APP_NAME}-api:${VERSION}
      ║          ${DOCKER_USER}/${APP_NAME}-ui:${VERSION}
      ║          ${DOCKER_USER}/${APP_NAME}-analytics:${VERSION}
      ╚══════════════════════════════════════════════════╝
      """
    }
    failure { echo 'PIPELINE FAILED' }
    always  { echo "Build #${BUILD_NUMBER} finished: ${currentBuild.result ?: 'SUCCESS'}" }
  }

}
