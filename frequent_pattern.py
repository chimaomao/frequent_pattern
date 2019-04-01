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

    # abstractSplitSentence = re.split('[,.?]+', inFile.read().lower())

    # transaction = []
    # for splitSentence in abstractSplitSentence:  
    #     splitSentence = re.sub('[!@#$%^&*()\\n$:;]', '', splitSentence)
    #     transaction.append(splitSentence)
    # abstractSpiltWord = [i.strip().split() for i in transaction]

    # transactionItem = []
    # for sentence in abstractSpiltWord:
    #     reserveItem = []
    #     for item in sentence:
    #         if item not in stopWords:
    #         # if item not in stopWords and item not in reserveItem:
    #             reserveItem.append(item)
    #     transactionItem.append(reserveItem)
    # return transactionItem         

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
                # for w in tid:
                #     if w == word:
                #         tranItem.append(w)
        sortFreqTable.append(tranItem)
            
    return sortFreqTable

class treeNode:
    def __init__(self, word, count, parentNode):
        self.name = word
        self.count = count
        self.sumCount = count
        self.parent = parentNode
        self.children = {}
        self.childrenTemp = {}
        self.next = None

    def add(self):
        self.count += 1

    def emptyChildren(self):
        self.childrenTemp = self.children
        self.children = {}

    def recoverChildren(self):
        self.children = self.childrenTemp
        self.childrenTemp = {}
    
    def display(self):
        print (self.name, self.count)
        for child in self.children.values():
            print(child)
            child.display()
            

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

def suffixTraverse(rootNode, headerTable, minSup):
    for item in headerTable:
        # print('------------------------', item, '--------------------------------------')
        deleteLeaf(headerTable[item][1])
        sumChildValue(rootNode, item)
        pickFpSet(rootNode, item, minSup)
        recoverLeaf(headerTable[item][1])
        # break
        # print(item, rootNode.sumCount)  
               
def deleteLeaf(headerNode):
    p = headerNode
    while(p != None):
        p.emptyChildren()
        p = p.next

def recoverLeaf(headerNode):
    p = headerNode
    while(p.next != None):
        p.recoverChildren()
        p = p.next

def sumChildValue(rootNode, name):
    rootNode.sumCount = 0
    if not bool(rootNode.children):
        if rootNode.name == name:
            return rootNode.count
        else:
            return 0

    for child in rootNode.children.values():
        rootNode.sumCount += sumChildValue(child, name)

    return rootNode.sumCount

def pickFpSet(rootNode, name, minSup):
    if rootNode.name == name:
        freqSet = []
        freqSet.append(name)
        return         
    for child in rootNode.children.values():
        pickFpSet(child, minSup)


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

    suffixTraverse(rootNode, reverseHeaderTable, minSup)
    # print(wordCount)

    
main()