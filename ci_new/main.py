from typer import Typer

from cli import build, deploy, update

app = Typer()
app.add_typer(build.app, name="build")
app.add_typer(deploy.app, name="deploy")
app.add_typer(update.app, name="update")

if __name__ == "__main__":
    app()
