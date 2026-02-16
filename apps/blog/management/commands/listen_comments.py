import redis
from django.conf import settings
from django.core.management.base import BaseCommand

COMMENTS_CHANNEL = "comments"


class Command(BaseCommand):
  help = "Listen to Redis pub/sub channel 'comments' and print messages."

  def handle(self, *args, **options):
    client = redis.from_url(settings.CACHES["default"]["LOCATION"])
    pubsub = client.pubsub()
    pubsub.subscribe(COMMENTS_CHANNEL)

    self.stdout.write(self.style.SUCCESS("Listening on channel: comments"))
    for message in pubsub.listen():
      if message["type"] != "message":
        continue
      data = message["data"]
      if isinstance(data, bytes):
        data = data.decode("utf-8", errors="replace")
      self.stdout.write(data)