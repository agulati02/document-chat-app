from invoke import task


@task
def run(c):
    """
    Run the AI Document Backend service.
    """
    c.run("docker-compose -f .\devops-config\docker-compose.local.yml up --build")


@task
def stop(c):
    """
    Stop the AI Document Backend service.
    """
    c.run("docker-compose down")
