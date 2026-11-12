import typer

from zapcart_api.core.enums import UserRole
from zapcart_api.core.security import hash_password
from zapcart_api.database import SessionLocal
from zapcart_api.models import User

app = typer.Typer(
    name="zapcart",
    help="Zapcart CLI management application.",
    no_args_is_help=True,
)

@app.command()
def ping() -> None:
    """Check if the CLI application is working."""
    typer.secho("Zapcart CLI is working properly!", fg=typer.colors.GREEN)

@app.command(name="create-admin")
def create_admin(
    username: str = typer.Option(..., "--username", "-u", prompt=True, help="Admin username"),
    email: str = typer.Option(..., "--email", "-e", prompt=True, help="Admin email address"),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Admin password",
    ),
) -> None:
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            typer.secho(
                f"Error: A user with email '{email}' already exists.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)

        hashed_password = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        typer.secho(
            f"Successfully created admin user '{new_user.username}' (ID: {new_user.id}, Role: {new_user.role.value})!",
            fg=typer.colors.GREEN,
        )
    except typer.Exit:
        raise
    except Exception as exc:
        db.rollback()
        typer.secho(f"Failed to create admin user: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    finally:
        db.close()

if __name__ == "__main__":
    app()