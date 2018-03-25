# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import random
from math import *
import time 
import subprocess
import os
import re
from tqdm import tqdm
import datetime
import requests
from pandasql import sqldf

#import sys
#sys.path.append(r'C:\Users\davidsc_huang\Desktop\git_workspace\asus_work\RevenueAnalysis\code\RawData_Local_FOTA')
from   FilePathConf  import *

#=====================================================================================#
#變數區
#=====================================================================================#
today = time.strftime('%Y-%m-%d',time.gmtime())


#=====================================================================================#
#讀取資料
#1.處理MODEL
#2.處理COUNTRY(COUNTRY_BRANCH)
#3.讀取ireport 對照表 (手動輸入)
#=====================================================================================#
#從new讀取group_list 用此份資料來判斷

class display_check():
    def __init__(self):
        self.aa = 'a'
        #row_data = pd.read_csv(r'{0}/act_history_2018-02-21_new.csv'.format(output_path), encoding = 'utf8' ,dtype='unicode')
        self.row_data = pd.read_csv(r'D:/asus/data/{0}_diff.csv'.format(output_csv_name), encoding = 'utf8')
        #row_data = pd.read_csv(r'{0}/{1}_diff.csv'.format(output_path,output_csv_name), encoding = 'utf8')
        
        #當網址404使用備份
        self.display_name_s_url = 'http://staging-ireport.abc-atec.com/alis/api/v1.0/mapping_table/RowValueListReference'
        self.display_name_t_url = 'http://qtesting-ireport.abc-atec.com/alis/api/v1.0/mapping_table/RowValueListReference'
        
        
        self.brian_json = requests.get('{0}'.format(self.display_name_s_url)) if requests.get('{0}'.\
                                      format(self.display_name_s_url))!=200 else requests.get('{0}'.\
                                            format(self.display_name_t_url))
        self.brian_json_1 = self.brian_json.json()['success']['result']
        self.brian_data = pd.DataFrame(self.brian_json_1)
        self.brian_data.columns = ['ID','ID_1','MODEL_NAME']
        self.c_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='country').rename(columns ={'COUNTRY_ID':'ID'})
        self.m_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='model').rename(columns ={'MODEL_NAME':'ID'})
        
        
        #找出共同的MODE
        self.row_data_1 = self.row_data[['MODEL_NAME','SALES_MODEL_NAME']].drop_duplicates().copy()
        
    def model_main(self):   
        brian_data_m = pd.merge(self.brian_data,self.m_list,on=['ID'])
        #model_check_3 = pysqldf("select * from brian_data_m where MODEL_NAME like '%model%'")
        pat_3 ="model (.*)?"
        model_check_3_1 =pd.DataFrame([i for i in brian_data_m[['ID','ID_1','MODEL_NAME']].values.tolist() if re.findall(pat_3,i[2])!=[]],\
                                       columns =['ID','ID_1','MODEL_NAME'])
   
        #查看index
        #[[i+1,model_check_3.values.tolist()[i]] for i in range(len(model_check_3.values.tolist()))]
        
        #有家括弧
        #pat_5 = "\(MODEL REGEXP '(.*)?'\)"
        #pat_4 = "\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME (NOT )?REGEXP '(.*)?'\)"
        #pat_3 = "\(MODEL REGEXP '(.*)?' OR MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\)"
        #pat_2 = "\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR \(MODEL REGEXP '(.*)?'\)"
        #pat_1 = "\(\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR MODEL REGEXP '(.*)?'\)"
        
        pat_8= "^\(\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR MODEL REGEXP '(.*)?'\)$|\
        ^\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR \(MODEL REGEXP '(.*)?'\)$|\
        \(MODEL REGEXP '(.*)?' OR MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\)|\
        \(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME (NOT )?REGEXP '(.*)?'\)|\
        \(MODEL REGEXP '(.*)?'\)"
        
        #判斷是哪一種
        
        def model_check_f_2(df,df_3,pat):
            #df_3 ,pat,df= model_check_3,pat_8,row_data_1
            model_check_3_list= df_3.values.tolist()    
        
            all_list = []
            for i in tqdm(model_check_3_list):
                text_test = i[2]
                id_test =i[0]
                if re.search(pat,text_test.upper()).group(1,2,3)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(1,2,3)
        
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[1]))|(df['MODEL_NAME'].str.match(ts_1[2]))]
                    #'^(?!P55VA|X550LA)'
                    #'^ZB553KL|^X00LDA'
                elif re.search(pat,text_test.upper()).group(4,5,6)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(4,5,6)
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[1]))|(df['MODEL_NAME'].str.match(ts_1[2]))]
                    
                elif re.search(pat,text_test.upper()).group(7,8,9)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(7,8,9)
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0]))|(df['MODEL_NAME'].str.match(ts_1[1])&df['SALES_MODEL_NAME'].str.match(ts_1[2]))]
                    
                elif re.search(pat,text_test.upper()).group(10,11,12)!=(None, None, None):
                    if re.search(pat,text_test.upper()).group(11) is None:
                        ts_1 = re.search(pat,text_test.upper()).group(10,11,12)
                        ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[2])]
                    else:
                        #為not 需要將字串另外處理
                        ts_1 = re.search(pat,text_test.upper()).group(10,11,12)
                        tt1 = ts_1[2][:1]+'(?!'+ts_1[2][1:]+')'
                        #sft_model_new.loc[sft_model_new['MODEL_NAME'].str.match(pattern)]
                        ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(tt1)]
                    
                elif re.search(pat,text_test.upper()).group(13)!=(None):
                    ts_1 = re.search(pat,text_test.upper()).group(13)
                    ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1)]            
                else:
                    ''
                #ts_2['ID']= id_test
                ts_2.insert(2,'ID',id_test)
                all_list.append(ts_2)  
            data_all = pd.concat(all_list)
            return data_all
        
        #model_check_3_2 = model_check_f_2(self.row_data_1,model_check_3,pat_8)
        model_check_3_2 = model_check_f_2(self.row_data_1,model_check_3_1,pat_8)
#        model_check_3_2 = model_check_f_2(row_data_1,model_check_3_1,pat_8)
#        row_data_1 = display_check().row_data_1.append(pd.DataFrame([['X541test','test1'],['UX461test','test2']],\
#                                                    columns=['MODEL_NAME','SALES_MODEL_NAME']))
        return model_check_3_2

display_check().model_main()       
 









re.findall(pat,text_test.upper())







row_data = pd.read_csv(r'D:/asus/data/{0}_diff.csv'.format(output_csv_name), encoding = 'utf8')
#row_data = pd.read_csv(r'{0}/{1}_diff.csv'.format(output_path,output_csv_name), encoding = 'utf8')

#當網址404使用備份
display_name_s_url = 'http://staging-ireport.abc-atec.com/alis/api/v1.0/mapping_table/RowValueListReference'
display_name_t_url = 'http://qtesting-ireport.abc-atec.com/alis/api/v1.0/mapping_table/RowValueListReference'


brian_json = requests.get('{0}'.format(display_name_s_url)) if requests.get('{0}'.\
                          format(display_name_s_url))!=200 else requests.get('{0}'.\
                                format(display_name_t_url))
brian_json_1 = brian_json.json()['success']['result']
brian_data = pd.DataFrame(brian_json_1)
brian_data.columns = ['ID','ID_1','MODEL_NAME']
c_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='country').rename(columns ={'COUNTRY_ID':'ID'})
m_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='model').rename(columns ={'MODEL_NAME':'ID'})

row_data_1 = row_data[['MODEL_NAME','SALES_MODEL_NAME']].drop_duplicates().copy()


brian_data_m = pd.merge(brian_data,m_list,on=['ID'])
#model_check_3 = pysqldf("select * from brian_data_m where MODEL_NAME like '%model%'")
pat_3 ="model (.*)?"
model_check_3_1 =pd.DataFrame([i for i in brian_data_m[['ID','ID_1','MODEL_NAME']].values.tolist() if re.findall(pat_3,i[2])!=[]],\
                           columns =['ID','ID_1','MODEL_NAME'])
       

a1= "(model REGEXP '^E203')"
a2 = "(model REGEXP '^UX460|^UX461')"
a3 =[ ['FX753',
  'FX753',
  "(model REGEXP '^GL753' and sales_model_name REGEXP '^FX|^ZX|^FZ')"],
 ['G701', 'G701', "(model REGEXP '^G701')"]]




def model_main():  
    
    pat_8= "^\(\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR MODEL REGEXP '(.*)?'\)$|\
    ^\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR \(MODEL REGEXP '(.*)?'\)$|\
    \(MODEL REGEXP '(.*)?' OR MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\)|\
    \(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME (NOT )?REGEXP '(.*)?'\)|\
    \(MODEL REGEXP '(.*)?'\)"
    def model_check_f_2(df,df_3,pat):
        #df_3 ,pat,df= model_check_3_1,pat_8,row_data_1
        model_check_3_list= df_3.values.tolist()    
        try:
            all_list = []
            for i in tqdm(model_check_3_list):
                i = model_check_3_list[0]
                text_test = i[2]
                id_test =i[0]
                if re.search(pat,text_test.upper()).group(1,2,3)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(1,2,3)
        
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[1]))|(df['MODEL_NAME'].str.match(ts_1[2]))]
                    #'^(?!P55VA|X550LA)'
                    #'^ZB553KL|^X00LDA'
                elif re.search(pat,text_test.upper()).group(4,5,6)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(4,5,6)
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[1]))|(df['MODEL_NAME'].str.match(ts_1[2]))]
                    
                elif re.search(pat,text_test.upper()).group(7,8,9)!=(None, None, None):
                    ts_1 = re.search(pat,text_test.upper()).group(7,8,9)
                    ts_2 = df.loc[(df['MODEL_NAME'].str.match(ts_1[0]))|(df['MODEL_NAME'].str.match(ts_1[1])&df['SALES_MODEL_NAME'].str.match(ts_1[2]))]
                    
                elif re.search(pat,text_test.upper()).group(10,11,12)!=(None, None, None):
                    if re.search(pat,text_test.upper()).group(11) is None:
                        ts_1 = re.search(pat,text_test.upper()).group(10,11,12)
                        ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(ts_1[2])]
                    else:
                        #為not 需要將字串另外處理
                        ts_1 = re.search(pat,text_test.upper()).group(10,11,12)
                        tt1 = ts_1[2][:1]+'(?!'+ts_1[2][1:]+')'
                        #sft_model_new.loc[sft_model_new['MODEL_NAME'].str.match(pattern)]
                        ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1[0])&df['SALES_MODEL_NAME'].str.match(tt1)]
                    
                elif re.search(pat,text_test.upper()).group(13)!=(None):
                    ts_1 = re.search(pat,text_test.upper()).group(13)
                    ts_2 = df.loc[df['MODEL_NAME'].str.match(ts_1)]            
                else:
                    ''
                #ts_2['ID']= id_test
                ts_2.insert(2,'ID',id_test)
                all_list.append(ts_2) 
        except:
                ''
        data_all = pd.concat(all_list)
        return data_all

    model_check_3_2 = model_check_f_2(row_data_1,model_check_3_1,pat_8)
    return model_check_3_2



model_main()
