/**
 * ============================================================
 *  Jenkins Practice Pipeline — Task Manager App
 *  Parallel: Java Backend + React Frontend + Python Service
 * ============================================================
 *
 *  Prerequisites on Jenkins:
 *    - Docker available on agents (jenkins user in docker group)
 *    - Plugins: Docker Pipeline, JUnit, Blue Ocean
 *
 *  How to use:
 *    1. Fork this repo to your GitHub account
 *    2. Create a Pipeline job in Jenkins
 *    3. Set "Pipeline script from SCM" → Git → your fork URL
 *    4. Script Path: Jenkinsfile
 *    5. Save and Build Now
 * ============================================================
 */

pipeline {
  // ── No global agent — each stage declares its own Docker container ──────────
  agent none

  // ── Pipeline-wide options ────────────────────────────────────────────────────
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
    disableConcurrentBuilds()
    timestamps()
  }

  // ── Global environment variables ─────────────────────────────────────────────
  environment {
    APP_NAME    = 'task-manager'
    VERSION     = "1.0.${env.BUILD_NUMBER}"
    REGISTRY    = 'docker.io/your-dockerhub-username'   // ← change this
  }

  stages {

    // ── Stage 1: SCM Checkout ─────────────────────────────────────────────────
    stage('Checkout') {
      agent { label 'docker' }   // any agent with Docker
      steps {
        checkout scm
        script {
          env.SHORT_SHA = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
          env.BRANCH    = env.GIT_BRANCH?.replaceAll('origin/', '') ?: 'unknown'
        }
        echo "🔀 Branch: ${env.BRANCH}  |  Commit: ${env.SHORT_SHA}  |  Build: #${BUILD_NUMBER}"
      }
    }

    // ── Stage 2: Parallel Build + Test ────────────────────────────────────────
    stage('Parallel Build') {
      parallel {

        // ── 2a: Java Spring Boot Backend ──────────────────────────────────────
        stage('Java Backend') {
          agent {
            docker {
              image 'maven:3.9-eclipse-temurin-17'
              // Mount Maven local repo to cache dependencies between builds
              args  '-v $HOME/.m2:/root/.m2'
            }
          }
          steps {
            dir('backend') {
              echo '☕ Building Java Spring Boot backend...'

              // Compile
              sh 'mvn clean compile -q'

              // Run unit tests + generate coverage report
              sh 'mvn test jacoco:report'

              // Package the JAR (tests already ran above)
              sh 'mvn package -DskipTests -q'

              // Archive the JAR for downstream stages
              archiveArtifacts artifacts: 'target/*.jar', fingerprint: true

              // Publish JUnit results
              junit 'target/surefire-reports/*.xml'

              echo "✅ Java build complete — JAR archived"
            }
          }
          post {
            failure { echo '❌ Java build failed — check Maven output above' }
          }
        }

        // ── 2b: React Frontend ────────────────────────────────────────────────
        stage('React Frontend') {
          agent {
            docker {
              image 'node:20-alpine'
              // Mount npm cache to speed up dependency install
              args  '-v $HOME/.npm:/root/.npm'
            }
          }
          steps {
            dir('frontend') {
              echo '⚛️  Building React frontend...'

              // Clean install (uses package-lock.json exactly)
              sh 'npm ci --prefer-offline'

              // Lint check
              sh 'npm run lint || true'     // warn but don't fail on lint

              // Run tests with coverage
              sh 'npm test -- --watchAll=false --coverage --passWithNoTests'

              // Production build
              sh 'npm run build'

              // Archive the build output
              archiveArtifacts artifacts: 'build/**', allowEmptyArchive: true

              echo "✅ React build complete — static assets archived"
            }
          }
          post {
            failure { echo '❌ React build failed — check npm output above' }
          }
        }

        // ── 2c: Python Analytics Service ──────────────────────────────────────
        stage('Python Tests') {
          agent {
            docker {
              image 'python:3.11-slim'
              // Mount pip cache directory
              args  '-v $HOME/.cache/pip:/root/.cache/pip'
            }
          }
          steps {
            dir('python-service') {
              echo '🐍 Running Python analytics service tests...'

              // Install all dependencies (including test tools)
              sh 'pip install -r requirements.txt -q'

              // Run pytest with coverage
              sh '''
                pytest tests/ \
                  -v \
                  --tb=short \
                  --cov=app \
                  --cov-report=term-missing \
                  --cov-report=xml:coverage.xml \
                  --junitxml=pytest-results.xml
              '''

              // Publish JUnit results from pytest
              junit 'pytest-results.xml'

              echo "✅ Python tests complete"
            }
          }
          post {
            always {
              // Always publish coverage even on partial failure
              dir('python-service') {
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
              }
            }
            failure { echo '❌ Python tests failed — check pytest output above' }
          }
        }

      } // end parallel
    }   // end stage('Parallel Build')

    // ── Stage 3: Docker Images ────────────────────────────────────────────────
    // Only runs on main/master branch to avoid building images for every branch
    stage('Docker Build') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
          expression { return env.BUILD_DOCKER == 'true' }
        }
      }
      agent { label 'docker' }
      steps {
        echo "🐳 Building Docker images for version ${VERSION}..."
        parallel(
          'backend-image': {
            dir('backend') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-api:${VERSION} ."
            }
          },
          'frontend-image': {
            dir('frontend') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-ui:${VERSION} ."
            }
          },
          'python-image': {
            dir('python-service') {
              sh "docker build -t ${REGISTRY}/${APP_NAME}-analytics:${VERSION} ."
            }
          }
        )
        echo "✅ All Docker images built"
      }
    }

    // ── Stage 4: Integration Test ─────────────────────────────────────────────
    stage('Integration Test') {
      when {
        anyOf { branch 'main'; branch 'master' }
      }
      agent { label 'docker' }
      steps {
        echo '🔗 Running integration tests with docker compose...'
        sh 'docker compose -f docker-compose.test.yml up -d --wait'
        sh 'sleep 10'
        sh '''
          # Smoke test backend
          curl -f http://localhost:8080/health && echo "Backend ✅"
          # Smoke test analytics
          curl -f http://localhost:5000/health && echo "Analytics ✅"
        '''
      }
      post {
        always {
          sh 'docker compose -f docker-compose.test.yml down -v || true'
        }
      }
    }

    // ── Stage 5: Push Images ──────────────────────────────────────────────────
    stage('Push Images') {
      when {
        allOf {
          branch 'main'
          // Only push when DOCKERHUB_CREDS credential exists
          expression { return Jenkins.instance.getCredentials().any { it.id == 'dockerhub-creds' } }
        }
      }
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
        echo "✅ Images pushed to registry"
      }
    }

  } // end stages

  // ── Post-pipeline actions ──────────────────────────────────────────────────
  post {
    success {
      echo """
      ╔══════════════════════════════════════════╗
      ║  ✅  PIPELINE PASSED                     ║
      ║  App: ${APP_NAME}                        ║
      ║  Build: #${BUILD_NUMBER}                 ║
      ║  Version: ${VERSION}                     ║
      ╚══════════════════════════════════════════╝
      """
    }
    failure {
      echo """
      ╔══════════════════════════════════════════╗
      ║  ❌  PIPELINE FAILED                     ║
      ║  Check the stage logs above for details  ║
      ╚══════════════════════════════════════════╝
      """
    }
    always {
      echo "Pipeline finished with status: ${currentBuild.result ?: 'SUCCESS'}"
    }
  }

}
