import json
from typing import TextIO

class AllocatedCache():
    def __init__(self, file: TextIO, key):
        self.file = file
        self.key = key
    
    @property
    def _cache(self):
        return json.load(self.file)
        
    def read(self):
        return self._cache[self.key]
    
    def write(self, value):
        cache = self._cache
        cache[self.key] = value

        json.dump(cache, self.file, indent=2)
