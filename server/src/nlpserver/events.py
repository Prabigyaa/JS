from typing import Callable, Any
from collections import defaultdict
import logging

EVENT_AND_EVENT_HANDLERS: dict[str, list[Callable[..., Any]]] = defaultdict(list)

event_logger = logging.getLogger("event_logger")


def subscribe(event_name: str, event_handler: Callable[..., Any]):
    """
    Add callables (functions) to the event_name
    """
    EVENT_AND_EVENT_HANDLERS[event_name].append(event_handler)


def post_event(event_name: str, *args, **kwargs):
    """
    Call each of the functions associated with the event
    """

    if event_name not in EVENT_AND_EVENT_HANDLERS:
        event_logger.debug(f"The event {event_name} not found.")

    for func in EVENT_AND_EVENT_HANDLERS[event_name]:
        func(*args, **kwargs)


def on_event(event_name):
    """
    Decorator to subscribe to an event
    """
    def subscribe_to_event(func: Callable[..., Any], ):
        subscribe(event_name, func)
    return subscribe_to_event
