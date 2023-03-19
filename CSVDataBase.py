from abstracts import DataBase
from csv import DictReader, DictWriter, excel, register_dialect
from NetCheckExceptions import InputDataNotValid


# create and register cvs dialect for right parse
class CSV_Dialect(excel):
    """Describe the usual properties of CSV files."""
    delimiter = ';'
    quotechar = '"'
    lineterminator = '\n'


register_dialect("CSV", CSV_Dialect)


# csv db class
class CSV(DataBase):

    def __init__(self, path: str, exceptIfNotValid=False):
        super().__init__(path_to_base=path, exceptIfNotValid=exceptIfNotValid)

    def read(self):

        with open(self._PATH) as f:
            reader = DictReader(f, dialect="CSV")
            for row in reader:
                tmp = row
                if tmp["Ports"].count(",") > 0:
                    ports = tmp["Ports"].split(",")
                    tmp["Ports"] = ports
                self.addToBase([tmp])
        # print(self.data)

    def write(self, data: list):
        with open(self._PATH, 'w') as f:
            writer = DictWriter(f, data[0].keys())
            for row in data:
                writer.writerow(row)

    def check(self, debug=False):
        res = []
        for row in self.data:
            valid = 1
            if debug:
                print(f"DB Debug: Read this from file: {row}")
            if ((row["Host"] == "")):
                valid = 0
            if isinstance(row["Ports"], list):
                for port in row["Ports"]:
                    if not port.isdigit():
                        valid = 0
            else:
                if (not row["Ports"].isdigit() and not row["Ports"] == ""):
                    valid = 0
            res += [valid]
        if self.exceptIfDBDataNotValid:
            if res.count(0) > 0:
                raise InputDataNotValid
        else:
            return res


if __name__ == "__main__":
    db = CSV("test.csv", exceptIfNotValid=False)
    db.read()
    check_res = db.check(debug=True)
    print(check_res)
    if check_res.count(0) > 0:
        print("Not all input data is valid!!!")
