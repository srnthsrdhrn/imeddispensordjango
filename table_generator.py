from beautifultable import BeautifulTable

table = BeautifulTable()
table.column_headers = ["Sno", "Test"]
table.append_row([1, "Test1"])
table.append_row([2, "Test2"])
table.append_row([3, "Test3"])
table.append_row([4, "Test4"])
f = open("table.txt", "w")
f.write(str(table))
f.close()
