from django.db import models

from django.utils import timezone

from parsers.models.parser import Parser


class Source(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    parser = models.ForeignKey(
        Parser, on_delete=models.CASCADE, related_name='sources')
    source_path = models.CharField(max_length=1023, null=False)
    interval_seconds = models.IntegerField()
    next_run_time = models.DateTimeField(null=False, default=timezone.now)
    activated = models.BooleanField(default=True)

    class Meta:
        db_table = 'sources'
