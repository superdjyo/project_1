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
        
        #brian_data = pd.read_csv(r'{0}/row_value_list_reference_table.csv'.format(output_path), encoding = 'utf8' ,dtype='unicode')
        #brian_data.columns = ['ID','ID_1','MODEL_NAME']
          
        #ya_list = pd.read_csv(r'{0}/zf_training_withspec_cleaned.csv'.format(output_path,output_csv_name,today), encoding = 'utf8' ,dtype='unicode')
        #ya_list.columns
        #ze554kl_list = ya_list[ya_list['model']=='ZE554KL'][['model','cpu','pno']].drop_duplicates()
        
        
        #從ireport資料EXCEL  手動填入表格 此表為目前ireport有在使用的資料 
        self.c_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='country').rename(columns ={'COUNTRY_ID':'ID'})
        self.m_list = pd.read_excel(r'{0}/ireport_list.xlsx'.format(output_path), encoding = 'utf8' ,dtype='unicode',sheetname='model').rename(columns ={'MODEL_NAME':'ID'})
        
        
        #找出共同的MODE
        self.row_data_1 = self.row_data[['MODEL_NAME','SALES_MODEL_NAME']].drop_duplicates().copy()

#display_check().row_data_1
#display_check().brian_json

    def country_main(self):
#=====================================================================================#
#運算區 COUNTRY
#分成三階段
#1.比對Brian跟RAW DATA的資料是否同ireport
#2.比對CUSTOMER_BRANCH_NAME
#3.比對不到的補同個COUNTRY
#=====================================================================================#
         #1.比對Brian跟RAW DATA的資料是否同ireport 此部分可以找到CUSTOMER_BRANCH_NAME
        brian_data_c = pd.merge(self.brian_data,self.c_list,on=['ID'])
        
        #2.比對CUSTOMER_BRANCH_NAME
        brian_data_c_1 = brian_data_c[['ID','MODEL_NAME']].rename(columns ={'MODEL_NAME':'CUSTOMER_BRANCH_NAME'})
        
        #3.比對不到的補同個COUNTRY
        row_data_c = self.row_data[['COUNTRY_ID','CUSTOMER_BRANCH_NAME']].drop_duplicates()
        row_data_c_1 = pd.merge(brian_data_c_1,row_data_c,on=['CUSTOMER_BRANCH_NAME'],how='right')
        row_data_c_2= row_data_c_1[row_data_c_1['ID'].notnull()]
        
        #row_data_c_1.loc[row_data_c_1.ID.isnull(),'ID'] = row_data_c_1.loc[row_data_c_1.ID.isnull(),'COUNTRY_ID']
        #找出NULL 且不能在c_list
        row_data_c_1_null = row_data_c_1.loc[row_data_c_1.ID.isnull()]
        row_data_c_1_null.columns =['ID_NEW','CUSTOMER_BRANCH_NAME','ID']
        
        c_list_1=  self.c_list.copy()
        c_list_1['key'] = 1
        
        row_data_c_1_new = pd.merge(c_list_1,row_data_c_1_null,on=['ID'],how='right').copy()
        row_data_c_1_new_1 = row_data_c_1_new[row_data_c_1_new['key'].isnull()].copy()
        row_data_c_1_new_1['ID_NEW'] = row_data_c_1_new_1['ID']
        row_data_c_1_new_2= row_data_c_1_new_1[['ID_NEW','ID','CUSTOMER_BRANCH_NAME']].rename(columns={'ID_NEW':'COUNTRY_ID'})
        
        row_data_all = pd.concat([row_data_c_2,row_data_c_1_new_2])
        
        
        #輸出同時再次比對ireport 的country
        row_data_all = row_data_all[['ID','CUSTOMER_BRANCH_NAME','COUNTRY_ID']].drop_duplicates()#
        country_check_all = pd.merge(row_data_all,self.c_list).rename(columns ={'ID':'C_ID'})
        return country_check_all
    
        
    def model_main(self):    
            #=====================================================================================#
        #運算區 MODEL
        #分成三階段
        #1.model_name 跟 id 相同
        #2.model_name 用;分隔
        #3.model_name 用regexp
        #=====================================================================================#
        
        #pysqldf = lambda q: sqldf(q, globals())
        
        #比對IREPORT有使用到的MODEL
        brian_data_m = pd.merge(self.brian_data,self.m_list,on=['ID'])
        
        #=====================================================================================#
        #1.model_name 跟 id 相同
        #=====================================================================================#
        #單個MODEL
        model_check_1 = pd.merge(self.row_data_1,brian_data_m,on='MODEL_NAME')
        #=====================================================================================#
        #2.model_name 用;分隔
        #=====================================================================================#
        
        #2.model_name 用;分隔
        
        pat_2 ="(.*)?;(.*)?"
        #pat_2 ="(.*)*;(.*)*"
        model_check_2 = [i for i in brian_data_m[['ID','MODEL_NAME']].values.tolist() if re.findall(pat_2,i[1])!=[]]    
        model_check_2_1 = pd.DataFrame([[i[0],j] for i in model_check_2 for j in i[1].replace(' ','').replace(';',',').split(',')],\
                            columns=['ID','MODEL_NAME'])
        model_check_2_2 = pd.merge(model_check_2_1,self.row_data_1,on='MODEL_NAME')
        
        
        
        #=====================================================================================#
        #3.model_name 用regexp
        #=====================================================================================#
        #3.model_name 用regexp
        #74
        
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
            model_check_3_list= df_3.values.tolist()    
            
            all_list = []
            for i in tqdm(model_check_3_list):
                text_test = i[2]
                id_test =i[0]
                all_list.append(text_test)
            return all_list
        
        model_check_3_2 = model_check_f_2(self.row_data_1,model_check_3_1,pat_8)
        return model_check_3_2

display_check().model_main()    


#a1 = "(model REGEXP '^E203')"
#a1 = "(model REGEXP '^X705NA|^X705UV|^X705UA|^X705NC')"
#a1 = "(model REGEXP '^GL753' and sales_model_name REGEXP '^GL|^G5|^G7|^S5|^S7|^z$|^KX|^PX')"
#a1 = "((model REGEXP '^GL502' and sales_model_name REGEXP '^FX|^ZX|^FZ') or model REGEXP '^FX502')"
#re.search(pat,a1.upper()).group(1,2,3)
#re.search(pat,a1.upper()).group(4,5,6)
#re.search(pat,a1.upper()).group(7,8,9)
#re.search(pat,a1.upper()).group(10,11,12)
#re.findall(pat,a1.upper())
        
        def model_check_f_2(df,df_3,pat):
            #df_3 = model_check_3
            #pat = pat_8
            #df = row_data_1
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
    
        #final
#model_check_all = pd.concat([model_check_1[['MODEL_NAME','SALES_MODEL_NAME','ID']],\
#                             model_check_2_2[['MODEL_NAME','SALES_MODEL_NAME','ID']],\
#                             model_check_3_2[['MODEL_NAME','SALES_MODEL_NAME','ID']]]).rename(columns={'ID':'M_ID'})            
        return model_check_3_2
    
display_check().model_main()


#if __name__ == '__main__':  
#    main_all()


#output
#model_check_all.to_csv(r'{0}/model_check_all.csv'.format(output_path,output_csv_name), encoding = 'utf8',index=False)
#country_check_all.to_csv(r'{0}/country_check_all.csv'.format(output_path,output_csv_name), encoding = 'utf8',index=False)
#calendar_list_min_new.to_csv(r'{0}/calendar_list_min_new.csv'.format(output_path,output_csv_name), encoding = 'utf8',index=False)

#找出沒對到的model  因為沒有SALES_MODEL_NAME 所以補上MODEL_NAME也沒有意義 暫先不處理
#model_check_all = pd.merge(model_check_all,m_list,on='ID',how ='right')
#model_check_all.loc[model_check_all['MODEL_NAME'].isnull(),'MODEL_NAME']=model_check_all.loc[model_check_all['MODEL_NAME'].isnull(),'ID']
#model_check_all= model_check_all.rename(columns={'ID':'M_ID'})

#=====================================================================================#
#運算區 COUNTRY
#分成三階段
#1.model_name 跟 id 相同
#2.model_name 用;分隔
#3.model_name 用regexp
#=====================================================================================#

#country_check_all
#model_check_all


#檢查沒串到CID



# "((model REGEXP '^GL502' and sales_model_name REGEXP '^FX|^ZX|^FZ') or model REGEXP '^FX502')"]
#
##2 model regexp '^C302'
#re.search(pat_5,test_2_1[1][2].upper()).group(1)
#
##6 MODEL REGEXP '^GL502' AND SALES_MODEL_NAME REGEXP '^FX|^ZX|^FZ'
#re.search(pat_4,test_2_1[5][2].upper()).group(1)
#re.search(pat_4,test_2_1[5][2].upper()).group(3)
#re.findall(pat_4,test_2_1[5][2].upper())
#
##97 model regexp '^ZD553KL$' and sales_model_name not regexp '^ZB553KL|^X00LDA'
#re.search(pat_4,test_2_1[96][2].upper()).group(1)
#re.search(pat_4,test_2_1[96][2].upper()).group(2)
#re.search(pat_4,test_2_1[96][2].upper()).group(3)
#re.findall(pat_4,test_2_1[96][2].upper())
#
#
##1 model regexp '^FX503' or model regexp '^GL502|^GL553|^GL753' and sales_model_name regexp '^FX|^ZX|^FZ'
#re.search(pat_3,test_2_1[0][2].upper()).group(1)
#re.search(pat_3,test_2_1[0][2].upper()).group(2)
#re.search(pat_3,test_2_1[0][2].upper()).group(3)
#re.findall(pat_3,test_2_1[0][2].upper())
#
#re.findall(pat_3,test_2_1[27][2].upper())
#
##"(MODEL REGEXP '^X411' AND SALES_MODEL_NAME REGEXP '^S|^X|^F|^A|^R422') OR (MODEL REGEXP '^X405|^X442')"
#re.search(pat_2,test_2_1[74][2].upper()).group(3)
#re.findall(pat_2,test_2_1[74][2].upper())


#pat_5 = "\(\(MODEL REGEXP '(.*)?' AND SALES_MODEL_NAME REGEXP '(.*)?'\) OR MODEL REGEXP '(.*)?'\)"
#aaa = "((model REGEXP '^GL502' and sales_model_name REGEXP '^FX|^ZX|^FZ') or model REGEXP '^FX502')"
#re.search(pat_8,aaa.upper()).group(3)
#re.findall(pat_8,aaa.upper())






#country_check_all[country_check_all['C_ID']=='EE']
#
#country_check_all[country_check_all['COUNTRY_ID']=='EE']
#





# -*- coding: utf-8 -*-





class test_main():
    def t1(self,text):
        a1 = text*2
        return a1
    def t2(self,text):
        def t3(tt):
            tt1  = tt*2
            return  tt1          
        a1 = t3(test)/2
        return a1

test= 10

test_main().t1(10)
test_main().t2(10)














