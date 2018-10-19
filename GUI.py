from Tkinter import *
import preprocess

app_window = Tk()

w, h = app_window.winfo_screenwidth(), app_window.winfo_screenheight()
app_window.geometry("%dx%d+0+0" % (w, h))

doc = ""

gap3 = LabelFrame(app_window, width = 200, height = 50, bd = 0)
repo = Frame(app_window, width = 200, height = 50)
gap1 = LabelFrame(app_window, width = 800, height = 100, bd = 0)
gap2 = LabelFrame(app_window, width = 200, height = 50, bd = 0)
search = Frame(app_window)
result = LabelFrame(app_window)
flag = 0

def defaultRepo():
    global flag
    flag = preprocess.defaultLists(flag)
    if flag == 0 :
        setRepo()
        
def setRepo():
    repo_path = repo_entry.get()
    preprocess.preprocessing(repo_path)

repo_label = Label(repo, text = "    Enter repository path:  ")
repo_entry = Entry(repo, width = 50)
repo_button = Button(repo, text = "Load corpus", command = defaultRepo, width = 10, height = 1)

repo_label.pack(side = LEFT)
repo_entry.pack(side = LEFT)
repo_button.pack(side = LEFT)

def searchQuery():
    query = query_entry.get()
    global doc
    doc = preprocess.querying(query)
    result_doc.config(text = doc)

query_label = Label(search, text = "                         Search:  ")
query_entry = Entry(search, width = 50)
query_button = Button(search, text = "Search", command = searchQuery, width = 10, height = 1)
query_label.pack(side = LEFT)
query_entry.pack(side = LEFT)
query_button.pack()

result_doc = Message(result, text = doc, width = 1000, relief = RAISED)
result_label = Label(result, text="Result Document IDs")
result_label.pack(side = TOP)
result_doc.pack(fill = BOTH, expand = YES)

gap3.pack()
repo.pack()
gap1.pack()
search.pack()
gap2.pack()
result.pack(fill = "both", expand = "yes")




app_window.mainloop()
