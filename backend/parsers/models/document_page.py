from django.db import models


class DocumentPage(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        "Document", null=True, related_name='document_pages', on_delete=models.CASCADE)
    page_num = models.IntegerField()
    image_file = models.FileField(null=True, max_length=1023)
    width = models.IntegerField()
    height = models.IntegerField()
    xml = models.TextField(
        default="<?xml version=\"1.0\" encoding=\"utf-8\" ?>")
    hocr = models.TextField()
    ocred = models.BooleanField(null=False, blank=False, default=False)
    chatbot_completed = models.BooleanField(
        null=False, blank=False, default=False)

    class Meta:
        db_table = 'document_pages'
