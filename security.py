import json
from io import StringIO

class Principal:
    def __init__(self, id):
        self.id = id
    
    def _parse_json(self, label_str):
        """Parse a JSON string into a dictionary."""
        try:
            return json.load(StringIO(label_str))
        except Exception:
            return {}
    
    def can_read(self, data_label):
        """Check if the principal can read data based on its security label."""
        label_dict = self._parse_json(data_label)
        read_by = label_dict.get("read_by", [])
        return "public" in read_by or self.id in read_by
    
    def can_write(self, data_label):
        """Check if the principal can write data based on its security label."""
        label_dict = self._parse_json(data_label)
        write_by = label_dict.get("write_by", [])
        return self.id in write_by