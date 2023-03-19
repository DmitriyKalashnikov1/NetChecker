import socket
from pythonping import ping

from abstracts import IPChecker, DataBase
from NetCheckExceptions import InputDataNotValid
from CSVDataBase import CSV
from datetime import datetime
import time


class ServerChecker(IPChecker):

    def __init__(self, debug=False):
        super().__init__(debug=debug)

    def read_from_dataBase(self, dbase: DataBase):
        dbase.read()
        if dbase.exceptIfDBDataNotValid == True:
            try:
                dbase.check()
            except InputDataNotValid:
                print("Not All input data is valid and flag dbase.exceptIfDBDataNotValid = True -> Exit")
                exit(0)
        else:
            res = dbase.check()
            self.db_check_res = res
            if self.debug:  # show many debug info
                if res.count(0) > 0:
                    print("Not all input data is valid. See check result bellow")
                    for row in dbase.data:
                        msg = ""
                        if row["Host"] == "":
                            msg += "|Invalid Host Name|"

                        if isinstance(row["Ports"], list):
                            for port in row["Ports"]:
                                if not port.isdigit():
                                    msg += "|Invalid Port|"
                        else:
                            if (not row["Ports"].isdigit() and not row["Ports"] == ""):
                                msg += "|Invalid Port|"
                        if msg == "":
                            msg = "Valid"
                        print(f"{row}: Check Result: {msg}")

            self.servers = dbase.data

    def check_all(self):
        for index, row in enumerate(self.servers):
            if self.db_check_res[index] == 1:
                # print(row)
                if (row["Host"].count(".") != 3):  # if count of "." != 3 -> need to transform host name to ip
                    if isinstance(row["Ports"], str):
                        adrinfo = []
                        ips = []
                        error = 0
                        try:
                            adrinfo = socket.getaddrinfo(row["Host"], row["Ports"])
                        except socket.gaierror:
                            print(
                                f"DNS server does not return IP address by domain name: {row['Host']}. Skip this host")
                            error = 1
                        if not error:
                            for lst in adrinfo:
                                ips += [lst[4]]  # get ip from all results
                            tmp_info = {}  # And save
                            tmp_info["Host"] = row["Host"]
                            tmp_info["Ports"] = row["Ports"]
                            tmp_info["Ips"] = ips
                            tmp_info["Incorrect"] = 0
                            # print(tmp_info)
                            self.server_info += [tmp_info]
                    else:
                        for port in row["Ports"]:
                            error = 0
                            adrinfo = []
                            ips = []
                            try:
                                adrinfo = socket.getaddrinfo(row["Host"], port)
                                # print(adrinfo)
                            except socket.gaierror:
                                print(
                                    f"DNS server does not return IP address by domain name: {row['Host']}. Skip this host")
                                error = 1
                            if not error:
                                for lst in adrinfo:
                                    ips += [lst[4]]  # get ip from all results
                                tmp_info = {}  # And save
                                tmp_info["Host"] = row["Host"]
                                tmp_info["Ports"] = row["Ports"]
                                tmp_info["Ips"] = ips
                                tmp_info["Incorrect"] = 0
                                # print(tmp_info)
                                self.server_info += [tmp_info]
                            else:
                                break  # if DNS server doesn't return ip -> stop checking this host
                else:  # # if count of "." == 3 -> we have the ip yet
                    if isinstance(row["Ports"], str):
                        tmp_info = {}
                        tmp_info["Host"] = "???"
                        tmp_info["Ports"] = row["Ports"]
                        tmp_info["Ips"] = [row["Host"], row["Ports"]]
                        tmp_info["Incorrect"] = 0
                        # print(tmp_info)
                        self.server_info += [tmp_info]
                    else:
                        for port in row["Ports"]:
                            tmp_info = {}
                            tmp_info["Host"] = "???"
                            tmp_info["Ports"] = row["Ports"]
                            tmp_info["Ips"] = [row["Host"], port]
                            tmp_info["Incorrect"] = 0
                            # print(tmp_info)
                            self.server_info += [tmp_info]


            else:  # this is an incorrect data
                tmp_info = {}
                tmp_info["Host"] = row["Host"]
                tmp_info["Ports"] = row["Ports"]
                tmp_info["Ips"] = []
                tmp_info["Incorrect"] = 1
                # print(tmp_info)
                self.server_info += [tmp_info]
        # print(self.server_info)
        for server in self.server_info:  # check each server
            if server["Incorrect"] == 0:
                if isinstance(server["Ips"][0], tuple):
                    for ip in server["Ips"]:
                        if len(ip) == 2:
                            iptocheck = ip[0]
                            porttocheck = ip[1]
                            if porttocheck > 0:
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                isOpen = s.connect_ex((iptocheck, porttocheck))
                                if isOpen == 0:
                                    # print(iptocheck + ":" + str(porttocheck) + " is open!")
                                    init_time = time.time()
                                    s.sendall(b"GET / HTTP/1.1\r\n\r\n")
                                    s.recv(4096)
                                    stop_time = time.time()
                                    rtt_ms = (stop_time - init_time) * 1000
                                    # print(rtt_ms)
                                    tmp_info = {}
                                    tmp_info["Host"] = server["Host"]
                                    tmp_info["Ip"] = (iptocheck, porttocheck)
                                    tmp_info["Status"] = "Open"
                                    tmp_info["Rtt_ms"] = rtt_ms
                                    tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                                    self.result_of_testing += [tmp_info]
                                else:
                                    # print(iptocheck + ":" + str(porttocheck) + " unknown!")
                                    tmp_info = {}
                                    tmp_info["Host"] = server["Host"]
                                    tmp_info["Ip"] = (iptocheck, porttocheck)
                                    tmp_info["Status"] = "Unknown"
                                    tmp_info["Rtt_ms"] = -1
                                    tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                                    self.result_of_testing += [tmp_info]
                                s.close()
                            else:
                                try:
                                    responce = ping(target=iptocheck)
                                    tmp_info = {}
                                    tmp_info["Host"] = server["Host"]
                                    tmp_info["Ip"] = (iptocheck, porttocheck)
                                    tmp_info["Status"] = "Open"
                                    tmp_info["Rtt_ms"] = responce.rtt_avg_ms
                                    tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                                    self.result_of_testing += [tmp_info]
                                except RuntimeError:
                                    tmp_info = {}
                                    tmp_info["Host"] = server["Host"]
                                    tmp_info["Ip"] = (iptocheck, porttocheck)
                                    tmp_info["Status"] = "Unknown"
                                    tmp_info["Rtt_ms"] = -1
                                    tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                                    self.result_of_testing += [tmp_info]

                elif isinstance(server["Ips"][0], str):
                    iptocheck = server["Ips"][0]
                    porttocheck = int(server["Ips"][1])
                    if porttocheck > 0:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        isOpen = s.connect_ex((iptocheck, porttocheck))
                        if isOpen == 0:
                            print(iptocheck + ":" + str(porttocheck) + " is open!")
                            init_time = time.time()
                            s.sendall(b"GET / HTTP/1.1\r\n\r\n")
                            s.recv(4096)
                            stop_time = time.time()
                            rtt_ms = (stop_time - init_time) * 1000
                            # print(rtt_ms)
                            tmp_info = {}
                            tmp_info["Host"] = server["Host"]
                            tmp_info["Ip"] = (iptocheck, porttocheck)
                            tmp_info["Status"] = "Open"
                            tmp_info["Rtt_ms"] = rtt_ms
                            tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                            self.result_of_testing += [tmp_info]
                        else:
                            # print(iptocheck + ":" + str(porttocheck) + " unknown!")
                            tmp_info = {}
                            tmp_info["Host"] = server["Host"]
                            tmp_info["Ip"] = (iptocheck, porttocheck)
                            tmp_info["Status"] = "Unknown"
                            tmp_info["Rtt_ms"] = -1
                            tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                            self.result_of_testing += [tmp_info]
                        s.close()
                    else:
                        try:
                            responce = ping(target=iptocheck)
                            tmp_info = {}
                            tmp_info["Host"] = server["Host"]
                            tmp_info["Ip"] = (iptocheck, porttocheck)
                            tmp_info["Status"] = "Open"
                            tmp_info["Rtt_ms"] = responce.rtt_avg_ms
                            tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                            self.result_of_testing += [tmp_info]
                        except RuntimeError:
                            tmp_info = {}
                            tmp_info["Host"] = server["Host"]
                            tmp_info["Ip"] = (iptocheck, porttocheck)
                            tmp_info["Status"] = "Unknown"
                            tmp_info["Rtt_ms"] = -1
                            tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                            self.result_of_testing += [tmp_info]
            else:
                tmp_info = {}
                tmp_info["Host"] = server["Host"]
                tmp_info["Ip"] = ("???", server["Ports"])
                tmp_info["Status"] = "Incorrect"
                tmp_info["Rtt_ms"] = -1
                tmp_info["DateTime"] = datetime.now().isoformat(sep=' ')
                self.result_of_testing += [tmp_info]

    def show_check_result(self):
        for res in self.result_of_testing:
            print(
                f"|Host: {res['Host']}|Ip: {res['Ip'][0]}|Port: {res['Ip'][1]}|Status: {res['Status']}|RTT in ms: {res['Rtt_ms']}|Time: {res['DateTime']}|")


if __name__ == "__main__":
    db = CSV("test.csv", exceptIfNotValid=False)
    checker = ServerChecker()
    checker.read_from_dataBase(db)
    checker.check_all()
    checker.show_check_result()
