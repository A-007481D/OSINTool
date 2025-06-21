import os
from sherlock import sherlock
from notify import QueryNotify
from sites import SitesInformation
import result as sherlock_result
from result import QueryStatus
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
    progress = pyqtSignal(int, int)
    result_found = pyqtSignal(str, str, str)
    finished = pyqtSignal()

    def __init__(self, total_sites=0):
        super(RealtimeNotifier, self).__init__()
        QObject.__init__(self)
        self.counter = 0
        self.total = total_sites

    def start(self, message):
        # This method is called by Sherlock, but we don't need to do anything here
        # as we've already initialized the total count.
        pass

    def update(self, result):
        self.counter += 1
        self.progress.emit(self.counter, self.total)
        if result.status == sherlock_result.QueryStatus.CLAIMED:
            self.result_found.emit(result.site_name, result.site_url_user, "Found")

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
    data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'data.json'))
    sites = SitesInformation(data_file_path)
    site_data_for_sherlock = {name: site.information for name, site in sites.sites.items()}
    total_sites = len(site_data_for_sherlock)
    query_notify = notifier if notifier else RealtimeNotifier(total_sites=total_sites)
    # The sherlock function is blocking, but our notifier will give us live results.
    sherlock(username, site_data_for_sherlock, query_notify, timeout=60)

    # The results will be collected via the notifier's signals, so we return nothing here.
    # The original return value is now redundant.
    return []
