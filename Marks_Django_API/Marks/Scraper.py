from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import json
import os
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")

BASE = "http://www.vitol.ac.in"
LOGIN = BASE + "/login"
DASHBOARD = BASE + "/dashboard"
Dict = {}
Course_page = {}
Course_data = {}
Course_list = []
errmsg = "Wrong Credentials \n Excessive login failure will blocked your account temporarily."
def parser(quiz, dict):
    temp_dict = {}
    quiz_avg = dict[quiz][-1:][0].split(" ")[3]
    for marks in dict[quiz]:
        sub_dict = {}
        group = marks.split(' ')
        if (len(group) > 6):
            sub_dict['Scored_marks'] = group[len(group) - 1][group[len(group) - 1].find("(") + 1:group[len(group) - 1].find(")")].split("/")[0]
            sub_dict['Max_marks'] = group[len(group) - 1][group[len(group) - 1].find("(") + 1:group[len(group) - 1].find(")")].split("/")[1]
            sub_dict['percentage'] = group[len(group) - 2]
            temp = "Quiz-" + group[1]
            temp_dict[temp] = sub_dict
    # Dict[key]['Quiz'] = temp_dict
    # Dict[key]['Quiz']['Quiz Average'] = quiz_avg
    return [temp_dict, quiz_avg]

def Scrapy(Username,Password):
    driver = webdriver.Chrome(executable_path="C:/Users/Lenovo/Desktop/chromedriver_win32/chromedriver.exe",
                              options=chrome_options)
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options)
    driver.get(LOGIN)
    driver.find_element_by_name("email").send_keys(Username)
    driver.find_element_by_name("password").send_keys(Password)
    driver.find_element_by_class_name("login-button").click()

    time.sleep(1)
    try:
        driver.get(DASHBOARD)
        DASHBOARD_PAGE = driver.page_source
        DASHBOARD_DATA = BeautifulSoup(DASHBOARD_PAGE, 'html.parser')

        Dict['Username'] = DASHBOARD_DATA.find('span', attrs={'class': 'username'}).text
        Course_Parent = DASHBOARD_DATA.select('h3', attrs={'class': 'course-title'})
    except:
        return (errmsg)
    for item in range(0, len(Course_Parent)):
        sub_dict = {}
        sub_dict['title'] = Course_Parent[item].find('a').text
        sub_dict['code'] = Course_Parent[item].find('a')['data-course-key'].split('+')[1]
        sub_dict['link'] = Course_Parent[item].find('a')['href'][:-7]
        Dict[item + 1] = sub_dict
    # print(Dict)
    Course_list = list(Dict.keys())[1:]
    for key in Course_list:
        link = BASE + Dict[key]['link'] + "progress"
        driver.get(link)
        time.sleep(1)

        Course_page = driver.page_source
        Course_data = BeautifulSoup(Course_page, 'html.parser')
        p = re.compile('var detail_tooltips = (.*);')

        for script in Course_data.find_all("script", {"src": False}):
            if p.search(script.string):
                m = script.string
                lower_index = m.find('var detail_tooltips = {')
                upper_index = m.find(';', lower_index)
                # print(lower_index)
                # print(upper_index)
                m = m[lower_index + 22:upper_index]
                m = json.loads(m)
                # print(m)

                Credit = str(Course_data.select('div p'))
                if (Credit.find('Quiz(1-9)') > 0):
                    Dict[key]['Credit'] = 3
                    quiz = "Quiz(1-9)"
                    [Dict[key]['Quiz'], Dict[key]['Quiz']['Quiz Average']] = parser(quiz, m)
                elif (Credit.find('Quiz(1-9)') < 0):
                    Dict[key]['Credit'] = 4
                    if 'Quiz(1-12)' in m.keys():
                        quiz = "Quiz(1-12)"
                        [Dict[key]['Quiz'], Dict[key]['Quiz']['Quiz Average']] = parser(quiz, m)
                    else:
                        quiz = "Quiz"
                        [Dict[key]['Quiz'], Dict[key]['Quiz']['Quiz Average']] = parser(quiz, m)
                else:
                    Dict[key]['Credit'] = 2
                    quiz = "Quiz(1-6)"
                    [Dict[key]['Quiz'], Dict[key]['Quiz']['Quiz Average']] = parser(quiz, m)

                #######################################   Assignment     ############################################
                temp_dict = {}
                for mark in m['Digital Assignment']:
                    asgn_avg = m['Digital Assignment'][-1].split(" ")[4]
                    sub_dict = {}
                    group = mark.split(" ")
                    if (len(group) > 7):
                        sub_dict['Scored_marks'] = \
                            group[len(group) - 1][
                            group[len(group) - 1].find("(") + 1:group[len(group) - 1].find(")")].split(
                                "/")[0]
                        sub_dict['Max_marks'] = \
                            group[len(group) - 1][
                            group[len(group) - 1].find("(") + 1:group[len(group) - 1].find(")")].split(
                                "/")[1]
                        sub_dict['Percentage'] = group[len(group) - 2]
                        temp_dict["DA" + group[2]] = sub_dict

                Dict[key]['Digital Assignment'] = temp_dict
                Dict[key]['Digital Assignment']['Average'] = asgn_avg
                #######################################   Assignment     ############################################
            else:
                Dict[key]['Quiz'] = "It seems today is the Quiz day. All the best for quiz."
        # print("Dictionary Starts Here")
        # print(Dict)
    driver.quit()
    return Dict

