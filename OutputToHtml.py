import json, io, sys


def openTag(tag):
    return "<" + tag + ">"


def closeTag(tag):
    return "</" + tag + ">"


def readFile(filename):
    with io.open(filename, 'r', encoding="utf-8") as file:
        try:
            result = file.read()
            return result.replace('<', "&lt").replace('>', "&gt").replace('\n', '<br>')
        except:
            print("error in opening file: " + filename + " in utf8 mode")
            exit(1)


def addIssue(file, issue, filename):
    fileSplit = file.split("<br>")
    className = ''
    if issue['checkerProperties']['impact'] == 'High':
        className = 'issue-high'
    elif issue['checkerProperties']['impact'] == 'Medium':
        className = 'issue-medium'
    else:
        className = 'issue-low'
    # print(issue)
    cid = str(issue['stateOnServer']["cid"])
    owner = issue['stateOnServer']['triage']["owner"]
    impact = issue['checkerProperties']['impact']
    eventDescriptor = next(obj for obj in issue['events'] if obj["main"]==True)
    issueResultstr = "<p class='"+className+"' id='"+str(issue['stateOnServer']["cid"])+"'>#issue " + impact +" cid " + cid +": " + eventDescriptor["eventDescription"]+"</p>"
    issues[issue['stateOnServer']["cid"]] = {
        'Type': issue['checkerName'],
        'File': filename,
        'Classification': issue['stateOnServer']['triage']['classification'],
        'Impact': impact,
        'Owner': owner,
        
    }
    try:
        fileSplit.insert(issue['mainEventLineNumber'], issueResultstr)
        result = "<br>".join(fileSplit)
    except:
        result = file
    return result


def sortIssue(e):
    return e["mainEventLineNumber"]


def script():
    result = ''
    with open("script.js", 'r') as file:
        result = file.read()
    output = openTag("script")
    output += result
    output += closeTag("script")
    return output

def style():
    result = ''
    with open("style.css", 'r') as file:
        result = file.read()
    output = openTag("style")
    output += result
    output += closeTag("style")
    return output


files = {}
issues = {}
hasIssues = False

with open("output.json") as f:
    data = json.load(f)
    data["issues"].sort(reverse=True, key=sortIssue)
    if (len(data["issues"]) > 0):
        hasIssues = True
        for issue in data["issues"]:
            if issue["strippedMainEventFilePathname"] not in files:
                result = readFile(issue["mainEventFilePathname"])
                files[issue["strippedMainEventFilePathname"]] = result
            files[issue["strippedMainEventFilePathname"]] = addIssue(files[issue["strippedMainEventFilePathname"]], issue, issue["strippedMainEventFilePathname"])
    else:
        print("No issues found")



def main(args):
    outputHtml = ""
    outputHtml += openTag("html")
    outputHtml += openTag("head")
    outputHtml += '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">'
    outputHtml += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">'
    #outputHtml += '<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/default.min.css">'
    #outputHtml += '<script src="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/highlight.min.js"></script>'
    outputHtml += '<script src="https://cdnjs.cloudflare.com/ajax/libs/split.js/1.5.11/split.min.js"></script>'
    outputHtml += style()
    outputHtml += closeTag("head")
    outputHtml += openTag("body")

    outputHtml += openTag('div class="split column" id="one"')
    if(hasIssues):
        outputHtml += openTag('table class="table table-hover"')
        outputHtml += openTag('thead class="thead-dark"')
        outputHtml += openTag('tr')
        outputHtml += openTag('th scope="col"')
        outputHtml += "CID"
        outputHtml += closeTag('th')
        outputHtml += openTag('th scope="col" class="sortable"')
        outputHtml += "Impact"
        outputHtml += closeTag('th')
        outputHtml += openTag('th scope="col"')
        outputHtml += "Classification"
        outputHtml += closeTag('th')
        outputHtml += openTag('th scope="col" class="sortable"')
        outputHtml += "Type"
        outputHtml += closeTag('th')
        outputHtml += openTag('th scope="col" class="sortable"')
        outputHtml += "Owner"
        outputHtml += closeTag('th')
        outputHtml += openTag('th scope="col" class="sortable"')
        outputHtml += "File Name"
        outputHtml += closeTag('th')
        outputHtml += closeTag('tr')
        outputHtml += closeTag('thead')
        outputHtml += openTag('tbody')
        for issue in issues:
            trAtr = "id='li." + issues[issue]['File'].replace("\\", ".") + '.' + str(issue) + "'" + "onclick='showById(" + '"' + issues[issue]['File'].replace("\\", ".") + '", "' + str(issue) + '"' + ")'"
            if issues[issue]['Impact'] == 'High':
                outputHtml += openTag("tr " + 'class="table-danger trow" ' + trAtr)
            elif issues[issue]['Impact'] == 'Medium':
                outputHtml += openTag("tr " + 'class="table-warning trow" ' + trAtr)
            else:
                outputHtml += openTag("tr " + 'class="table-success trow" ' + trAtr)
            outputHtml += openTag('td')
            outputHtml += str(issue)
            #outputHtml += openTag("li class='list-group-item list-group-item-action' id='li." + file.replace("\\", ".") + "'" + "onclick='showById(" + '"' + file.replace("\\", ".") + '"' + ")'")
            #outputHtml += file
            #outputHtml += closeTag("li")
            outputHtml += closeTag('td')
            outputHtml += openTag('td')
            outputHtml += issues[issue]['Impact']
            outputHtml += closeTag('td')
            outputHtml += openTag('td')
            outputHtml += issues[issue]['Classification']
            outputHtml += closeTag('td')
            outputHtml += openTag('td')
            outputHtml += issues[issue]['Type']
            outputHtml += closeTag('td')
            outputHtml += openTag('td')
            outputHtml += issues[issue]['Owner']
            outputHtml += closeTag('td')
            outputHtml += openTag('td')
            index = issues[issue]['File'].rfind('\\') + 1
            outputHtml += issues[issue]['File'][index:]
            outputHtml += closeTag('td')
            outputHtml += closeTag('tr')
        outputHtml += closeTag('tbody')
        outputHtml += closeTag('table')
    else:
        outputHtml += u"No defects found"
    outputHtml += closeTag('div')

    outputHtml += openTag('div class="split column" id="two"')
    outputHtml += openTag("pre")
    #outputHtml += openTag('div class="scrollButtons"')
    #outputHtml += openTag("button onclick='prevIssue()'")
    #outputHtml += "prev"
    #outputHtml += closeTag("button")
    #outputHtml += openTag("button onclick='nextIssue()'")
    #outputHtml += "next"
    #outputHtml += closeTag("button")
    #outputHtml += closeTag('div')
    for file in files:
        outputHtml += openTag("code class='hidden' id='" + file.replace("\\", ".") + "'")
        try:
            outputHtml += files[file]
        except:
            print(file)
        outputHtml += closeTag("code")
    outputHtml += closeTag("pre")
    outputHtml += closeTag("div")

    outputHtml += script()
    #outputHtml += '<script>hljs.initHighlightingOnLoad();</script>'
    outputHtml += closeTag("body")
    outputHtml += closeTag("html")
    with io.open("output.html", 'w+', encoding='utf-8') as output:
        output.write(outputHtml)

if __name__ == '__main__':
    main(sys.argv)