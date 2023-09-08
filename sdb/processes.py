from multiprocessing import Process, Event

ACTIVE_PROCESSES = {}
STOP_EVENT = Event()

def cleanup_processes():
    """Cleans up processes dictionary after process is complete."""
    global ACTIVE_PROCESSES
    if 'scraper' in ACTIVE_PROCESSES:
        del ACTIVE_PROCESSES['scraper']
    return
