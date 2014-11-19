import requests
import mechanize
from bs4 import BeautifulSoup as bs

br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_refresh(False)

def search(br, courseNum):
    response = br.open(
            "http://onestop2.umn.edu/courseinfo/searchcriteria.jsp?institution=UMNTC")
    
    # Fill in search criteria
    br.select_form(name="searchCriteriaForm")
    br["searchTerm"] = ["UMNTC,1153,Spring,2015"]
    br["searchCatalogNumber"] = str(courseNum)
    
    response = br.submit()
    return response.read()

def isOpen(br, courseNum, courseID):
    pageText = search(br, courseNum)
    if str(courseID) in pageText:
        return True
    return False

def register(br, user, password):
    br.select_form(name="lform")
    br["j_username"] = user
    br["j_password"] = password
    
    response = br.submit()
    for form in br.forms():
        br.form = form
    response = br.submit()
    print response.read()
