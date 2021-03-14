IRS Tax Form Utility Project
Python 3.7.6

How to Run:
The command-line application is run from the  app.py file by calling 'python app.py' within the terminal.

---

File Structure:
The app.py file imports a utility class from the src folder and writes files to the data folder.
There are two built-in .json files and three .pdf files to write to when running the application.

IRSPriorYearFormApplicaton
|- app.py
|- src
|   |- scrape_data.py
|
|- data
|   |- irs_forms.json
|   |- test_form.json
|   |- test_1.pdf
|   |- test_2.pdf
|   |- test_3.pdf
|
|- README.txt
|- requirements.txt
|- README.md (for GitHub)

---

Thoughts
It had been a hot minute since I had worked in Python, so I found this really fun!
I would be interested in learning more about how testing happens within Python since 
JUnit testing within my Java applications has become an essential part of my coding process.

I used this challenge as inspiration for my weekend homework project for creating a full-stack application
that can perform CRUD on a database.  
https://github.com/A-Hanson/JPACRUDProject