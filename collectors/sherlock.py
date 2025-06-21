import os
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus
import sherlock_project
from PyQt5.QtCore import QObject, pyqtSignal

class SilentNotifier(QueryNotify):
    def start(self, username):
        pass
    def update(self, result):
        pass
    def finish(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class RealtimeNotifier(QueryNotify, QObject):
    """Notifier that emits PyQt signals for real-time updates."""
    # Signal: current_progress, total
    progress = pyqtSignal(int, int)
    # Signal: site_name, url, status (e.g., 'Found', 'Not Found')
    result_found = pyqtSignal(str, str, str)
    finished = pyqtSignal()

    def __init__(self):
        super(RealtimeNotifier, self).__init__()
        QObject.__init__(self)
        self.counter = 0
        self.total = 0

    def start(self, message, social_network):
        self.total = len(social_network)

    def update(self, result):
        self.counter += 1
        self.progress.emit(self.counter, self.total)
        if result.status == sherlock_project.result.QueryResult.CLAIMED:
            self.result_found.emit(result.site_name, result.url_user, "Found")

    def finish(self):
        self.finished.emit()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def scan_username(username, notifier=None):
    """
    Scans for a given username across social networks using Sherlock.
    Returns a list of found URLs.
    """
    sherlock_path = os.path.dirname(sherlock_project.__file__)
    data_file_path = os.path.join(sherlock_path, "resources", "data.json")
    sites = SitesInformation(data_file_path)

    query_notify = notifier if notifier else RealtimeNotifier()

    site_data_for_sherlock = {name: site.information for name, site in sites.sites.items()}
    # The sherlock function is blocking, but our notifier will give us live results.
    sherlock(username, site_data_for_sherlock, query_notify, timeout=60)

    # The results will be collected via the notifier's signals, so we return nothing here.
    # The original return value is now redundant.
    return []
