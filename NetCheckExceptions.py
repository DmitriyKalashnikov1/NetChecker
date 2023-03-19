class InputDataNotValid(Exception):
    def __init__(self):
        super().__init__()
        self.txt = "InputDataNotValid"


class DBNotModifycateable(Exception):
    def __init__(self):
        super().__init__()
        self.txt = "You can't modify DB"
