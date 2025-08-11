from invoke import task


@task
def install(c):
    """
    Install the AI Document Backend service dependencies.
    """
    c.run("python -m pip install -r requirements.txt")

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
