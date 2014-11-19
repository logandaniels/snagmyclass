import requests
import mechanize
import getpass
import sys
import time
from bs4 import BeautifulSoup as bs

SEARCH_URL = "http://onestop2.umn.edu/courseinfo/searchcriteria.jsp?institution=UMNTC"
REGISTER_URL = "https://onestop2.umn.edu/registration/initializeCurrentEnrollment.do?institution=UMNTC&resetInstitut"

TERM = "UMNTC,1153,Spring,2015"

user = ""
password = ""
courseNum = ""
courseID = ""

br = mechanize.Browser()
br.set_handle_robots(False)

def search(courseNum):
    response = br.open(SEARCH_URL)
    
    # Fill in our search criteria
    br.select_form(name="searchCriteriaForm")
    br["searchTerm"] = [TERM]
    br["searchCatalogNumber"] = str(courseNum)
    
    response = br.submit()
    return response.read()

def isOpen(courseNum):
    pageText = search(courseNum)
    if str(courseID) in pageText:
        return True
    return False

def testLogin():
    response = br.open(REGISTER_URL)
    br.select_form(name="lform") # Select the login form
    br["j_username"] = user
    br["j_password"] = password
    response = br.submit()

    if "Incorrect ID/Password" in response.read():
       return False
    return True

def getRegistrationPage():
    response = br.open(REGISTER_URL)
    br.select_form(name="lform") # Select the login form
    br["j_username"] = user
    br["j_password"] = password
    response = br.submit()

    if "Incorrect ID/Password" in response.read():
        raise Exception("Incorrect login information")

    for form in br.forms(): # Select the Continue form on the no-Javascript page
        br.form = form
    response = br.submit()  # and click to continue

    for form in br.forms(): # And again. There are two identical pages.
        br.form = form
    response = br.submit() 
    return response.read()

def register(courseID):
    br.select_form(name="addNowForm") # Select the course add form
    br["courseNbr"] = courseID
    response = br.submit()

    # Grading basis
    br.select_form(name="addClassStep2")
    br["gBasis"] = ["A-F"]  # Can support pass/fail later

    response = br.submit()  # Submit form to finalize course add
    pageText = response.read()
    if "error" in pageText.lower() or courseID not in pageText:
        raise Exception("Error registering for class.")
    return pageText

def watchTime(courseNum, courseID):
    pass

def watchSlots(courseNum, courseID):
    pass

def run():
    global user, password
    user = raw_input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    print "Testing login...\n"
    if not testLogin():
        sys.exit("Incorrect login details!")
    else:
        print "Login OK!"
    courseNum = raw_input("Enter the course number (including the trailing H, W, or V) that you wish to watch: ").strip()
    courseID = raw_input("Enter the 5-digit course ID for that class: ").strip()i
    print "\n" + "Would you like to register:\n" +"\t(1) When your registration time occurs\n" + "\t(2) As soon as a slot opens up"
    mode = raw_input("[Enter a number:] ")
    if mode == "1":
        watchTime(courseNum, courseID)
    elif mode == "2":
        watchSlots(courseNum, courseID)
    else:
        sys.exit("Invalid choice.")




if __name__ == "__main__":
    run()
