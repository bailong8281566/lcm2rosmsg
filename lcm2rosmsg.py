# TrajectoryMsg
import os,winreg

key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
desktop = winreg.QueryValueEx(key, "Desktop")[0]

setDir = os.path.join(desktop,'lcm_message')
# 创建desktop/lcm_message/convertros的文件夹，用于保存msg消息
resDir = os.path.join(setDir,'convertros')
lcmfiles = [file for file in os.listdir(setDir) if file.endswith('hpp')]
 
if not os.path.exists(resDir):
    os.makedirs(resDir)


def prehandle(line):
    s_var_index = line.find("<")
    e_var_index = line.find(">")
    if s_var_index > -1 and e_var_index > -1 and s_var_index < e_var_index:
        line = line[s_var_index+1:e_var_index].split("::")[-1].split()[0] + "[] " + line[e_var_index+2:]
        
    else:
        line = line.split("::")[-1]
    
    s_fix_index = line.find("[")
    e_fix_index = line.find("]")
    if s_fix_index > -1 and e_fix_index > -1 and s_fix_index < e_fix_index-1:
        try:
            int(line[s_fix_index+1:e_fix_index])
            first = line.split(" ")[0].split()[0]
            second = line[s_fix_index:]
            third = line.rstrip(second).split(" ")[-1]
            line = first + second + ' ' + third
        except :
            raise RuntimeError('[]间出现非数字，异常！')
    # print(line)
    
    line_split1 = line.split()
    if len(line_split1) != 2:
        print(line_split1)
        raise RuntimeError('格式错误，异常！')
    elif line_split1[0].split('[')[0] in ('float','double','int8_t','int16_t','int32_t','int64_t','boolean','byte'):
        line = line.replace('float','float32',1)
        line = line.replace('double','float64',1)
        line = line.replace('int8_t','int8',1)
        line = line.replace('int16_t','int16',1)
        line = line.replace('int32_t','int32',1)
        line = line.replace('int64_t','int64',1)
        line = line.replace('boolean','bool',1)
        line = line.replace('byte','int8',1)
    else:
        if line_split1[0].split('[')[0] != 'string':
            print('自定义类型 %s\n'%line)
    return line

    
def exportfile(filename):
    with open(os.path.join(setDir,filename),'r',encoding='ISO-8859-1') as f:
        msg = f.readlines()

    checkFlag = False
    msgFilter = []
    for _,line in enumerate(msg):
        #去掉首尾的空格
        line = line.lstrip()
        line = line.rstrip()
        #取第一个;前面的内容，eg.  int8_t     num;
        line = line.split(";")[0]
        if ("public:" == line) and not checkFlag:
            checkFlag = True
            continue
        if ("public:" == line) and checkFlag:
            checkFlag = False
        if checkFlag and line:
            line = prehandle(line)
            msgFilter.append(line)
    # print(msgFilter)
    # 将处理后的定义信号保存到文件中
    with open( os.path.join(resDir,filename.split('.')[0]) + '.msg','a+',encoding='ISO-8859-1') as fp:
        for line in msgFilter:
            fp.write(line + '\n')


for file in lcmfiles:
    exportfile(file)

# 创建1_lcMsg.txt文档，包含所有消息名称   --- 用于填入CMakelists.txt的ADD_FILE
with open( os.path.join(resDir ,'1_lcMsg') + '.txt','a+',encoding='ISO-8859-1') as fp:
    for file in lcmfiles:
        fp.write(file.split('.')[0]+'.msg' + '\n')
        
# 创建1_lcMsgHeader.txt文档，里面以.h格式的头文件包含所有消息
with open( os.path.join(resDir ,'1_lcMsgHeader') + '.txt','a+',encoding='ISO-8859-1') as fp:
    for file in lcmfiles:
        fp.write('#include ' + '"athena/' + \
                  file.split('.')[0] + '.h"' + '\n')