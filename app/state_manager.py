from threading import Lock

report_states = {}
lock = Lock()

def set_status(report_id, status):
    with lock:
        report_states[report_id] = status

def get_status(report_id):
    with lock:
        return report_states.get(report_id, "not_found")
