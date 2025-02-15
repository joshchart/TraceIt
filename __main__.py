import os

import dotenv
import pulumi
import pulumi_docker as docker
from pulumi_gcp import cloudrun

# Load and Fetch environment variables from the .env file
dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# Build and push the Docker image
image = docker.Image(
    "main-app",
    build=docker.DockerBuildArgs(
        context=".",
        dockerfile="Dockerfile",
        platform="linux/amd64",
    ),
    image_name="gcr.io/traceit-426022/main-app",
    skip_push=False,
)

# Deploy the Cloud Run service
service = cloudrun.Service(
    "main-app",
    location="us-central1",
    template=cloudrun.ServiceTemplateArgs(
        spec=cloudrun.ServiceTemplateSpecArgs(
            containers=[
                cloudrun.ServiceTemplateSpecContainerArgs(
                    image=image.image_name,
                    envs=[
                        cloudrun.ServiceTemplateSpecContainerEnvArgs(
                            name="DATABASE_URL",
                            value=DATABASE_URL,
                        ),
                        cloudrun.ServiceTemplateSpecContainerEnvArgs(
                            name="ECHO_SQL", value="True"
                        ),
                    ],
                )
            ]
        )
    ),
    traffics=[cloudrun.ServiceTrafficArgs(latest_revision=True, percent=100)],
)

# Allow unauthenticated invocations by adding this IAM binding
iam_binding = cloudrun.IamMember(
    "main-app-invoker",
    service=service.name,
    location="us-central1",
    role="roles/run.invoker",
    member="allUsers",
)

# Export the service URL (available after deployment)
pulumi.export("service_url", service.statuses.apply(lambda statuses: statuses[0].url))
