from invoke import task


@task
def run(c):
    """
    Run the AI Document Backend service.
    """
    c.run("docker-compose up -d --build")


@task
def stop(c):
    """
    Stop the AI Document Backend service.
    """
    c.run("docker-compose down")
