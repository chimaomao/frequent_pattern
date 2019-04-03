import sys
import re
import operator
import copy

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

def abs_2_trans(abstract , stop_words):
    abstract = abstract.lower()
    abstract = re.sub('[\\n]',' ',abstract)
    abstract = re.sub('[!@#$%^&*()\\n$:;]+','',abstract)
    sentences = re.split('[.,?]+',abstract)
    
    ret = []
    
    for se in sentences:
        k = se.split(' ')
        a = []
        for s in k:
            if s not in stop_words and len(s)>0 and s not in a:
                a.append(s)
        if len(a)>0:
            ret.append(a)
    return ret

def genTransactionItem():
    in_file = arg[1]
    inFile = open(in_file, 'r').readlines()
    stop = open('stop_words.txt', 'r')
    stopWords = stop.read().split()

    transactionItem = []
    for line in inFile:
        transactionItem += abs_2_trans(line, stopWords)

    return transactionItem
      
def genWordCount(trancsactionItem):
    wordCount = {}
    for trans in trancsactionItem:
        for word in trans:
            if word not in wordCount:
                wordCount[word] = 1
            else:
                wordCount[word] += 1
    sortedWordCount = sorted(wordCount.items(), key=operator.itemgetter(1), reverse=True)

    return sortedWordCount

def buildHeaderTable(wordCount, minSup):
    headerWord = []
    # headerTable = {}
    reverseHeaderTable = {}

    for tup in wordCount: 
        if tup[1] >= minSup:
            # headerTable[tup[0]] = tup[1]
            headerWord.append(tup[0])
    
    for tup in reversed(wordCount):
        if tup[1] >= minSup:
            reverseHeaderTable[tup[0]] = tup[1]
    
    for i in reverseHeaderTable:
        reverseHeaderTable[i] = [reverseHeaderTable[i], None]

    # for i in headerTable:
    #     headerTable[i] = [headerTable[i], None]

    return reverseHeaderTable, headerWord

def excludeFreqItem(transactionItem, headerWord):
    freqTable = []
    for trans in transactionItem:
        freqtran = []
        for item in trans:
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
                tranItem.append(word)
        sortFreqTable.append(tranItem)
            
    return sortFreqTable

class treeNode:
    def __init__(self, word, count, parentNode):
        self.name = word
        self.count = count
        self.parent = parentNode
        self.children = {}
        self.next = None

    def add(self):
        self.count += 1
    
    def display(self, layer=1):
        # if layer > 3:
        #     return
        print(' '*layer, layer ,self.name , self.sumCount, self.count)
        for child in self.children.values():
            child.display(layer+1)
            

def createTree(trans, headerTable, root):
    if trans[0] in root.children:
        root.children[trans[0]].add()
    else:
        root.children[trans[0]] = treeNode(trans[0], 1, root)

        if headerTable[trans[0]][1] == None:
            headerTable[trans[0]][1] = root.children[trans[0]]
        else:
            updateHeaderTable(headerTable[trans[0]][1], root.children[trans[0]])

    if len(trans) > 1:
        createTree(trans[1:], headerTable, root.children[trans[0]])

def updateHeaderTable(headerNode, newChildNode):
    while(headerNode.next != None):
        headerNode = headerNode.next
    headerNode.next = newChildNode

def suffixTaverse(rootNode, headerTable):
    return

def findParentPath():
    return

def main():
    out_file, min_sup = arg[2], arg[3]
    minSup = int(min_sup)
    outFile = open(out_file, 'w')
    transactionItem = genTransactionItem()
    wordCount = genWordCount(transactionItem)
    reverseHeaderTable, headerWord = buildHeaderTable(wordCount, minSup)
    freqTable = excludeFreqItem(transactionItem, headerWord)
    sortFreqTable = sortFreqItem(freqTable, headerWord)
    # create tree and header table linklist
    rootNode = treeNode('Root', 0, None)
    for trans in sortFreqTable:
        createTree(trans, reverseHeaderTable, rootNode)

    suffixTaverse(rootNode, reverseHeaderTable)
    

    # print(wordCount)

    # rootNode.display()
    
main()