pipeline {
    agent any

    environment {
        // Use host.docker.internal to refer to the host machine (where ports are mapped)
        TARGET_URL = "http://host.docker.internal:5000"
    }

    stages {
        stage('Initialization') {
            steps {
                echo "Initializing DevSecOps pipeline..."
                sh 'mkdir -p reports'
            }
        }

        stage('Static Analysis (SAST)') {
            parallel {
                stage('Bandit Code Scanning') {
                    steps {
                        echo "Running Bandit SAST scan..."
                        // We run bandit inside a python container to inspect our source code
                        sh 'docker run --rm -v "$(pwd):/src" -w /src python:3.8-slim /bin/sh -c "pip install --quiet bandit && bandit -r app -f json -o reports/bandit_report.json || true"'
                    }
                }

                stage('Dependency Vulnerability Scan') {
                    steps {
                        echo "Running Safety Dependency check..."
                        // Scan python dependencies in requirements.txt
                        sh 'docker run --rm -v "$(pwd):/src" -w /src python:3.8-slim /bin/sh -c "pip install --quiet safety && safety check -r app/requirements.txt --json > reports/safety_report.json || true"'
                    }
                }

                stage('Dockerfile Configuration Scan') {
                    steps {
                        echo "Running Trivy Config scan on Dockerfile..."
                        // Scan the Dockerfile for misconfigurations (running as root, outdated commands, etc.)
                        sh 'docker run --rm -v "$(pwd):/src" -w /src aquasec/trivy config . -f json -o reports/trivy_config_report.json || true'
                    }
                }
            }
        }

        stage('Build Image') {
            steps {
                echo "Building vulnerable application Docker image..."
                sh 'docker build -t vuln-app ./app'
            }
        }

        stage('Image Scanning') {
            steps {
                echo "Running Trivy container image scan..."
                // Scan the built image for operating system package vulnerabilities
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$(pwd):/src" -w /src aquasec/trivy image vuln-app -f json -o reports/trivy_image_report.json || true'
            }
        }

        stage('Dynamic Analysis (DAST)') {
            steps {
                echo "Starting the application container in background..."
                // Run the application container. Note: host.docker.internal will target this container via exposed host port
                sh 'docker run -d --name vuln-app-run -p 5000:5000 vuln-app'
                
                // Wait for the server to start up
                echo "Waiting for app to start..."
                sh 'sleep 5'

                echo "Running SQLMap SQL Injection Scan..."
                // Test the SQL Injection endpoint
                sh 'docker run --rm securing/sqlmap -u "${TARGET_URL}/api/user?username=admin" --batch --text-only --columns --batch > reports/sqlmap_report.txt || true'

                echo "Running OWASP ZAP Baseline Scan..."
                // Run OWASP ZAP against the home and API endpoints
                // We mount reports directory to output ZAP reports
                sh 'docker run --rm -v "$(pwd)/reports:/zap/wrk/:rw" -t owasp/zap2docker-stable zap-baseline.py -t "${TARGET_URL}" -r zap_report.html -J zap_report.json || true'
            }
        }
    }

    post {
        always {
            echo "Cleaning up dynamic containers..."
            sh 'docker stop vuln-app-run || true'
            sh 'docker rm vuln-app-run || true'
            
            echo "Copying reports back to the host workspace..."
            sh 'cp -r reports/* /src/reports/ || true'
            
            echo "Archiving security reports..."
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
        }
    }
}
