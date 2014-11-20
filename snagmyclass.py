import requests
import mechanize
import getpass
import sys
import time
import datetime
from bs4 import BeautifulSoup as bs

SEARCH_URL = "http://onestop2.umn.edu/courseinfo/searchcriteria.jsp?institution=UMNTC"
REGISTER_URL = "https://onestop2.umn.edu/registration/initializeCurrentEnrollment.do?institution=UMNTC&resetInstitut"

TERM = "UMNTC,1153,Spring,2015"
SLEEP_BETWEEN_OPEN_CHECKS = 10800 # in seconds; currently 3 hours
SLEEP_BETWEEN_REGTIME_CHECKS = 300 # in seconds; currently 5 minutes

user = ""
password = ""

br = mechanize.Browser()
br.set_handle_robots(False)

def search(courseNum):
    response = br.open(SEARCH_URL)
    
    # Fill in our search criteria
    br.select_form(name="searchCriteriaForm")
    br["searchTerm"] = [TERM]
    br["searchCatalogNumber"] = courseNum
    
    response = br.submit()
    return response.read()

def isOpen(courseNum, courseID):
    pageText = search(courseNum)
    if courseID in pageText:
        return True
    return False

def login():
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
    pageText = response.read()
    if "login" in pageText.lower():
        if not login():
            raise Exception("Error logging in.")

    for form in br.forms(): # Select the Continue form on the no-Javascript page
        br.form = form
    response = br.submit()  # and click to continue

    for form in br.forms(): # And again. There are two identical pages.
        br.form = form
    response = br.submit()
    pageText = response.read()
    if "current enrollment by term" not in pageText.lower():
        raise Exception("Error reaching registration page.")
    return response.read()

def register(courseID):
    getRegistrationPage()
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
    print "Registration successful!"
    return pageText

def watchTime(courseNum, courseID):
    timeString = raw_input("\nPlease enter your registration date and time\nin the form 'mm-dd HH-MM am/pm': ")
    regTime = datetime.datetime.strptime(timeString, "%m-%d %I-%M %p")
    regTime = regTime.replace(year=2014)
    now = datetime.datetime.now()
    while (now < regTime):
        print "Registration not yet open. Sleeping %i minutes." % (SLEEP_BETWEEN_REGTIME_CHECKS/60)
        time.sleep(SLEEP_BETWEEN_REGTIME_CHECKS)
        now = datetime.datetime.now()
    print "Registration is open!"
    if isOpen(courseNum, courseID):
        print "Course available. Attempting to register."
        register(courseID)
    else:
        print "Course unavailable. Switching to course watch mode."
        watchSlots(courseNum, courseID)


def watchSlots(courseNum, courseID):
    attempts = 0
    while attempts < 24:
        print "Checking availability of " + courseNum
        if isOpen(courseNum, courseID):
            register(courseID)
            break
        else:
            print "No slots open. Sleeping for %i hours." % (SLEEP_BETWEEN_OPEN_CHECKS/60/60)
            time.sleep(SLEEP_BETWEEN_OPEN_CHECKS)
        attempts += 1

def run():
    global user, password
    user = raw_input("Enter your x500 username: ")
    password = getpass.getpass("Enter your x500 password: ")
    print "Testing login..."
    if not login():
        sys.exit("Incorrect login details!")
    else:
        print "Login OK!\n"
    courseNum = raw_input("Enter the course number (including the trailing H, W, or V) that you wish to watch: ").strip()
    courseID = raw_input("Enter the 5-digit course ID for that class: ").strip()
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
