from decouple import Csv, config

BLOG_SECRET_KEY: str = config("BLOG_SECRET_KEY")
BLOG_DEBUG: bool = config("BLOG_DEBUG", cast=bool, default=False)
BLOG_ALLOWED_HOSTS: list[str] = config("BLOG_ALLOWED_HOSTS", cast=Csv(), default="").copy()

BLOG_REDIS_URL: str = config("BLOG_REDIS_URL", default="redis://127.0.0.1:6379/1")