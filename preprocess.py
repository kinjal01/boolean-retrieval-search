import nltk, os, math, pickle
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import *
from collections import defaultdict

file = {} #file is a dictionary which holds all the docs. Its index is the docID
fileopen = {} #Stores all the open files
file_content = {}   #It is a dictionary which holds the contents of each file
file_tokenize = {}  #Dictionary to hold the tokenized words
file_stop = {}  #Holds the set of words after removal of stop words
file_stem = {}  #Holds the set of words after stemming
file_count = 0  #Holds the count of number of documents in the directory

term_freq = {}  #Holds the term frequency of each word in each document
term_pos = {} #Holds the positions of occurance of the term in each document

posting_list = defaultdict(list) #Holds the word name and the doc ID
word_unique = []    #Holds the unique words in the posting list
query_tokenize = [] #Holds the tokenized terms of the query
query_stop = []
query_stem = []

match_list = [] #Holds the posting list for all the words. It is designed to be a list of lists
final_list = [] #List which holds the final list of docID's

word_full_unique = []   #Holds all the unique complete words (Not stemmed)
final_wildcard_list = [] #Holds the final wildcard list

punctuation = ['.', ',', '(', ')', ":", ";"] #List of all punctuations
stray_chars = ['..', '==', '++', '--', '//', '``'] #List of stray characters which must be removeds
stemmer = PorterStemmer()

def defaultLists(get_flag):
    flag = get_flag
    flag = 0
    path_object = os.getcwd()
    path_object += "\f_file"
    if (os.path.exists(path_object)):
        flag = 1
        return flag
    else:
        file_name = "f_file"
        fileObject = open(file_name, 'wb')
        pickle.dump(file, fileObject)
        fileObject.close()

        file_name = "f_stop"
        fileObject = open(file_name, 'wb')
        pickle.dump(file_stop, fileObject)
        fileObject.close()

        file_name = "f_word_unique"
        fileObject = open(file_name, 'wb')
        pickle.dump(word_unique, fileObject)
        fileObject.close()

        file_name = "f_word_full_unique"
        fileObject = open(file_name, 'wb')
        pickle.dump(word_full_unique, fileObject)
        fileObject.close()

        file_name = "t_freq"
        fileObject = open(file_name, 'wb')
        pickle.dump(term_freq, fileObject)
        fileObject.close()

        file_name = "t_pos"
        fileObject = open(file_name, 'wb')
        pickle.dump(term_pos, fileObject)
        fileObject.close()

        file_name = "p_list"
        fileObject = open(file_name, 'wb')
        pickle.dump(posting_list, fileObject)
        fileObject.close()
        
        return flag
    
def preprocessing(get_path):
    
    global word_full_unique
    global word_unique
    global file_count
    global file_tokenize
    path= get_path
    
    docID = 1 #docID gives the ID's to the documents
    for filename in os.listdir(path):
        file[docID] = filename
        docID = docID+1

    file_count = len(file) #Get count of number of files in the folder

    for i in range(1, file_count+1):
        print(i)
        if (file[i].endswith(".txt")): #Open the files
            fileopen[i] = open(path + file[i])
            file_content = fileopen[i].read()

        file_content = file_content.lower() #Make the docs into lowercase
        file_tokenize[i] = word_tokenize(file_content) #Tokenize each file

        file_stem = [stemmer.stem(word) for word in file_tokenize[i]] #Porter Stemmer
        file_stop[i] = [word for word in file_stem if (word not in stopwords.words('english') and word not in punctuation)] #Remove stop words and punctuations

        #Remove multi-character punctuations
        for word in file_stop[i]:
            for stray in stray_chars:
                if stray in word:
                    while word in file_stop[i]:
                        file_stop[i].remove(word)
        
        #Store index of each word
        term_pos_temp = {}
        term_freq_temp = {}
        for term in file_stop[i]:
            index_list = []
            for index, k in enumerate(file_stop[i]):
                if k == term:
                    index_list.append(index)
            term_pos_temp[term] = index_list
            term_freq_temp[term] = len(index_list)
            
        term_pos[i] = term_pos_temp #This dict stores the index of each word. This is per document
        term_freq[i] = term_freq_temp   

    for i in range(1, file_count+1):
        for term in file_tokenize[i]:
            word_full_unique.append(term)

    word_full_unique = list(set(word_full_unique))

    file_tokenize = {} #Clear file_tokenize dictionary

    for i in range(1, file_count+1): #Create posting list
        unique = list(set(file_stop[i]))
        for word in unique:
            posting_list[word].append(i)
            
    for i in range(1, file_count+1): #Sort posting list
        unique = list(set(file_stop[i]))
        for word in unique:
            word_unique.insert(0, word)
            posting_list[word].sort()

    word_unique = list(set(word_unique))
    
def querying(get_query):

    global posting_list
    global final_list
    global file_count

    result_count = -1
    query = get_query
    query_tokenize = [] #Holds the tokenized terms of the query
    query_stop = []     #Holds the stop words of the query
    query_stem = []     #Holds the stemmed query words
    final_list = []     
    tf_idf = {}

    query_tokenize = word_tokenize(query)   #Tokenize the query
    query_stop = [word for word in query_tokenize if (word not in stopwords.words('english') and word not in punctuation)]  #Remove stop words from query	
		
    #Apply Porter Stemmer iff the word is not a wildcard query
    for word in query_stop:
        if '*' in word:
            query_stem.append(word)
        else:
            word = stemmer.stem(word) #Porter Stemmer for words in query that have no wildcard character
            query_stem.append(word)

    print("Query")
    print(query_stem)

    flag = 0    #0 means AND(default), 1 means OR, -1 means NOT
    flag_prox = False
    flag_prox_check = False
    diff = -1

    for index, word in enumerate(query_stem):
        if(word in word_unique):
            temp = posting_list[word] #Holds the posting list for a given word
                    
            if not final_list and flag != -1: #Check if the list is empty
                final_list = temp #Directly insert the posting list

            elif not final_list and flag == -1 and not flag_prox_check: #If -- is the first token in the query (i.e. the final_list is empty and you get --)
                for i in range(1, file_count+1):
                    final_list.append(i)
                final_list.sort()
                for doc_id in temp:
                    print(final_list)
                    if doc_id in final_list:
                        final_list.remove(doc_id)
                flag = 0    #Resetting flag to 0
                        
            else:
                if(flag == 0 and not flag_prox):  #++ is present (AND operation)
                    temp1 = []
                    for doc_id in temp: #ANDing the posting list obtained till then and the posting list of the word
                        if doc_id in final_list:
                            temp1.append(doc_id)
                    final_list = temp1  #Replacing the old final_list with the new ANDed list

                elif(flag == 1 and not flag_prox): #// is present (OR operation)
                    temp1 = []
                    for doc_id in temp: #Insert all docID's which are in temp but not in final_list
                        if doc_id not in final_list:
                            temp1.append(doc_id)
                    for doc_id in final_list: #Insert all the docID's from the final_list
                        temp1.append(doc_id)
                    final_list = temp1                      
                    flag = 0    #Resetting the flag to 0

                elif(flag == -1 and not flag_prox and not flag_prox_check):   #-- is present (NOT operation)
                    temp1 = final_list
                    for doc_id in temp:
                        if doc_id in final_list:
                            temp1.remove(doc_id)
                    final_list = temp1
                    flag = 0

                elif(flag_prox):    #Handle proximity queries
                    prox_list = []
                    for doc_id in range(1, file_count+1):
                        if(query_stem[index-2] in term_pos[doc_id] and query_stem[index] in term_pos[doc_id]):
                            pos_prev_word = term_pos[doc_id][query_stem[index-2]]
                            pos_curr_word = term_pos[doc_id][query_stem[index]]

                            #print(pos_prev_word)
                            #print(pos_curr_word)
                            
                            i=0
                            j=0                    
                            
                            while (j<len(pos_prev_word) and i<len(pos_curr_word)):
                                if((pos_curr_word[i]-pos_prev_word[j]) == diff): #MAKE SURE THAT COUNT IS ADDED IF RANKING IS GIVEN
                                    i+=1
                                    j+=1
                                    prox_list.append(doc_id)
                                    break
                                elif((pos_curr_word[i] - pos_prev_word[j]) < diff):
                                    i+=1
                                elif((pos_curr_word[i] - pos_prev_word[j]) > diff):
                                    j+=1
                    print("PROXIMITY")
                    print(prox_list)

                    print("FINAL")
                    print(final_list)
                    if not final_list and flag != -1:  #If the final list is empty and flag is not -1, final list is the proximity list
                        final_list = prox_list

                    elif not final_list and flag == -1: #If final list is empty and and flag is -1
                        for i in range(1, file_count+1):
                            final_list.append(i)
                            final_list.sort()
                        for doc_id in prox_list:
                            if doc_id in final_list:
                                final_list.remove(doc_id)
                        flag = 0    #Resetting flag to 0
                        flag_prox_check = False
                
                    elif(flag == 0):  #++ is present (AND operation)
                        temp1 = []
                        for doc_id in prox_list: #ANDing the posting list obtained till then and the posting list of the word
                            if doc_id in final_list:
                                temp1.append(doc_id)
                        final_list = temp1  #Replacing the old final_list with the new ANDed list

                    elif(flag == 1): #// is present (OR operation)
                        temp1 = []
                        for doc_id in prox_list: #Insert all docID's which are in temp but not in final_list
                            if doc_id not in final_list:
                                temp1.append(doc_id)
                        for doc_id in final_list: #Insert all the docID's from the final_list
                            temp1.append(doc_id)
                        final_list = temp1                      
                        flag = 0    #Resetting the flag to 0
                    
                    elif(flag == -1):   #-- is present (NOT operation)
                        temp1 = final_list
                        for doc_id in prox_list:
                            if doc_id in final_list:
                                temp1.remove(doc_id)
                        final_list = temp1
                        flag = 0
                        flag_prox_check = False
                    flag_prox = False
            
        elif(word == "++"): #If there is a ++, set flag to 0
            flag = 0
            continue
        elif(word == "--"): #If there is a --, set flag to -1. So in the next iteration it perfroms a NOT operation
            flag = -1
            if index+2 < len(query_stem):
                if (query_stem[index+2].startswith('^^') and query_stem[index+2].split('^^')[1].isdigit()):
                    flag_prox_check = True
            
        elif(word == "//"): #If there is a //, set flag to 1. In the next iter, it performs an OR operation
            flag = 1
        elif(word.startswith('^^') and word.split('^^')[1].isdigit()):
            flag_prox = True
            diff = int(word.split('^^')[1])+1

        elif(word.startswith('..') and word.split('..')[1].isdigit()):
            result_count = int(word.split('..')[1])
        
        #WILDCARD QUERIES    
        elif('*' in word): #Handle wildcard queries
            fore_word = word.split('*')[0]
            back_word = word.split('*')[1]

            wildcard_list = []
            wildcard_list_full = []
            final_wildcard_list = []
            first = True

            for term in word_full_unique:
                if term.startswith(fore_word) and term.endswith(back_word):
                    wildcard_list_full.append(term)
                    term = stemmer.stem(term)
                    wildcard_list.append(term)

            print("WILDCARD LIST")
            print(wildcard_list)

            print("UNSTEMMED WILDCARD LIST")
            print(wildcard_list_full)
                    
            for term in wildcard_list:
                temp = posting_list[term]

                #print(posting_list[term])
                
                if not final_wildcard_list: #Check if the list is empty
                    final_wildcard_list = temp #Directly insert the posting list
                    
                else:
                    temp1 = []
                    for doc_id in temp:
                        if doc_id not in final_wildcard_list:
                            temp1.append(doc_id)
                    for doc_id in final_wildcard_list:
                        temp1.append(doc_id)
                    final_wildcard_list = temp1

            print("FINAL WILDCARD LIST")
            print(final_wildcard_list)
            
            if not final_list and flag != -1:  #If the final list is empty and flag is not -1, final list is the final_wildcard_list
                final_list = final_wildcard_list

            elif not final_list and flag == -1:
                for i in range(1, file_count+1):
                    final_list.append(i)
                final_list.sort()
                for doc_id in final_wildcard_list:
                    if doc_id in final_list:
                        final_list.remove(doc_id)
                flag = 0    #Resetting flag to 0 
                
            elif(flag == 0):  #++ is present (AND operation)
                    temp1 = []
                    for doc_id in final_wildcard_list: #ANDing the posting list obtained till then and the posting list of the word
                        if doc_id in final_list:
                            temp1.append(doc_id)
                    final_list = temp1  #Replacing the old final_list with the new ANDed list

            elif(flag == 1): #// is present (OR operation)
                    temp1 = []
                    for doc_id in final_wildcard_list: #Insert all docID's which are in temp but not in final_list
                        if doc_id not in final_list:
                            temp1.append(doc_id)
                    for doc_id in final_list: #Insert all the docID's from the final_list
                        temp1.append(doc_id)
                    final_list = temp1                      
                    flag = 0    #Resetting the flag to 0
                    
            elif(flag == -1):   #-- is present (NOT operation)
                    temp1 = final_list
                    for doc_id in final_wildcard_list:
                        if doc_id in final_list:
                            temp1.remove(doc_id)
                    final_list = temp1
                    flag = 0

    #print(final_list)
    
    #tf-idf of each term of query over each document of the final_list
    for doc_id in final_list:
        doc_score = 0
        for term in query_stem:
            if term in term_freq[doc_id]:
                term_tf = term_freq[doc_id][term]
            else:
                term_tf = 0
            term_df = len(posting_list[term])
            N = file_count

            if(term_df != 0):
                doc_score = doc_score + (term_tf * math.log10(N/term_df))
                
        tf_idf[doc_id] = doc_score

    """print("FINAL LIST")
    print(final_list)"""
    print("RANKED FINAL LIST")
    ranked_final_list = []
    ranked_final_list = sorted(tf_idf, key = tf_idf.get, reverse = True) #Print the sorted final list (Based on rank)

    result = "Doc_ID:     Doc_Name\n"
    
    if(result_count == -1):
        for doc_id in ranked_final_list:
            if doc_id < 10:
                result += (str(doc_id) + "           " + file[doc_id] + "\n")
            else:
                result += (str(doc_id) + "         " + file[doc_id] + "\n")
            print(str(doc_id) + " " + file[doc_id])
            
    else:
        for doc_id in ranked_final_list:
            if(result_count <= 0):
                break
            else:
                print(str(doc_id) + " " + file[doc_id])
                if doc_id < 10:
                    result += (str(doc_id) + "          " + file[doc_id] + "\n")
                else:
                    result += (str(doc_id) + "        " + file[doc_id] + "\n")
                result_count = result_count - 1
    return result

     
