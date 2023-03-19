from abstracts import NetChecker, DataBase, IPChecker
from ServerChecker import ServerChecker
from CSVDataBase import CSV
import socket


class App(NetChecker):
    def __init__(self, db: DataBase, checker: IPChecker):
        super().__init__(db, checker)

    def checkAndPrepareEnv(self):
        try:
            import pythonping
        except ImportError:
            print("Please install pythonping lib")
            exit(0)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("172.217.22.14", 80))
            s.close()
        except OSError:
            print("Please check your internet connection")
            exit(0)


if __name__ == "__main__":
    path_to_base = "test.csv"  #
    p = input("Input path to database (default: test.csv): ")
    if p != "":
        path_to_base = p
    debug = "No"
    m = input("Run with debug mode (Yes/No) (default: No): ")
    if m != "":
        debug = m
    if debug == "Yes":
        db = CSV(path=path_to_base, exceptIfNotValid=False)
        checker = ServerChecker(debug=True)
        app = App(db, checker)
        app.checkAndPrepareEnv()
        app.run()
    else:
        db = CSV(path=path_to_base, exceptIfNotValid=True)
        checker = ServerChecker()
        app = App(db, checker)
        app.checkAndPrepareEnv()
        app.run()
