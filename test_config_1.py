# -*- coding: utf-8 -*-


env_1 ='all'
#if env_1 :
#    output_path ='hl'
#else:
#    output_path ='sc'
    
def main_all(tt):
    #from test_main import *
    if env_1 =='all':
        if tt == 'y':
            output_path ='hl_u'
            file_path = 'hl_u'
        else:
            output_path ='hl_nu'
            file_path = 'hl_nu'
    else:
        if tt == 'y':
            output_path ='sc_u'
            file_path = 'sc_u'
        else:
            output_path ='sc_nu'
            file_path = 'sc_nu'
    return output_path,file_path
#output_path = main_all(tt)[0]
#file_path = main_all(tt)[1]

if __name__ == "__main__":
    
    output_path = main_all(tt)[0]
    file_path = main_all(tt)[1]



