import os
from src.scrape_data import IRSWebAccessor, clean_search_terms, clean_year_range

def prompt_for_search_terms(single_or_multi):
    if single_or_multi == "multi":
        print("Please enter what forms you want returned. Seperate each form with a comma.")
        choice = input("Forms: ")
    else:
        print("Please enter what form you want returned.")
        choice = input("Form: ")        
    return choice

def prompt_for_year_range():
    print("Please enter the year range you want to download (ex: 2001-2017")
    year_choice = input("Years: ")
    year_start, year_end = clean_year_range(year_choice)
    return year_start, year_end    

def prompt_for_file_name():
    print("I will write your file to the data sub-folder.")
    print("Please enter the name of the file you want the data written to (ex: test_form.json)")
    file_name = input("File name: ")
    return file_name

if __name__ == "__main__":
    print("Program launching...")
    print("Please select what you want to do: ")
    print("1. Download a json of search results")
    print("2. Download individual pdfs of forms in year range")

    user_choice = input("Choice: ")
    access_object = IRSWebAccessor()

    if user_choice == '1':  
        user_input = prompt_for_search_terms("multi")
        search_for = clean_search_terms(user_input)
        # Scrape Data
        access_object.scrape_by_search_terms(search_for)
        file_name = prompt_for_file_name()
        access_object.write_to_json(file_name)
        # Clear Data
        access_object.clear()
    elif user_choice == '2':
        user_input = prompt_for_search_terms("single")
        search_for = clean_search_terms(user_input)
        year_start, year_end = prompt_for_year_range()
        access_object.scrape_by_search_term_and_year_range(search_for, year_start, year_end)
    else:
        print("Sorry, didn't understand that.")        