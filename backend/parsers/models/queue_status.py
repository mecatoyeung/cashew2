from enum import Enum


class QueueStatus(Enum):

    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    TERMINATED_AFTER_TRIAL = "TERMINATED_AFTER_TRIAL"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
