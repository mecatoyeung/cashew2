from django.utils import timezone

from django.db import models

from parsers.models.parser import Parser

class OpenAIMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    parser = models.ForeignKey(Parser, on_delete=models.CASCADE)
    date = models.DateField(null=False, default=timezone.now)
    processed_tokens = models.IntegerField()
    generated_tokens = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'open_ai_metrics'