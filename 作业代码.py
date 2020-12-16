#!/usr/bin/env python
# coding: utf-8

# In[23]:


#-- coding: utf-8 --
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc("font",family='YouYuan')       #设置字体
import jieba,codecs
from collections import Counter
from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image 
from matplotlib.pyplot import imread
import re


# In[29]:


def rating_stat(df):
    '''
    功能：输入电影数据dataframe,输出评论总数、带有评级的评论总数、前两者之差、不同等级评价数量统计
    '''
    num_rating = df.groupby(['rating']).size()
    print('评论总数：',df.shape[0])
    print('有评级的评论总数：',sum(num_rating))
    print('缺失评级的评论数：',df.shape[0]-sum(num_rating))
    print(num_rating)
    num_rating.plot.bar()
    plt.xlabel("评分等级")
    plt.ylabel("评分数量")
    plt.show()    


# In[30]:


# 缺失值4457
def rating_label(df):
    '''
    功能：输入电影数据dataframe,为不同评价等级赋分，很差->力荐 对应 1->5，之后输出平均分数
    ''' 
    df['rating_label'] =None
    df.loc[(df['rating']=='很差'),'rating_label']=1
    df.loc[(df['rating']=='较差'),'rating_label']=2
    df.loc[(df['rating']=='还行'),'rating_label']=3
    df.loc[(df['rating']=='推荐'),'rating_label']=4
    df.loc[(df['rating']=='力荐'),'rating_label']=5
    num_label = df.groupby(['rating_label']).size()
    print(num_label)
    print('电影评分均值：%0.2f'%df['rating_label'].mean())
    num_label.plot.bar()
    plt.xlabel("评分等级")
    plt.ylabel("评分数量")
    plt.show()


# In[31]:


def comment_time(df):
    '''
    功能：输入电影数据dataframe,输出电影数量，评论最少的电影的评论数，评论最多电影的评论数，分年度的评论数统计
    ''' 
    num_movie = df.groupby(['movie_url']).size()   #根据url判断电影
    print('电影总数：',len(num_movie))
    print('评论最少的电影的评论数：',num_movie.values.min())
    print('评论最多的电影的评论数：',num_movie.values.max())
    num_movie_year=df.groupby(['year']).size()
    display(num_movie_year)
    num_movie_year.plot.bar()
    plt.ylim(0,90000)
    plt.yticks(np.arange(0,90000,10000))
    plt.ylabel("评论数量")
    plt.xlabel("年度")
    plt.show()       


# In[32]:


def rating_individual(df):
    '''
    功能：输入电影数据dataframe,统计每部电影评分，输出评分中位数，评分最高电影的评分及url，评分最低电影的评分及url，评分分布图
    ''' 
    num_movie = df.groupby(['movie_url']).size()
    title=[] #电影url列表
    for i in num_movie.index:
        title.append(i)
    score=[] #电影评分
    for i in title:                                               #遍历dataframe,获取和title中名称匹配的评分
        sum=0
        for tup in zip(df['movie_url'], df['rating_label']):         
            if i==tup[0]:
                if tup[1]!=None:
                    sum=sum+tup[1]        
        score.append(sum/num_movie[i])
    score_movie=pd.Series(data=score,index=title)
    print('电影评分中位数：%0.2f'%score_movie.median())
    print('评分最高电影url: %s'%score_movie.idxmax())
    print('最高电影评分：%0.2f'%score_movie.max())
    print('评分最低电影url: %s'%score_movie.idxmin())
    print('最低电影评分：%0.2f'%score_movie.min())
    score_movie.plot.hist(density=1)
    plt.xlim(1,5)
    plt.xticks(np.arange(1,5,0.5))
    plt.yticks(np.arange(0,0.5,0.05))
    plt.ylabel("电影数量")
    plt.xlabel("评分等级")
    score_movie.plot.kde()
    plt.show()
    
rating_individual(df)


# In[33]:


def comment_individual(df):
    '''
    功能：输入电影数据dataframe,统计每个用户的评论数,输出评论的用户总数，每人评论数均值，单人最多评论数，评论数分布图
    '''
    num_user = df.groupby(['user_url']).size()
    display(num_user)
    print('评论用户总数：',len(num_user))
    print('每人评论数均值：%0.2f'%num_user.values.mean())
    print('单人最多评论数：%d'%num_user.values.max())
    num_user.plot.hist(bins=190)
    plt.ylim(0,5000)
    plt.xticks(np.arange(0,190,10))
    plt.yticks(np.arange(0,5000,500))
    plt.ylabel("评分数量")
    plt.xlabel("每人评论数")
    plt.show()
    
comment_individual(df)


# In[46]:


def get_comment(df):
    '''
    功能：输入电影数据dataframe，将所有评论写入all.txt
    '''
    file=open(r"C:\Users\gynda\Desktop\all.txt",'w',encoding='utf-8')   #打开all.txt(可自定义路径)
    for tup in zip(df['rating_label'], df['comment']):
        file.write((str(tup[1])))
        file.write('\n')
    file.close()

def get_commment_low(df):
    '''
    功能：输入电影数据dataframe，将所有1分评论与2分评论写入low.txt
    '''
    file=open(r"C:\Users\gynda\Desktop\low.txt",'w',encoding='utf-8')   #打开low.txt(可自定义路径)
    for tup in zip(df['rating_label'], df['comment']):
        if tup[0]==1 or tup[0]==2:
            if tup[1]!=None:
                file.write((str(tup[1])))
                file.write('\n')
    file.close()

def get_commment_high(df):
    '''
    功能：输入电影数据dataframe，将所有4分评论与5分评论写入low.txt
    '''
    file=open(r"C:\Users\gynda\Desktop\high.txt",'w',encoding='utf-8')   #打开high.txt(可自定义路径)
    for tup in zip(df['rating_label'], df['comment']):
        if tup[0]==4 or tup[0]==5:
            if tup[1]!=None:
                file.write((str(tup[1])))
                file.write('\n')
    file.close()


# In[51]:


def ciyun_comment_all(df):
    '''
    功能：输入电影数据dataframe，导入评论txt、背景图片、停用词，输出词云图
    '''
    text = open(r"C:\Users\gynda\Desktop\all.txt", 'r', encoding='utf-8').read()       #导入评论txt（可自定义路径）
    #结巴分词
    wordlist = jieba.cut(text,cut_all=True)
    wl = " ".join(wordlist)

    #设置词云
    wc = WordCloud(background_color = "white", #设置背景颜色
                   mask = imread(r"C:\Users\gynda\Desktop\OIP.jpg"),  #设置背景图片（可自定义路径）
                   max_words = 2000, #设置最大显示的字数
                   stopwords = open(r"C:\Users\gynda\Desktop\cn_stopwords.txt", 'r', encoding='utf-8').read().split('\n')[:-1], #设置停用词（可自定义路径）
                   font_path=r'C:\Windows\Fonts\SIMYOU.TTF',  # 设置为黑体
            #设置中文字体，使得词云可以显示（词云默认字体是“DroidSansMono.ttf字体库”，不支持中文）
                   max_font_size = 60,  #设置字体最大值
                   random_state = 30, #设置有多少种随机生成状态，即有多少种配色方案
        )
    myword = wc.generate(wl)#生成词云
    wc.to_file('result.jpg')

    #展示词云图
    plt.imshow(myword)
    plt.axis("off")           
    plt.show()
    
def ciyun_comment_low(df):
    low = open(r"C:\Users\gynda\Desktop\low.txt", 'r', encoding='utf-8').read()
    #结巴分词
    wordlist_low = jieba.cut(low,cut_all=True)
    wl_low = " ".join(wordlist_low)

    #设置词云
    wc_low = WordCloud(background_color = "white", #设置背景颜色
                   mask = imread(r"C:\Users\gynda\Desktop\OIP.jpg"),  #设置背景图片
                   max_words = 2000, #设置最大显示的字数
                   stopwords = open(r"C:\Users\gynda\Desktop\cn_stopwords.txt", 'r', encoding='utf-8').read().split('\n')[:-1], #设置停用词
                   font_path=r'C:\Windows\Fonts\SIMYOU.TTF',  # 设置为黑体
            #设置中文字体，使得词云可以显示（词云默认字体是“DroidSansMono.ttf字体库”，不支持中文）
                   max_font_size = 60,  #设置字体最大值
                   random_state = 30, #设置有多少种随机生成状态，即有多少种配色方案
        )
    myword_low = wc_low.generate(wl_low)#生成词云
    wc_low.to_file('result.jpg')

    #展示词云图
    plt.imshow(myword_low)
    plt.axis("off")
    plt.show()
    
def ciyun_comment_high(df):
    high = open(r"C:\Users\gynda\Desktop\high.txt", 'r', encoding='utf-8').read()
    #结巴分词
    wordlist_high = jieba.cut(high,cut_all=True)
    wl_high = " ".join(wordlist_high)

    #设置词云
    wc_high = WordCloud(background_color = "white", #设置背景颜色
                   mask = imread(r"C:\Users\gynda\Desktop\OIP.jpg"),  #设置背景图片
                   max_words = 2000, #设置最大显示的字数
                   stopwords = open(r"C:\Users\gynda\Desktop\cn_stopwords.txt", 'r', encoding='utf-8').read().split('\n')[:-1], #设置停用词
                   font_path=r'C:\Windows\Fonts\SIMYOU.TTF',  # 设置为黑体
            #设置中文字体，使得词云可以显示（词云默认字体是“DroidSansMono.ttf字体库”，不支持中文）
                   max_font_size = 60,  #设置字体最大值
                   random_state = 30, #设置有多少种随机生成状态，即有多少种配色方案
        )
    myword_high = wc_high.generate(wl_high)#生成词云
    wc_high.to_file('result.jpg')

    #展示词云图
    plt.imshow(myword_high)
    plt.axis("off")
    plt.show()


# In[ ]:


CSV_FILE_PATH =r'C:\Users\gynda\Desktop\2018豆瓣电影评论.csv'            #获取csv路径 
df = pd.read_csv(CSV_FILE_PATH)                                          #读取csv文件
df['year'] =None
all_type = df['time'].str.split('/').apply(pd.Series) #获取评价年份
df['year']=all_type[0]

rating_stat(df)
rating_label(df)
comment_time(df)
rating_individual(df)
comment_individual(df)
get_comment(df)
get_commment_low(df)
get_commment_high(df)
ciyun_comment_all(df)
ciyun_comment_low(df)
ciyun_comment_high(df)

