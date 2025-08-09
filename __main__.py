import os

import dotenv
import pulumi
import pulumi_docker as docker
from pulumi_gcp import cloudrun

# Load environment variables from .env
dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
GCP_PROJECT = os.getenv("GCP_PROJECT")
PUBSUB_ENABLED = os.getenv("PUBSUB_ENABLED", "true")
PUBSUB_TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", "device-locations")

# Build and push the Docker image
image = docker.Image(
    "main-app",
    build=docker.DockerBuildArgs(
        context=".",
        dockerfile="Dockerfile",
        platform="linux/amd64",
    ),
    image_name=f"gcr.io/{GCP_PROJECT or 'traceit-426022'}/main-app",
    skip_push=False,
)

# Deploy the Cloud Run service with Pub/Sub envs
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
                            name="ECHO_SQL",
                            value="True",
                        ),
                        cloudrun.ServiceTemplateSpecContainerEnvArgs(
                            name="PUBSUB_ENABLED",
                            value=PUBSUB_ENABLED,
                        ),
                        cloudrun.ServiceTemplateSpecContainerEnvArgs(
                            name="GCP_PROJECT",
                            value=GCP_PROJECT,
                        ),
                        cloudrun.ServiceTemplateSpecContainerEnvArgs(
                            name="PUBSUB_TOPIC_ID",
                            value=PUBSUB_TOPIC_ID,
                        ),
                    ],
                )
            ]
        )
    ),
    traffics=[cloudrun.ServiceTrafficArgs(latest_revision=True, percent=100)],
)

# Allow unauthenticated invocations
iam_binding = cloudrun.IamMember(
    "main-app-invoker",
    service=service.name,
    location="us-central1",
    role="roles/run.invoker",
    member="allUsers",
)

# Export the service URL
pulumi.export("service_url", service.statuses.apply(lambda statuses: statuses[0].url))
