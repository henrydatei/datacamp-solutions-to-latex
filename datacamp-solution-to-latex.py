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

url = "https://campus.datacamp.com/courses/data-types-for-data-science-in-python/fundamental-data-types?ex=2"
req = requests.get(url)
result = html.unescape(re.search("window.PRELOADED_STATE = (.*)</script>", req.text).group(1)[:-1])

previousChapter = ""
latexString = ""

urls = [url.split("]")[0] for url in findString(result, "url")]
for url in makeListUnique(urls):
    req = requests.get(url)
    result = html.unescape(re.search("window.PRELOADED_STATE = (.*)</script>", req.text).group(1)[:-1])

    # process information from URL
    titleraw = url.split("/")[4].replace("-", " ")
    chapterraw = url.split("/")[5].split("?")[0].replace("-", " ")
    parsed_url = urlparse(url)
    exercise = int(parse_qs(parsed_url.query)['ex'][0])

    # get solution
    solLines = findString(result, "solution")[exercise - 1].split('\\\\n')

    # find exact titles for exercise
    titles = findString(result, "title")
    title = difflib.get_close_matches(titleraw, titles)[0]
    chapter = difflib.get_close_matches(chapterraw, titles)[0]
    exerciseTitle = titles[titles.index(chapter) + exercise]

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
                .replace('{solutions}', str(latexString)))