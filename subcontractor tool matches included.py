# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 21:10:01 2018

@author: Iwan
"""

import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import time
from difflib import SequenceMatcher
import Levenshtein


csv_data = pd.read_csv(r'C:\Users\Iwan\Documents\subcontractors.csv', header=0)
subcontractors = csv_data['job titles']
subcontractors.drop_duplicates(inplace=True)
missed_subs= []
    
    
company_data= []
extracted_cd =[]

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

for company in subcontractors:
    try:
        r = requests.get(f'https://api.companieshouse.gov.uk/search/companies/?q={company}&items_per_page=10&start_index=1 ', auth=('Ax8_AS-s_MyXeDKbeV8D6V80kvFzUwR2tRI7jGiB', ''))
        
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
        api_ext= a[['company_number', 'title', 'address_snippet','company_type', 'company_status']].loc[0]
        api_ext=api_ext.append(pd.Series(company, index=['subcontractor_name']))
        api_ext= api_ext.str.lower()
        api_ext= api_ext.map(lambda x: x.replace('ltd','').replace('limited',''))
        api_ext= api_ext.str.strip()
        api_ext=api_ext.append(pd.Series(Levenshtein.distance(str(company), str(api_ext.loc['title'])), index=['similarity_distance']))
        api_ext=api_ext.append(pd.Series(Levenshtein.ratio(str(company), str(api_ext.loc['title'])), index=['similarity_ratio']))
        api_ext=api_ext.append(pd.Series(Levenshtein.jaro(str(company), str(api_ext.loc['title'])), index=['similarity_jaro']))
        company_data.append(api_ext)
        '''JSONDecodeError: Expecting value'''
    except Exception as e: print(e, company), missed_subs.append(company)
    time.sleep(0.5)
    

    '''a lot of companies look like they should be in companies house. why aren't they fetching results? that is the issue.
    Companies house has a request limit of 600 per 5 minutes. timing repeat operations every 0.5 seconds means I'm completing 600 requests per 5 minutes.
    Binning a list of missed subcontractors showed that companies were being extracted in each instance, the problem was the request limit.
    Also noted on API forums that some clients simply aren't on the companies house api, so they may be on the CH system but they're not visible under the API.'''

df_cd=pd.DataFrame(company_data)

numbers = df_cd['company_number']

import numpy as np
director_data= []
missed_directors= []
for co_no in numbers:
    try:
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
        officers = b[['name', 'officer_role','date_of_birth', 'address']]
        officers=pd.concat([officers, pd.Series(co_no, index=['company_number'])], axis=1)
        director_data.append(officers)
    except Exception as e: print(e, co_no), missed_subs.append(co_no)
    try:
        officers =pd.concat([officers, pd.Series(b['appointed_on'], index=['appointed'])], axis=1)
        director_data.append(officers)
    except:officers=officers.assign(appointed=np.nan)
    director_data.append(officers)
    try:
        officers =pd.concat([officers, pd.Series(b['resigned_on'], index=['resigned'])], axis=1)
        director_data.append(officers)
    except:officers=officers.assign(resigned=np.nan)
    director_data.append(officers)

all_officers=pd.DataFrame(director_data)
test=pd.concat(director_data)
company_house_sub_data=df_cd.join(all_officers, lsuffix='company_number', rsuffix='company_number')

'''resolved issue with similar function, variable and loc needed to be declared a string. Made a function with the loops originally.
then removed as it wasn't advantageous anyway doing so. I had a problem with the loop not forming a dataframe, nothing was added.
'''

'''now i just need to check the levenshulme on matching officers vs client contacts. clients vs subcontractors and drop'''