from huey_monitor.monitor import Monitor
from ..services.event_bus import event_bus

class ProgressMonitor(Monitor):
    def on_task_progress(self, process_info):
        event_bus.update_progress(process_info)

monitor = ProgressMonitor() 