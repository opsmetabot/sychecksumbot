import sys

# -*- coding: UTF-8 -*-
import os

dirs = []
files = []

def walkFile(file):
    fileList = []
    for root, dirs, files in os.walk(file):
        # 遍历文件
        for f in files:
            fileList.append(os.path.abspath(os.path.join(root, f)))
    return fileList

def writeFile(filename,flieList,model):
    if model!="a":
        model = "w"
    with open(filename,model,encoding='utf-8') as file:
        for line in flieList:
            file.write(line)
            file.write("\n")

def filterFileList(fileList,model,condition):
    conditions = condition.split("|")
    filteredFileList = []
    if model=="-f":
        for file in fileList:
            flag = True
            for suffix in  conditions:
                if file.endswith(suffix):
                    flag = False
            if flag:
                filteredFileList.append(file)
    elif model=="-n":
        for file in fileList:
            flag = True
            for suffix in conditions:
                if file.endswith(suffix):
                    filteredFileList.append(file)
    else:
        return fileList
    return filteredFileList


if __name__ == '__main__':
    args = sys.argv
    if len(args)<3:
        print("缺少参数 请参考文档")
        sys.exit()
    else:
        directory = args[1]
        targeFile = args[2]
        fileModel = "-w"
        filterModel = ""
        suffix = ""
        if "-a" in args:
            filterModel = "-a"


        if "-n" in args and "-f" in args:
            print()
            sys.exit()
        else:
            if "-f" in args:
                index = args.index("-f")
                if(len(args)>=index+1):
                    suffix = args[index+1]
                    filterModel = "-f"
            elif "-n" in args:
                index = args.index("-n")
                if (len(args) >= index + 1):
                    suffix = args[index + 1]
                    filterModel = "-n"
        fileList = walkFile(directory)
        writeFile(targeFile,filterFileList(fileList,filterModel,suffix),fileModel)

