from parsers.models.parser import Parser
from parsers.models.queue_status import QueueStatus
from parsers.models.queue_class import QueueClass
from parsers.models.queue import Queue
from parsers.models.pre_processing import PreProcessing


def create_queue_when_upload_document(document):

    parser = Parser.objects.get(id=document.parser_id)
    # Create queue object in database
    q = Queue()
    q.queue_status = QueueStatus.READY.value
    q.parser = parser
    q.document = document
    pre_processings = PreProcessing.objects.filter(parser_id=q.parser.id)
    if pre_processings.count() > 0:
        q.queue_class = QueueClass.PRE_PROCESSING.value
    else:
        q.queue_class = QueueClass.OCR.value
    q.save()
