import requests
from bs4 import BeautifulSoup
import numpy as np
from time import sleep
from random import randint
import json
import os

index_page = requests.get("https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=0&criteria=&value=&isDescending=false")
index_soup = BeautifulSoup(index_page.content, 'html.parser')

def get_all_rows_of_data_from_page(table):
    '''
    Acccesses each data cell from table and maps it to the header
    Returns the populated page_table_data = []
    '''
    page_table_data = []
    for tr in table.find_all("tr", {'class': ['even', 'odd']}):
        t_row = {}
        for td, th in zip(tr.find_all("td"), table_headers):
            t_row[th] = td.text.replace('\n', ' ').replace('\t', ' ').strip()
        page_table_data.append(t_row)
    return page_table_data

def get_all_pages_from_website(num_files, data):
    '''
    Accesses main page of Prior Form Publications
    Parses out total number of files
    Accesses each of the pages
    '''
    # web page setting: display 200 results per page
    pages = np.arange(200, (num_files + 1), 200)
    # keeping track of pages scraped
    num_pages = 1
    for page in pages:
        print("Scraping new page...")
        page = requests.get("https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=" + str(page) + "&criteria=&value=&isDescending=false")
        soup_local = BeautifulSoup(page.content, 'html.parser')
        page_table = soup_local.find("table", class_="picklist-dataTable")
        data += get_all_rows_of_data_from_page(page_table)
        num_pages += 1
        print(str(num_pages) + " scrapped so far")
        # Be nice to their servers
        sleep(randint(2,50))
    return data

def condense_data_to_include_year_range(table):
    temp_list = []
    keys = [list(table[0])]
    form_num = keys[0][0]
    form_title = keys[0][1]
    year = keys[0][2]
    first_row = table[0]
    first_dict = dict( [ 
        (form_num, first_row[form_num]),
        (form_title, first_row[form_title]),
        ('min_year', first_row[year]),
        ('max_year', first_row[year])
        ] )
    temp_list.append(first_dict)
    for i in table:
        place_holder = temp_list.pop()
        if ((i[form_num] == place_holder[form_num]) & 
            (i[form_title] == place_holder[form_title])):
            place_holder['min_year'] = i[year]
            temp_list.append(place_holder)
        else:    
            temp_list.append(place_holder)
            temp_dict = dict( [ 
                (form_num, i[form_num]),
                (form_title, i[form_title]),
                ('min_year', i[year]),
                ('max_year', i[year])
            ] )
            temp_list.append(temp_dict)

    return temp_list

if __name__ == "__main__":
    # Set up table for input from each page
    index_table = index_soup.find("table", class_="picklist-dataTable")
    table_headers = []
    for th in index_table.find_all("th"):
        table_headers.append(th['class'][0])
    table_headers[0] = 'form_number'
    table_headers[1] = 'form_title'
    table_data = []
    # input index page
    table_data += get_all_rows_of_data_from_page(index_table)
    Get the total number of files
    # find total number of documents
    showByColumn = index_soup.find("th", class_="ShowByColumn")
    value_in_column = showByColumn.get_text().strip()
    total_num_files = int(value_in_column[-12:-10] + value_in_column[-9:-6])  
    get_all_pages_from_website(num_files=total_num_files, data=table_data)
    # clean the data
    cleaned_data = []
    cleaned_data = condense_data_to_include_year_range(table_data)
    # write the data to json
    directory = os.path.dirname(os.getcwd())
    pathfile = os.path.join(directory,'data', 'irs_forms.json')
    with open(pathfile, 'w') as outfile:
        json.dump(cleaned_data, outfile)
    print("done")





