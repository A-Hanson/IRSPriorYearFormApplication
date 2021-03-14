import requests
from bs4 import BeautifulSoup
import numpy as np
from time import sleep
from random import randint
import json
import os

descending = "&isDescending=false"

class IRSWebAccessor:
    irs_url = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html?"
    parser = 'html.parser'
    
    
    def __init__(self):
        self.search_headers = []
        self.search_data = []
        self.search_terms = []
        self.cleaned_data = []

    def scrape_by_search_term_and_year_range(self, terms, start, end):
        for term in terms:
            term = term.strip()
        self.search_terms += terms
        if len(self.search_terms) == 0:
            print("No search terms used. Did not attempt to collect anything.")
        else:
            for i in self.search_terms:
                i = i.replace(' ', '+')
                end_of_url = "resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=0&criteria=formNumber&value=" + i + descending
                index_page = requests.get(self.irs_url + end_of_url) 
                index_soup = BeautifulSoup(index_page.content, self.parser)
                # check if results found
                found_results = index_soup.find("div", class_="searchFields")
                if found_results == None:
                    print("No results found.")
                    return
                # set up table
                index_table = index_soup.find("table", class_="picklist-dataTable")
                ####### INSERT METHOD FOR GETTING PDFs
                # Get the total number of files
                total_num_files = get_number_of_documents_from_search(index_soup) 
                self.search_data += get_pdf_links(table=index_table, term=i, start=start, end=end, num_files=total_num_files)

                
        # for term in self.search_terms:
        #     self.cleaned_data += condense_data_to_include_year_range_with_search_terms(table=self.search_data, term=term)

    def scrape_by_search_terms(self, terms):
        for term in terms:
            term = term.strip()
        self.search_terms += terms
        if len(self.search_terms) == 0:
            print("No search terms used. Did not attempt to collect anything.")
        else:
            for i in self.search_terms:
                i = i.replace(' ', '+')
                end_of_url = "resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=0&criteria=formNumber&value=" + i + descending
                index_page = requests.get(self.irs_url + end_of_url) 
                index_soup = BeautifulSoup(index_page.content, self.parser)
                # check if results found
                found_results = index_soup.find("div", class_="searchFields")
                if found_results == None:
                    print("No results found.")
                    return
                # set up table
                index_table = index_soup.find("table", class_="picklist-dataTable")
                self.search_headers += get_table_headers(index_table)
                self.search_data += get_all_rows_of_data_from_page(index_table, self.search_headers)
                # Get the total number of files
                total_num_files = get_number_of_documents_from_search(index_soup) 
                get_all_pages_from_website(get_all=False, num_files=total_num_files, data=self.search_data, headers=self.search_headers, value=i)
        for term in self.search_terms:
            self.cleaned_data += condense_data_to_include_year_range_with_search_terms(table=self.search_data, term=term)
        
        
    def scrape_all_forms(self):
        end_of_url = "resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=0&criteria=&value=&isDescending=false"
        index_page = requests.get(self.irs_url + end_of_url)
        index_soup = BeautifulSoup(index_page.content, self.parser)
        # set up table
        index_table = index_soup.find("table", class_="picklist-dataTable")
        self.search_headers += get_table_headers(index_table)
        self.search_data += get_all_rows_of_data_from_page(index_table, self.search_headers)
        # Get the total number of files
        total_num_files = get_number_of_documents_from_search(index_soup) 
        get_all_pages_from_website(get_all=True, num_files=total_num_files, data=self.search_data, headers=self.search_headers, value="")
        self.cleaned_data += condense_data_to_include_year_range(table=self.search_data)

    def write_to_json(self, file_name):
        ''' writes data from cleaned search data to 
        json file specified within parameters in sibling data file'''
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pathfile = os.path.join(directory,'data', file_name)
        with open(pathfile, 'w') as outfile:
            json.dump(self.cleaned_data, outfile)
        print("Writing to file complete.")

    def clear(self):
        self.search_headers.clear()
        self.search_data.clear()
        self.search_terms.clear()
        self.cleaned_data.clear()
        print("Cleared")

# Helper Methods
def get_pdf_links(table, term, start, end, num_files):
    '''
    Parameters: takes in a soup object, int for year range start, int for year range end
    Returns: List of Strings of pdf links
    '''
    def get_page_links(table, term, start, end):
        term = term.replace("+", " ")
        temp_list = []
        for tr in table.find_all("tr", {'class': ['even', 'odd']}):
            form_num = str(tr.find("td", class_="LeftCellSpacer").get_text(strip=True))
            date = int(tr.find("td", class_="EndCellSpacer").get_text(strip=True))
            print(form_num + ", " + str(date))
            match = [form_num == term, date >= start, date <= end]
            if all(match):
                link = str(tr.find('a').get('href'))
                temp_list.append(link)
                print(link)
        return temp_list
    links = get_page_links(table, term, start, end)
    if num_files >= 200:
        # web page setting: display 200 results per page
        pages = np.arange(200, (num_files + 1), 200)
        # keeping track of pages scraped
        num_pages = 1
        for page in pages:
            page = requests.get("https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=" + str(page) + "&criteria=formNumber&value=" + term + descending)
            soup_local = BeautifulSoup(page.content, 'html.parser')
            page_table = soup_local.find("table", class_="picklist-dataTable")
            links += get_page_links(page_table, term, start, end)
    print("Number of links: " + str(len(links)))
    return links

def clean_year_range(user_input):
    '''
    Parameters: String object
    Returns two int objects
    '''
    temp_list = user_input.split("-")
    start = int(temp_list[0])
    end = int(temp_list[1])
    return start, end

def clean_search_terms(user_input):
    '''
    Parameters: String object
    Returns: List of Strings
    '''   
    user_input = user_input.strip() 
    temp_list = []
    for i in user_input.split(","):
        i = i.strip()
        temp_list.append(i)
    return temp_list

def get_table_headers(table):
    '''
    Parameters: takes in a soup object
    Returns: List of Strings
    '''
    table_headers = []
    for th in table.find_all("th"):
        table_headers.append(th['class'][0])
    table_headers[0] = 'form_number'
    table_headers[1] = 'form_title'
    return table_headers

def get_number_of_documents_from_search(soup):
    '''
    Reaches into Results and returns total number of files found in search
    '''
    showByColumn = soup.find("th", class_="ShowByColumn")
    value_in_column = showByColumn.get_text().strip().replace('\n', '').replace('\t', '').replace(',', '')
    split_values = value_in_column.split(' ')
    total_num_files = int(split_values[-2])
    return total_num_files 


def get_all_rows_of_data_from_page(table, headers):
    '''
    Acccesses each data cell from table and maps it to the header
    Returns the populated page_table_data = []
    '''
    page_table_data = []
    for tr in table.find_all("tr", {'class': ['even', 'odd']}):
        t_row = {}
        for td, th in zip(tr.find_all("td"), headers):
            t_row[th] = td.text.replace('\n', ' ').replace('\t', ' ').strip()
        page_table_data.append(t_row)
    return page_table_data

def get_all_pages_from_website(get_all, num_files, data, headers, value):
    '''
    Parameters: boolean get_all, int num_files, list data, list headers, string value
    Accesses main page of Prior Form Publications
    Parses out total number of files
    Accesses each of the pages
    Returns modified list data
    '''
    # web page setting: display 200 results per page
    pages = np.arange(200, (num_files + 1), 200)
    # keeping track of pages scraped
    num_pages = 1
    for page in pages:
        print("Scraping new page...")
        if (get_all):
            page = requests.get("https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=" + str(page) + "&criteria=&value=&isDescending=false")
        else:
            page = requests.get("https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=" + str(page) + "&criteria=formNumber&value=" + value + self.descending)
        soup_local = BeautifulSoup(page.content, 'html.parser')
        page_table = soup_local.find("table", class_="picklist-dataTable")
        data += get_all_rows_of_data_from_page(page_table, headers)
        num_pages += 1
        print(str(num_pages) + " pages scrapped so far for " + value + " . Now for a little nap between 2 - 50 seconds.")
        # Be nice to their servers
        sleep(randint(2,50))
    return data

def condense_data_to_include_year_range_with_search_terms(table, term):
    '''
    Parameters: list of dicts : table, boolean : has_search_terms, list of strings : terms
    Iterates through set of scraped data
    Creates list of dicts with year ranges
    Filters to exact matches for form number
    Returns: list of dicts
    '''
    temp_list = []
    keys = [list(table[0])]
    form_num = keys[0][0]
    form_title = keys[0][1]
    year = keys[0][2]
    table_length = len(table)
    first_row = table[0]
    first_dict = dict( [ 
        (form_num, first_row[form_num]),
        (form_title, first_row[form_title]),
        ('min_year', first_row[year]),
        ('max_year', first_row[year])
        ] )
    temp_list.append(first_dict)
    for i in range(table_length):
        if table[i][form_num] == term:
            place_holder = temp_list.pop()
            if ((table[i][form_num] == place_holder[form_num]) & 
                (table[i][form_title] == place_holder[form_title])):
                place_holder['min_year'] = table[i][year]
                temp_list.append(place_holder)
            else:    
                temp_list.append(place_holder)
                temp_dict = dict( [ 
                    (form_num, table[i][form_num]),
                    (form_title, table[i][form_title]),
                    ('min_year', table[i][year]),
                    ('max_year', table[i][year])
                ] )
                temp_list.append(temp_dict)
    if temp_list[0][form_num] != term:
        del temp_list[0]
    return temp_list

def condense_data_to_include_year_range(table):
    '''
    Parameters: list of dicts : table, boolean : has_search_terms, list of strings : terms
    Iterates through set of scraped data
    Creates list of dicts with year ranges for all documents
    Returns: list of dicts
    '''
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
    print("Please select what you want to do: ")
    print("1. Download a json of search results")
    print("2. Download individual pdfs of forms in year range")
    user_choice = input("Choice: ")
    access_object = IRSWebAccessor()
    if user_choice == '1':
        print("Please enter what forms you want returned. Seperate each form with a comma.")
        search_choice = input("Terms: ")
        search_for = clean_search_terms(search_choice)
        access_object.scrape_by_search_terms(search_for)
        print("Please enter the name of the file you want the data written to (ex: test_form.json)")
        file_name = input("File name: ")
        access_object.write_to_json(file_name)
        access_object.clear()
    elif user_choice == '2':
        print("Please enter what form you want downloaded")
        search_choice = input("Terms: ")
        search_for = clean_search_terms(search_choice)
        print("Please enter the year range you want to download (ex: 2001-2017")
        year_choice = input("Years: ")
        year_start, year_end = clean_year_range(year_choice)
        access_object.scrape_by_search_term_and_year_range(search_for, year_start, year_end)
    else:
        print("Sorry, didn't understand that.")

    
    





