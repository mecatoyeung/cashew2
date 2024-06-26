from django.db import models


class DocumentPage(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        "Document", null=True, related_name='document_pages', on_delete=models.CASCADE)
    page_num = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    xml = models.TextField(
        default="<?xml version=\"1.0\" encoding=\"utf-8\" ?>")
    hocr = models.TextField()
    preprocessed = models.BooleanField(null=False, blank=False, default=False)
    ocred = models.BooleanField(null=False, blank=False, default=False)
    postprocessed = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        db_table = 'document_pages'
