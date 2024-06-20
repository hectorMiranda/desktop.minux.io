import logging

class FilteredStreamHandler(logging.StreamHandler):
    def emit(self, record):
        # Filter out specific unwanted messages
        if "ApplePersistenceIgnoreState" in record.getMessage() or record.getMessage() == "Darwin":
            return
        super().emit(record)