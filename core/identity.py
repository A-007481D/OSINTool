import os
import json

class TargetIdentity:
    """
    Represents a single target and all associated OSINT data.
    """
    def __init__(self, name):
        """
        Initializes a TargetIdentity object.

        Args:
            name (str): The name of the target (e.g., username, domain).
        """
        self.name = name
        self.data = {}  # {scan_type: data}
        self.load_data()

    def load_data(self):
        """Loads all saved data for the target from the data directory."""
        target_dir = os.path.join("data", self.name)
        if not os.path.isdir(target_dir):
            return

        for filename in os.listdir(target_dir):
            if filename.endswith(".json"):
                scan_type = filename.replace(".json", "").replace('_', ' ').title()
                file_path = os.path.join(target_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data[scan_type] = json.load(f)

    def get_data(self, scan_type):
        """
        Retrieves data for a specific scan type.

        Args:
            scan_type (str): The type of scan data to retrieve (e.g., "Username", "Domain").

        Returns:
            The data for the specified scan type, or None if not found.
        """
        return self.data.get(scan_type)

    def get_all_data(self):
        """Returns all data associated with the target."""
        return self.data
