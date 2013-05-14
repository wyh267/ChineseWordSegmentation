# -*- coding=utf-8 -*-
'''
Created on 2013-5-9

@author: Wu YingHao

@email:  wyh817@gmail.com

该程序可以在没有语料库的情况下从文本中抽取出中文词汇
理论支持：
http://www.matrix67.com/blog/archives/5044

'''


import math




"""
    计算每个字和词的出现频率
    输入： words 字符串内容
      num 需要截取的最长字串
    输出： split_words 分割好的所有子串的数据，以字典形式返回
      split_words 说明
      {"字串" : [ 出现次数,出现频率,凝固程度,凝固程度*出现次数,自由程度] .....}
"""
def find_words(words,num=6):
    split_words={}
    lens=len(words)
    for i in range(0,lens):
        for j in range(1,num+1):
            if i+j < lens -num-2:
                if words[i:i+j] in split_words:
                    split_words[words[i:i+j]][0]+=1
                    split_words[words[i:i+j]][1]=float(split_words[words[i:i+j]][0])/float(lens)
                    split_words[words[i:i+j]][6].append(words[i-1])
                    split_words[words[i:i+j]][7].append(words[i+j])
                else:
                    split_words[words[i:i+j]]=[1,#words.count(words[i:i+j])
                                               1/float(lens),#float(words.count(words[i:i+j]))/float(len(words))]
                                               words[i:i+j],#words[i:i+j],
                                               1,#1,
                                               1,#1,
                                               0,
                                               [words[i-1]],
                                               [words[i+j]]
                                               ]#0]
                    
                                               
        if(i%10000==0):
            print "完成 :" + str(float(i)/float(len(words))*100) + " %"
                
    return split_words
                


"""
    格式化文件编码，用来处理中文数据
    输入： obj 字符串
      encoding 编码格式【默认utf8】
    输出： 编码后的字符串
"""
def to_unicode_or_bust(obj,encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj




"""
去掉无用的各种符号
输入：words 字符串内容
输出：格式化之后的字符串
"""
def remove_syb(words):
    words=to_unicode_or_bust(words)
    unused_words=u" \t\r\n，。：；“‘”【】『』|=+-——（）*&……%￥#@！~·《》？/?<>,.;:'\"[]{}_)(^$!`"
    unused_english=u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in unused_words:
        words=words.replace(i, "")
    for i in unused_english:
        words=words.replace(i, "")
    return words




"""
    读取文件
    输入：file_name 文件名
    输出：文件内容
"""
def read_file(file_name):
    fp=open(file_name,"r")
    words=fp.read()
    words=remove_syb(words)
    fp.close()
    return words

    


"""
    计算凝聚程度
    输入：words_dic 已经拆分好的字符串字典
    输出：填充好凝聚程度的字典
"""
def find_nh(words_dic):
    for key in words_dic.keys():
        if(len(key)>1):
            #左凝聚程度
            left_p=words_dic[key][1]/(words_dic[key[:1]][1]*words_dic[key[1:]][1])
            #右凝聚程度
            right_p=words_dic[key][1]/(words_dic[key[:-1]][1]*words_dic[key[:-1]][1])
                 
            
            if(left_p<right_p):
                words_dic[key][3]=left_p
            else:
                words_dic[key][3]=right_p
    



"""
    计算自由程度
    输入： word_dic 字典文件
    返回：word_dic 添加自由程度以后的字典
"""
def calc_free(word_dic):
    for key in word_dic.keys():
        front_free=0
        end_free=0
        for front in word_dic[key][6]:
            if front in word_dic:
                front_free-=math.log(word_dic[front][1])*word_dic[front][1]
        
        for end in word_dic[key][7]:
            if end in word_dic:
                end_free-=math.log(word_dic[end][1])*word_dic[end][1]
            
        if(front_free < end_free):
            word_dic[key][5]=front_free
        else:
            word_dic[key][5]=end_free

    return word_dic




"""
    约束输出
    输入：split_new 拆分好的字典，并且已经计算好凝聚程度
     key_freq  词语出现的次数 默认10
     key_len   词语最小长度  默认大于等于2
     key_nh    词语凝聚程度 默认50
    输出：符合约束条件的词语集合
"""
def find_filter(split_new,key_freq=10,key_len=2,key_nh=50,free=0.5):
    key_words={}
    print free
    for key in split_new.keys():
        #print split_new[key][5]
        if( len(key)>=key_len 
            and split_new[key][0]>key_freq 
            and split_new[key][3]>key_nh 
            and split_new[key][5]>free
            ):
            key_words[key]=[split_new[key][0],
                            split_new[key][1],
                            split_new[key][2],
                            split_new[key][3],
                            split_new[key][5]*split_new[key][3],
                            split_new[key][5]
                            ]

    for key in key_words.keys():
        for sub_key in key_words.keys():
            if key.find(sub_key)>=0 and len(sub_key)<len(key) :
                key_words.pop(sub_key)
    
    return key_words






if __name__ == '__main__':
    #输入文件
    words=read_file("d:\\a.txt")
    word_len=raw_input("输入最大词语长度")
    while( word_len.isdigit()==False):
        word_len=raw_input("不是数字，请重新输入")
        
    word_len=int(word_len)
        

    #拆分words
    print "正在拆分词语......"
    split=find_words(words,word_len)
    #计算凝聚程度
    print "正在计算凝聚程度....."
    find_nh(split)
    #计算自由程度
    print "正在计算自由程度....."
    calc_free(split)
    while True:
        freq=raw_input("词语频率")
        while( freq.isdigit()==False):
            freq=raw_input("不是数字，请重新输入词语频率")
            
        nh=raw_input("输入凝合程度")
        while( nh.isdigit()==False):
            nh=raw_input("不是数字，请重新输入凝合程度")
            
        free=raw_input("输入自由程度")
        while(type(eval(free)) != float):
            free=raw_input("不是数字，请重新输入自由程度")
        
        split_new=find_filter(split,int(freq),2,int(nh),float(free))
        
        final_res=sorted(split_new.items(),key=lambda split_new:split_new[1][0])
        
        i=1
        for item in final_res:
            if(len(item[0])>2):
                print "Key : " + item[0] + "\tTimes :" \
                + str(item[1][0])  + "\t\tNG:" \
                + str(item[1][3]) + "\tMut :" \
                + str(item[1][4]) + "\tFree: " \
                + str(item[1][5])
            else:
                print "Key : " +item[0] + "\t\tTimes :" \
                + str(item[1][0])  + "\t\tNG:" \
                + str(item[1][3])  + "\tMut :" \
                + str(item[1][4])  + "\tFree :" \
                + str(item[1][5])
            i+=1
        print "Key Words Num :" + str(i)

    
    
    
    
    
    