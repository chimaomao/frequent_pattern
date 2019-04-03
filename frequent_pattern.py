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
    abstract = re.sub('[!@#$%^&*()\\n$:;]+',' ',abstract)
    #sentences = re.split('[.,?]+',abstract)
    sentences = re.split('(?<![0-9])([\.,?])',abstract)
    stop_words.extend(['.',',','?'])
    ret = []
    for se in sentences:
        k = se.split(' ')
        a = []
        for s in k:
            if s not in stop_words and len(s)>0:
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

    def add(self, count=1):
        self.count += count
    
    def display(self, layer=1):
        # if layer > 3:
        #     return
        print(' '*layer, layer ,self.name , self.count)
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


def suffixTaverse(rootNode, headerTable, minSup):
    freqSet = []
    for item in headerTable:
        itemPaths, tranSet = findParentPath(headerTable[item][1])
        # if item == 'using':
        #     print(itemPaths)
        myTree = treeNode('Root', 0, None)
        freqSet += createSubtree(itemPaths, tranSet, minSup, myTree)
        # myTree.display()
        # break
    return freqSet

def findParentPath(headerNode):
    parentPath = {}
    tranSet = []
    while headerNode is not None:
        upTraverse = []
        p = headerNode
        while p.parent is not None:
            upTraverse.append(p.name)
            p = p.parent
        if len(upTraverse) > 0:
            parentPath[frozenset(upTraverse)] = headerNode.count
            upTraverse.reverse()
            tranSet.append(upTraverse)
        headerNode = headerNode.next

    return parentPath, tranSet

def createSubtree(itemPaths, tranSet, minSup, rootNode):
    headerTable, headerWord = buildSubHeaderTable(itemPaths, minSup)
    hTable = [None]
    for trans, i in zip(tranSet, itemPaths):
        createsmallTree(trans, itemPaths[i], rootNode, headerWord, hTable)


    freqSet = []
    while hTable[0] is not None:
        if hTable[0].count >= minSup:
            p = hTable[0]
            oneSet = []
            tup = ()
            count = hTable[0].count
            while p.parent is not None:
                oneSet.append(p.name)
                tup = (oneSet, count)
                p = p.parent
        freqSet.append(tup)
        hTable[0] = hTable[0].next

    return freqSet

def buildSubHeaderTable(itemPaths, minSup):
    headerTable = {}
    for trans in itemPaths:
        for item in trans:
            if item not in headerTable:
                headerTable[item] = itemPaths[trans]
            else:
                headerTable[item] += itemPaths[trans]

    headerTemp = {}
    headerWord = []
    for i in headerTable:
        if headerTable[i] >= minSup:
            headerTemp[i] = headerTable[i]
            headerWord.append(i)
            # headerTemp[i] = [headerTable[i], None]

    return headerTemp, headerWord

def createsmallTree(trans, count, root, headerWord, htable):
    if trans[0] in headerWord:
        if trans[0] in root.children:
            root.children[trans[0]].add(count)
            if len(trans) > 1:
                createsmallTree(trans[1:], count, root, headerWord, htable)   
                createsmallTree(trans[1:], count, root.children[trans[0]], headerWord, htable)
        else:
            root.children[trans[0]] = treeNode(trans[0], count, root)

            if trans[0] == trans[-1]:
                # print(trans[0], htable)
                if htable[0] is None:
                    htable[0] = root.children[trans[0]]
                else:
                    updateHeaderTable(htable[0], root.children[trans[0]])

            if len(trans) > 1:
                createsmallTree(trans[1:], count, root, headerWord, htable)
                createsmallTree(trans[1:], count, root.children[trans[0]], headerWord, htable) 

    else:
        if len(trans) > 1:
            createsmallTree(trans[1:], count, root, headerWord, htable)    

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

    freqSet = suffixTaverse(rootNode, reverseHeaderTable, minSup)
    for f in freqSet:
        f[0].sort()
    
    
main()