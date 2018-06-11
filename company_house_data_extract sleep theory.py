# -*- coding: utf-8 -*-
"""
Created on Tue May 29 18:32:39 2018

@author: Iwan
"""
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import time 

subcontractors = ['marshall catering services', 'motion 7', 'james murray consultants', 'marshall catering services', 'acs consultancy', 'bodycote heat treatments ltd', 'dws', 'charles day steels limited', 'delta rubber', 'simple maintenance solutions', 'beyond limits uk ltd', 'enhanced control systems', 'rapidswitch', 'grosvenor chemicals', 'softlabs solutions ltd']

data = pd.read_csv(r'C:\Users\Iwan\Documents\subcontractors.csv', header=0)
subcontractors=data['job titles']
list = []
missed_list = []
missed_again_list = []

missed_subs = []
missed_again_subs = []
missed_again_again_subs = []

def req_loop(list, missed):
    try:
        r = requests.get(f'https://api.companieshouse.gov.uk/search/?q={company}&items_per_page=10&start_index=1 ', auth=('Ax8_AS-s_MyXeDKbeV8D6V80kvFzUwR2tRI7jGiB', ''))
        
        r=r.json()
        a=json_normalize(r, 'items')
        '''TypeError: 'Response' object does not support indexing. must have it converted to json, it's a specific object for the package'''
        
        '''normalizing the companies we get:
            address	
            address_snippet	WANT
            company_number	WANT
            company_status	WANT
            company_type	WANT
            date_of_creation	MAYBE
            description	
            description_identifier	
            kind	
            links	
            matches	
            snippet	
            title (name of company) WANT
            '''
        co_no= a['company_number'].loc[0]
        a['title'].loc[0]
        a['address_snippet'].loc[0]
        a['company_type'].loc[0]
        a['company_status'].loc[0]
        list.append(a)
    
    except Exception as e: print(e, company), missed.append(company)
    time.sleep(1)
    

for company in subcontractors:
    req_loop(list, missed_list)
    
of_r = requests.get(f'https://api.companieshouse.gov.uk/company/{co_no}/officers', auth=('Ax8_AS-s_MyXeDKbeV8D6V80kvFzUwR2tRI7jGiB', ''))
of_r=of_r.json()

'''this is specifically an formatted string literal operation. without the f this will not work.'''

b=json_normalize(of_r, 'items')

'''
address	WANT
appointed_on	WANT
country_of_residence	
date_of_birth	WANT
links	
name	WANT
nationality	
occupation	 MAYBE
officer_role	WANT
resigned_on WANT

'''

b['name']
b['officer_role']
b['resigned_on']
b['date_of_birth']
b['appointed_on']
b['address']
