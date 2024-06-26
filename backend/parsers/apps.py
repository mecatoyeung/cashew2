import sys

from django.apps import AppConfig
import logging

logging.getLogger('apscheduler.executors.default').setLevel('ERROR')
logging.getLogger('apscheduler.executors.default').propagate = False


def running_migration(argv):
    for arg in argv:
        if "makemigrations" in arg or "migrate" in arg:
            return True
    return False


class ParsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parsers'

    def ready(self):
        if not running_migration(sys.argv):
            from parsers.schedule_jobs.process_file_sources import file_source_scheduler_start
            file_source_scheduler_start()
            from parsers.schedule_jobs.process_import_queue import import_queue_scheduler_start
            import_queue_scheduler_start()
            from parsers.schedule_jobs.process_preprocessing_queue import preprocessing_queue_scheduler_start
            preprocessing_queue_scheduler_start()
            from parsers.schedule_jobs.process_ocr_queue import ocr_queue_scheduler_start
            ocr_queue_scheduler_start()
            from parsers.schedule_jobs.process_splitting_queue import splitting_queue_scheduler_start
            splitting_queue_scheduler_start()
            from parsers.schedule_jobs.process_parsing_queue import parsing_queue_scheduler_start
            parsing_queue_scheduler_start()
            from parsers.schedule_jobs.process_postprocessing_queue import postprocessing_queue_scheduler_start
            postprocessing_queue_scheduler_start()
            from parsers.schedule_jobs.process_integration_queue import integration_queue_scheduler_start
            integration_queue_scheduler_start()
            from parsers.schedule_jobs.process_trash_queue import trash_queue_scheduler_start
            trash_queue_scheduler_start()
            from parsers.schedule_jobs.get_open_ai_metrics import get_open_ai_metrics_scheduler_start
            get_open_ai_metrics_scheduler_start()