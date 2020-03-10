import os

file_list = []

for file in os.listdir('..\\test_out'):

    file_list.append(file)

print(file_list)

index = 0

for file in os.listdir('..\\result'):

    print(file, file_list[index])

    os.rename('..\\result\\' + file, '..\\result1\\' + file_list[index].split('.')[0] + '.' + file.split('.')[1])

    index = index + 1

