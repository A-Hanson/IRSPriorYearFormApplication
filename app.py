import os
from src.scrape_data import IRSWebAccessor, clean_search_terms

def prompt_for_search_terms():
    print("Please enter what forms you want returned. Seperate each form with a comma.")
    choice = input("Terms: ")
    return choice

def prompt_for_file_name():
    print("I will write your file to the data sub-folder.")
    print("Please enter the name of the file you want the data written to (ex: test_form.json)")
    file_name = input("File name: ")
    return file_name

if __name__ == "__main__":
    print("Program launching...")
    print("Enter q to quit at any time")

    access_object = IRSWebAccessor()
    user_input = prompt_for_search_terms()

    #Scrape Data
    search_for = clean_search_terms(user_input)
    access_object.scrape_by_search_terms(search_for)
    file_name = prompt_for_file_name()
    access_object.write_to_json(file_name)