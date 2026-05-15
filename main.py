"""Application entry point."""

from app.gui import run_app


def main() -> int:
    """Run the desktop application."""
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
