import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from django.utils.log import AdminEmailHandler

LOG_QUEUE = queue.Queue(-1)

queue_listener = None


def start_logging_listener():
    global queue_listener

    if queue_listener:
        return  # already started

    mail_handler = AdminEmailHandler(include_html=True)
    mail_handler.setLevel(logging.ERROR)

    queue_listener = QueueListener(
        LOG_QUEUE,
        mail_handler,
        respect_handler_level=True,
    )

    queue_listener.start()