#!/usr/bin/env python
# coding: utf-8

# ## Rocket launches, a best value anaylsis.
# <p>Launching payloads, such as satellites or space station modules, into
# space is expensive and requires careful planning
# Finding and investing in regions that have a developed space industry can
# reduce costs and improve the pace of space travel and exploration.
# <p>The European Space Agency (ESA) has decided to invest in countries that
# are home to the most efficient companies at sending payloads into space.
# In particular, they want to find countries with the lowest average price
# per kilo> (across all companies for each country) that can launch rockets
# into <strong>Low Earth Orbit (LEO)</strong> according to each of their three
# classes (light, medium, and heavy rockets).
# <p>However, there are some additional contraints that the ESA has put in
# place for the selection process:
# Companies included in each country's average price must have a Quality
# Assurance (QA) rating higher than 2. QA is a rating based on previous
# launches. This constraint establishes a minimum level of performance
# for the selection process.
# Countries with a launch costunder \$10,000,000 in total for all rocket
# launches across the three classes should be excluded. This constraint
# ensures that any selected countries will be able to manage the large volume
# of launches required.
#To help you in your task, the ESA has made available to you three datasets:
# single-owner companies (datasets/SO-space.csv) and joint-ventures
# datasets/JV-space.csv, both of which contain launch data on companies that
# offer space services. These are paired with the company info dataset
# (datasets/company_info.csv) which contains the company names, launch
# technology (rockets, balloons, planes, other), and their location details.
#The launch classes are defined as follows based on their payload in Kilograms:
#
#Light > 1,000
#1,000 > Medium > 10,000
#10,000 < Heavy

#Please note that 1000 kg = 1 metric ton
# datasets/SO-space.csv - Space launch data for private single owner companies
# datasets/JV-space.csv - Space launch data for joint venture companies
# datasets/company_info.csv - Company information for all companies

# In[1]:


import pandas as pd
import numpy as np
so = pd.read_csv('datasets/SO-space.csv', thousands=',')
jv = pd.read_csv('datasets/JV-space.csv', thousands=',')
print(so.shape)
print(jv.shape)
company = pd.read_csv('datasets/company_info.csv')
so['Launch Cost'] = 1000000 * pd.to_numeric(so['Launch Cost ($M)'], errors='coerce')
jv['Payload (kg)'] = jv['Payload (tons)'] * 1000
jv['Price ($/kg)'] = jv['Price ($/ton)'] / 1000
jv['Launch Cost'] = pd.to_numeric(jv['Launch Cost'], errors='coerce')


# In[3]:


combined = pd.concat([so, jv], axis=0)
combined = combined.drop(columns=['Launch Cost ($M)', 'Payload (tons)', 'Price ($/ton)'])
combined = combined[combined['Orbit Altitude'] == 'LEO']
combined = combined[combined['QA'] > 2]
print(combined.shape)


# In[4]:


merged = pd.merge(left=combined, right=company, how='left', left_on='Company ID', right_on='ID')
print(merged.shape)
merged['Country'] = merged['Country'].str.lower().str.strip()

merged = merged.drop(columns=['Orbit Altitude', 'QA', 'ID', 'Tech Type'])
print(merged.head())
print(merged.isna().any())
print(merged.isna().sum())
merged = merged.fillna('usa')
print(merged[(merged['Country'].isnull() == True)])


# In[5]:


payload_labels = ['Light', 'Medium', 'Heavy']
payload_bins = [0, 999, 9999, np.inf]
merged['Launch Class'] = pd.cut(merged['Payload (kg)'], payload_bins, labels=payload_labels)
print(merged.head())


# In[6]:


min_cost_sum = merged.groupby(['Country'])[['Launch Cost']].sum()
min_cost_sum = min_cost_sum[min_cost_sum['Launch Cost'] >= 10000000]
min_cost_sum = min_cost_sum.reset_index()
print(min_cost_sum)
grouped = merged[merged['Country'].isin(min_cost_sum['Country'])]
light = grouped[grouped['Launch Class'] == 'Light']
medium = grouped[grouped['Launch Class'] == 'Medium']
heavy = grouped[grouped['Launch Class'] == 'Heavy']


# In[7]:


light_grouped = light.groupby(['Launch Class', 'Country'])['Price ($/kg)'].agg(np.mean).sort_values().reset_index()
medium_grouped = medium.groupby(['Launch Class', 'Country'])['Price ($/kg)'].agg(np.mean).sort_values().reset_index()
heavy_grouped = heavy.groupby(['Launch Class', 'Country'])['Price ($/kg)'].agg(np.mean).sort_values().reset_index()
print(heavy)
print(light_grouped)
print(medium_grouped)
print(heavy_grouped)


# In[8]:


launch_cost = pd.DataFrame()
launch_cost = launch_cost.append(light_grouped.iloc[0])
launch_cost = launch_cost.append(medium_grouped.iloc[0])
launch_cost = launch_cost.append(heavy_grouped.iloc[0])
col_order = ['Launch Class', 'Price ($/kg)', 'Country']
launch_cost = launch_cost.reindex(columns=col_order)
launch_cost = launch_cost.rename(columns={'Price ($/kg)': 'Average Price'})
launch_cost['Country'] = launch_cost['Country'].str.title()
launch_cost.reset_index(inplace=True, drop=True)
print(launch_cost)
print(launch_cost.dtypes)
