```groovy
pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        EC2_KEY_NAME = 'disaster-management-key'
        SSH_ALLOWED_CIDR = '103.134.130.254/32'
        APP_ALLOWED_CIDR = '0.0.0.0/0'

        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SONAR_PROJECT_KEY = 'disaster-management-reliability'
        SONAR_PROJECT_NAME = 'Disaster Management Reliability Framework'
        APP_IMAGE = 'myapp:build'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Maddad1010/Disaster_Management_Reliability_Framework.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        "$SONAR_SCANNER_HOME/bin/sonar-scanner" \
                          -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                          -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                          -Dsonar.sources=app \
                          -Dsonar.sourceEncoding=UTF-8
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t "$APP_IMAGE" .'
            }
        }

        stage('Trivy Vulnerability Scan') {
            steps {
                sh '''
                    set -eu
                    mkdir -p reports

                    curl -fsSL \
                      https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl \
                      -o reports/html.tpl

                    JENKINS_VOLUME=$(docker inspect "$(hostname)" \
                      --format '{{range .Mounts}}{{if eq .Destination "/var/jenkins_home"}}{{.Name}}{{end}}{{end}}')

                    test -n "$JENKINS_VOLUME"
                    WORKSPACE_REL="${WORKSPACE#/var/jenkins_home/}"

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v "$JENKINS_VOLUME:/jenkins_home" \
                      aquasec/trivy:0.70.0 \
                      image \
                      --skip-version-check \
                      --scanners vuln \
                      --severity HIGH,CRITICAL \
                      --format template \
                      --template "@/jenkins_home/$WORKSPACE_REL/reports/html.tpl" \
                      --output "/jenkins_home/$WORKSPACE_REL/reports/trivy-report.html" \
                      "$APP_IMAGE"

                    test -s reports/trivy-report.html
                '''

                archiveArtifacts(
                    artifacts: 'reports/trivy-report.html,reports/html.tpl',
                    allowEmptyArchive: false
                )
            }
        }

        stage('Terraform Infrastructure') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    script {
                        sh '''
                            set -eu

                            JENKINS_VOLUME=$(docker inspect "$(hostname)" \
                              --format '{{range .Mounts}}{{if eq .Destination "/var/jenkins_home"}}{{.Name}}{{end}}{{end}}')

                            test -n "$JENKINS_VOLUME"
                            WORKSPACE_REL="${WORKSPACE#/var/jenkins_home/}"
                            TF_DIR="/jenkins_home/$WORKSPACE_REL/terraform"

                            tf() {
                                docker run --rm \
                                  -v "$JENKINS_VOLUME:/jenkins_home" \
                                  -w "$TF_DIR" \
                                  -e AWS_ACCESS_KEY_ID \
                                  -e AWS_SECRET_ACCESS_KEY \
                                  -e AWS_DEFAULT_REGION="$AWS_REGION" \
                                  -e TF_VAR_aws_region="$AWS_REGION" \
                                  -e TF_VAR_ec2_key_name="$EC2_KEY_NAME" \
                                  -e TF_VAR_ssh_allowed_cidr="$SSH_ALLOWED_CIDR" \
                                  -e TF_VAR_app_allowed_cidr="$APP_ALLOWED_CIDR" \
                                  hashicorp/terraform:1.9.8 "$@"
                            }

                            tf init
                            tf validate
                            tf plan -out=tfplan
                            tf apply -auto-approve tfplan

                            tf output -raw ec2_public_ip > "$WORKSPACE/terraform/ec2_ip.txt"
                            tf output -raw ecr_repository_url > "$WORKSPACE/terraform/ecr_url.txt"
                        '''

                        env.EC2_PUBLIC_IP =
                            readFile('terraform/ec2_ip.txt').trim()

                        env.ECR_REPOSITORY_URL =
                            readFile('terraform/ecr_url.txt').trim()

                        echo "EC2 instance provisioned."
                        echo "ECR repository: ${env.ECR_REPOSITORY_URL}"
                    }
                }
            }
        }

        stage('Push Image to ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id',
                           variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key',
                           variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        set -eu
                        export AWS_DEFAULT_REGION="$AWS_REGION"

                        ACCOUNT_ID=$(aws sts get-caller-identity \
                          --query Account --output text)

                        REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

                        aws ecr get-login-password --region "$AWS_REGION" |
                          docker login \
                            --username AWS \
                            --password-stdin "$REGISTRY"

                        docker tag "$APP_IMAGE" "$ECR_REPOSITORY_URL:$BUILD_NUMBER"
                        docker push "$ECR_REPOSITORY_URL:$BUILD_NUMBER"
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'EC2_PRIVATE_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu
                        chmod 600 "$EC2_PRIVATE_KEY"

                        REGISTRY="${ECR_REPOSITORY_URL%%/*}"

                        ssh -i "$EC2_PRIVATE_KEY" \
                          -o StrictHostKeyChecking=accept-new \
                          -o ConnectTimeout=30 \
                          "$SSH_USER@$EC2_PUBLIC_IP" \
                          "set -e
                           aws ecr get-login-password --region '$AWS_REGION' |
                             sudo docker login --username AWS --password-stdin '$REGISTRY'

                           sudo docker pull '$ECR_REPOSITORY_URL:$BUILD_NUMBER'

                           sudo docker rm -f disaster-app || true

                           sudo docker run -d --restart unless-stopped \
                             --name disaster-app \
                             -p 5000:5000 \
                             '$ECR_REPOSITORY_URL:$BUILD_NUMBER'"

                        echo "Deployment completed."
                        echo "Application URL: http://$EC2_PUBLIC_IP:5000"
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'reports/trivy-report.html',
                allowEmptyArchive: true
            )
        }
    }
}
```