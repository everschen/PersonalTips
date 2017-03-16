#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 输入两个文件夹a和b路径，将a中的文件拷进b，并计算拷贝的文件数。重复的不作处理。
import os, time
import shutil

def file_extension(path): 
	source_ext={'.so','','.apk'}
	#print os.path.splitext(path)
	if os.path.splitext(path)[1] in source_ext:
		return 1
	return 0
	
def copyFiles(src, dst):
    print 'copy '+src	
    srcFiles = os.listdir(src)

    if not os.path.isdir(dst):
        os.makedirs(dst) 
    filesCopiedNum = 0

    # 对源文件夹中的每个文件若不存在于目的文件夹则复制
    for file in srcFiles:
        src_path = os.path.join(src, file)
        dst_path = os.path.join(dst, file)
        # 若源路径为文件夹，若存在于目标文件夹，则递归调用本函数；否则先创建再递归。
        #if os.path.isdir(src_path):
            #if not os.path.isdir(dst_path):
            #    os.makedirs(dst_path)  
            #filesCopiedNum += copyFiles(src_path, dst_path)
        # 若源路径为文件，不重复则复制，否则无操作。
        if os.path.isfile(src_path):
            if file_extension(src_path):			
                shutil.copyfile(src_path, dst_path)
                filesCopiedNum += 1

    return filesCopiedNum




  
#print file_extension('C:\py\wxPython')	
			
path='E:\\0222\\20160224\\'

#path=path+time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
#os.makedirs(path)  
#print path

print copyFiles('X:\\sprd7.0_dev\\output',path)		





