import sys
import re
import operator

arg = sys.argv

def sort_pattern(pat, inv_word_idx):
    items = pat.items()
    words = []
    freqs = []
    for k , v in items:
        word = []
        for w in k:
            word.append(inv_word_idx[w])
        word.sort()
        freqs.append(v)
        words.append(word)
    ls = [[words[i],freqs[i]] for i in range(len(words)) ]
    ls.sort()
    return ls

def genTransactionItem():
    in_file = arg[1]
    inFile = open(in_file, 'r')
    stop = open('stop_words.txt', 'r')
    stopWords = stop.read().split()

    abstractSplitSentence = re.split('[,.?]+', inFile.read().lower())

    transaction = []
    for splitSentence in abstractSplitSentence:  
        splitSentence = re.sub('[!@#$%^&*()\\n$:;]', '', splitSentence)
        transaction.append(splitSentence)
    abstractSpiltWord = [i.strip().split() for i in transaction]

    transactionItem = []
    for sentence in abstractSpiltWord:
        reserveItem = []
        for item in sentence:
            if item not in stopWords:
                reserveItem.append(item)
        transactionItem.append(reserveItem)                       

    return transactionItem

def genWordCount(trancsactionItem):
    wordCount = {}
    for sentence in trancsactionItem:
        for word in sentence:
            if word not in wordCount:
                wordCount[word] =  1
            else:
                wordCount[word] += 1
    sortedWordCount = sorted(wordCount.items(), key=operator.itemgetter(1), reverse=True)

    return sortedWordCount

def buildHeaderTable(wordCount, minSup):
    headerTable = [tup for tup in wordCount if tup[1] >= minSup]
    return headerTable

def excludeFreqItem(transactionItem, headerWord):
    freqTable = []
    for sentence in transactionItem:
        freqtran = []
        for item in sentence:
            if item in headerWord:
                freqtran.append(item)
        if len(freqtran) > 0:
            freqTable.append(freqtran)

    return freqTable

def sortFreqItem(freqTable, headerWord):
    sortFreqTable = []
    for tid in freqTable:
        tranItem = []
        for word in headerWord:
            if word in tid:
                for w in tid:
                    if w == word:
                        tranItem.append(w)
        sortFreqTable.append(tranItem)
            
    return sortFreqTable

def genHeaderWord(headerTable):
    headerWord = [word for word, freq in headerTable]
    return headerWord

def main():
    out_file, min_sup = arg[2], arg[3]
    minSup = int(min_sup)
    outFile = open(out_file, 'w')
    transactionItem = genTransactionItem()
    wordCount = genWordCount(transactionItem)
    headerTable = buildHeaderTable(wordCount, minSup)
    headerWord = genHeaderWord(headerTable)
    freqTable = excludeFreqItem(transactionItem, headerWord)
    sortFreqTable = sortFreqItem(freqTable, headerWord)

    print(sortFreqTable)


main()