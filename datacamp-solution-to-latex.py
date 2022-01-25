import requests
import re
import html
from urllib.parse import urlparse, parse_qs
import difflib
import csv
from io import StringIO

# data is provided by Datacamp in a weired mixture of JSON and CSV, so I wrote my own function so find specific information
def findString(result, search):
    returnList = []
    data = StringIO(result)
    reader = csv.reader(data, delimiter=',')
    for row in reader:
        indices = [i for i, value in enumerate(row) if value == search]
        for index in indices:
            returnList.append(row[index + 1])
    return returnList

def makeListUnique(list):
    returnList = []
    for i in list:
        if i not in returnList:
            returnList.append(i)
    return returnList

url = "https://campus.datacamp.com/courses/ai-fundamentals/introduction-to-ai?ex=4"
req = requests.get(url)
result = html.unescape(re.search("window.PRELOADED_STATE = (.*)</script>", req.text).group(1)[:-1]).replace('\\"', "'").replace("\\'", "'").replace('\\\\t', '  ')

previousChapter = ""
latexString = ""
title = ""

urls = [url.split("]")[0] for url in findString(result, "url")]

#for line in findString(result, "solution")[2].split('\\\\n'):
#    print(line)
for url in makeListUnique(urls):
    req = requests.get(url)
    result = html.unescape(re.search("window.PRELOADED_STATE = (.*)</script>", req.text).group(1)[:-1]).replace('\\"', "'").replace("\\'", "'").replace('\\\\t', '  ')

    # process information from URL
    titleraw = url.split("/")[4].replace("-", " ")
    chapterraw = url.split("/")[5].split("?")[0].replace("-", " ")
    parsed_url = urlparse(url)
    exercise = int(parse_qs(parsed_url.query)['ex'][0])

    # get solution
    solLines = [line for line in findString(result, "solution")[exercise - 1].split('\\\\n')]

    # find exact titles for exercise
    titles = list(filter(lambda a: a != 'null', findString(result, "title")))
    try:
        title = difflib.get_close_matches(titleraw, titles)[0]
    except:
        if title == "":
            title = input("Title: ")
    try:
        chapter = difflib.get_close_matches(chapterraw, titles)[0]
    except:
        chapter = "unknown"
    try:
        exerciseTitle = titles[titles.index(chapter) + exercise]
    except:
        exerciseTitle = "unknown"

    #print(titles)
    print(title + " - " + chapter + " - " + exerciseTitle + " (" + str(exercise) + ")" + " - " + url)
    for line in solLines:
        print(line)

    # generate Latex
    if solLines[0] != '':
        if previousChapter != chapter:
            latexString = latexString + r"\section{" + chapter + r"}" + "\n"
        latexString = latexString + r"\subsection{" + exerciseTitle + r"}" + "\n"
        latexString = latexString + r"\begin{lstlisting}[tabsize=2]" + "\n"
        for line in solLines:
            latexString = latexString + line + "\n"
        latexString = latexString + r"\end{lstlisting}" + "\n"
        latexString = latexString + "\n"
        previousChapter = chapter

# produce Latex file
with open("template.tex", "rt") as fin:
        with open(title + ".tex", "wt") as fout:
            for line in fin:
                fout.write(line.replace('{title}', str(title))
                .replace('{solutions}', str(latexString.replace("&", "\&"))))