class SyncState:
    def __init__(self):
        self.current_playlist = None
        self.added = []
        self.failed = []

    def reset(self):
        self.__init__()
