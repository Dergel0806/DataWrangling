import PyPDF2
import pandas as pd
import re
import glob
from itertools import compress

rowsList = []
for pdf in glob.glob('./syllabi/*.pdf'):
    file = open(pdf, 'rb')
    fileReader = PyPDF2.PdfFileReader(file)

    text = ''
    for i in range(fileReader.numPages):
        text += fileReader.getPage(i).extractText()
    text = text.replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    while " ." in text:
        text = text.replace(" .", ".")   
            
    emails = re.findall('(?:\s|\))(\w+?@[\w.]+?\.\w+?)(?:\s|\))', text)
    links = re.findall('\s((?:(?:https?://)|(?:www\.))[\w\./~]+?)\s', text)
    time = re.findall('(?i)(?:1[0-2]|[0-9]|2[0-4]) ?: ?[0-6][0-9](?:\s?(?:p|a)m)?', text)
    timeRange = re.findall('(?i)(?:1[0-2]|[0-9]|2[0-4])(?::[0-6][0-9])?\s?-\s?(?:1[0-2]|[0-9]|2[0-4]) ?: ?[0-6][0-9](?:\s?(?:p|a)m)?', text)
    phone = re.findall('(?:\+?\d(?:-|\.)?)?(?:(?:\(\d{3}\))|(?:\d{3}))(?:-|\.)?\d{3}(?:-|\.)?\d{4}', text)
    weights = re.findall('\d{1,3}%', text)
    points = re.findall('\d{1,3} (?:points|pts)', text)
    isbn = re.findall('(?i)ISBN(?:13)?:? ([\d\-a-z]{10,})', text)
    terms = re.findall('(?i)(?:(?:Fall)|(?:Spring)|(?:Summer)|(?:Winter)) ?\d{2,4}', text)
    
    monthPattern = '(?:(?:Oct(?:(?:ober)|\.))|(?:Sep(?:(?:tember)|\.))|(?:Nov(?:(?:ember)|\.))|(?:Dec(?:(?:ember)|\.))|(?:Jan(?:(?:uary)\.))|(?:Feb(?:(?:ruary)|\.))|(?:Mar(?:(?:ch)|\.))|(?:May)|(?:June)|(?:July)|(?:Aug(?:(?:ust)|\.))|(?:Apr(?:(?:il)|\.)))'
    datePattern1 = '(?:\d{2}/\d{2}/(?:\d{2}|\d{4}))'
    datePattern2 = monthPattern + ' ?\d{2}(?:,? ?(?:\d{2}|\d{4}))?'
    dates = re.findall('(?i)(' + datePattern1 + '|' + datePattern2 +')', text)
       
    codes = re.findall('[A-Z]{2,}(?:-| )?\d{2,5}(?:[-\d\/]+)?', text)
    stopWords = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', 'ISBN', 'FALL', 'SPRING', 'SUMMER', 'EXAM']
    codes = list(compress(codes, [not any([word in code for word in stopWords]) for code in codes]))
    
    rooms = re.findall('(?i)Room\s?\d{1,3}[a-z]?', text)
    offices = re.findall('(?:O|o)(?:F|f)(?:F|f)(?:I|i)(?:C|c)(?:E|e):?\s([A-Z][a-z]+ ?\d{1,})', text)
    locations = []
    locations += rooms
    locations += offices
    
    instructor = re.findall('(?:Instructor|Coordinator):\s([A-Z][a-z]+\s[A-Z](?:[a-z]+|\.)(?:\s[A-Z][a-z]+)?)', text)
    if len(instructor) > 0:
        while('Email' in instructor[0]):
            instructor[0] = instructor[0].replace('Email', '')
        while('Office' in instructor[0]):
            instructor[0] = instructor[0].replace('Office', '')
    
    department = re.findall('Department(?:\sof|:)\s((?:[A-Z][a-z]+\s?)+)', text)
    
#     surnames = re.findall('Mrs?\. ([A-Z][a-z]+) ', text)

    hours = re.findall('(?i)((?:hours: \d+)|(?:\d+ hours))', text)
    credits = re.findall('(?i)((?:Credits:\s?\d{1,2})|(?:[1-9]\d?\scredits?))', text)
    credits += hours
    
    years = re.findall('(?:(?:199)|(?:20(?:0|1|2)))\d', text)
    
    assignments = re.findall('(?i)Assignment', text)
    reports = re.findall('(?i)Report', text)
    presentations = re.findall('(?i)Presentation', text)
    nHW = len(assignments) + len(reports) + len(presentations)
    
    literature = re.findall('((?:[A-Z][a-z]+),?\s?-?(?:[A-Z][a-z]*\.?)+[ ,\.&]{1,3})+(\(?(?:(?:199)|(?:20(?:0|1|2)))\d\)\.?)? ([A-Z[a-z]+:?( [A-Za-z:]+)+)', text)
    
    address = re.findall('(?:\d+\s)?(?:[A-Z][a-z]+\sSt)|(?:[A-Z][a-z]+\sAve)|(?:[A-Z][a-z]+\sWay)', text)
    
    row = {'emails':str(emails), 
           'links':str(links),
           'time':str(time),
           'timeRange':str(timeRange),
           'phone':str(phone),
           'weights':str(weights),
           'points':str(points),
           'ISBNs':str(isbn),
           'terms':str(terms), 
           'dates':str(dates), 
           'credits': str(credits), 
           'codes': str(codes), 
           'locations': str(locations), 
           'instructor': str(instructor), 
           'department':str(department), 
#            'surnames': str(surnames),
           'number of HWs': str(nHW),
           'years': str(years),
           'literature': str(literature),
           'address': str(address)
          }
    rowsList.append(row)
    
features = pd.DataFrame(rowsList) 
features.insert(0, 'FileName', [re.findall('\./syllabi\\\\(.+)\.pdf', pdf)[0] for pdf in glob.glob('./syllabi/*.pdf')])

features.to_csv('features-retrieved-by-IhorMarkevych.csv', index=False, header=False)