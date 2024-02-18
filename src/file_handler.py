def read_from_file(filename):
    file = open(filename, 'r')
    list1=[]
    for line in file:
        list1.append(line.rstrip())
    file.close()
    return list1


def write_to_file(filename, list1):
    file = open(filename, 'w')
    for line in list1:
        file.write(line + "\n")
    file.close()
