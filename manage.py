import os
import sys

from decouple import Config, RepositoryEnv


def main() -> None:
    env_path = os.path.join(os.path.dirname(__file__), "settings", ".env")
    config = Config(RepositoryEnv(env_path))

    env_id = config("BLOG_ENV_ID", default="local")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{env_id}")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()