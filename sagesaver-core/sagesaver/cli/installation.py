class ServerInstallation():
    def __init__(self, dev=False):
        self.dev = dev

    def install(self):
        if self.dev:
            pass


class NotebookInstallation(ServerInstallation):
    pass


class MongoInstallation(ServerInstallation):
    pass


class MysqlInstallation(ServerInstallation):
    pass
