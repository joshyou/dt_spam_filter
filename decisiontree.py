import math
import process

#examples is a list of tuples: (feature dictionary, category)
#I'll call it "category" because "class" is a python keyword and "value" is ambiguous
#features is list of tuples: (name, [feature values])

#return most common category among given examples
def pluralityCategory(examples):
    counter = {}
    for example in examples:
        if example[1] not in counter:
            counter[example[1]] = 1
        else:
            counter[example[1]] += 1
    max_count = -1
    plurality_category = counter.keys()[0]
    for category in counter:
        if counter[category] > max_count:
            max_count = counter[category]
            plurality_category = category
    return plurality_category

#returns false if the examples belong to more than one category; else, returns that one category
def soleCategory(examples):
    category = examples[0][1]
    for example in examples:
        if example[1] != category:
            return False
    return category

#returns entropy for the category variable
def entropy(examples, categories):
    sum = 0.0
    for category in categories:
        count = 0.0
        for example in examples:
            if example[1] == category:
                count += 1
        category_prob = count / len(examples)
        if category_prob != 0:
            sum += category_prob * math.log(category_prob, 2)
    return -sum

#returns conditional entropy of category given feature
#feature is tuple - (name, [possible values])
def conditionalEntropy(examples, feature, categories):
    name = feature[0]
    values = feature[1]
    outer_sum = 0.0
    
    #sum over possible feature values
    for value in values:
        value_examples = []
        #compiles examples with this feature value
        for example in examples:
            if example[0][name] == value:
                value_examples.append(example)
        value_prob = 1.0*len(value_examples) / len(examples)
        #print value
        #print "value prob: " + str(value_prob)
        if value_prob == 0:
            continue
        inner_sum = 0.0

        for category in categories:
            count = 0.0
            for example in value_examples:
                if example[1] == category:
                    count += 1
            #computes probability of category given value
            category_prob = count / len(value_examples)
            #print category
            #print "category prob: " + str(category_prob)
            if category_prob != 0:

                inner_sum += category_prob * math.log(category_prob, 2)
                #print "inner_sum: " + str(inner_sum)

        outer_sum += value_prob*inner_sum

    #-0.0 is just wrong
    if outer_sum == 0:
        return outer_sum
    return -outer_sum

#returns feature where the conditional entropy of category given feature is smallest
def leastConditionalEntropy(examples, features, categories):
    smallest_entropy = 1e300
    least = features[0]
    for feature in features:
        entropy = conditionalEntropy(examples, feature, categories)
        #print "entropy: " + str(entropy) + str(feature)
        if entropy < smallest_entropy:
            least = feature
            smallest_entropy = entropy
    return least

class DecisionTreeNode:

    def __init__(self, examples, features, categories, feature = None, feature_value = None, parentNode = None, parent_examples = None):
        self.parentNode = parentNode
        self.examples = examples
        self.parent_examples = parent_examples
        self.feature = feature
        self.feature_value = feature_value
        self.features = features
        self.childNodes = []
        self.categories = categories
        self.leafValue = None

    def getParent(self):
        return self.parentNode

    def getChildren(self):
        return self.childNodes

    def addChild(self, child):
        self.childNodes.append(child)

    def removeChildren(self):
        self.childNodes = []

    #turns parent node into a leaf node
    def pruneNode(self):
        if self.parentNode != None:
            self.parentNode.removeChildren()
            self.parentNode.setLeafValue(pluralityCategory(self.parent_examples))

    def getLeafValue(self):
        return self.leafValue

    def setLeafValue(self, leafValue):
        self.leafValue = leafValue

    def getfeature(self):
        return self.feature

    def getfeatureValue(self):
        return self.feature_value

    def getExamples(self):
        return self.examples

    #recursively splits up the data based on the feature with the most information gain
    def decisionTreeLearn(self):
        if len(self.examples) == 0:
            self.setLeafValue(pluralityCategory(self.parent_examples))
            return self.leafValue
        elif soleCategory(self.examples):
            #print "in soleCategory!"
            self.setLeafValue(soleCategory(self.examples))
            return self.leafValue
        elif len(self.features) == 0:
            self.setLeafValue(pluralityCategory(self.examples))
            return self.leafValue
        else:
            to_split = leastConditionalEntropy(self.examples, self.features, self.categories)
            cond_ent = conditionalEntropy(self.examples, to_split, self.categories)
            ent = entropy(self.examples, self.categories)
            info_gain = ent - cond_ent
            #print info_gain

            #create copy of features without the split feature
            new_features = list(self.features)
            new_features.remove(to_split)
            feature_name = to_split[0]
            #create new tree and recursively call for each value of the split feature
            #print "values in split feature:"
            #print to_split[1]
            for value in to_split[1]:
                #print value
                value_examples = []
                for example in self.examples:
                    if example[0][feature_name] == value:
                        value_examples.append(example)
                new_node = DecisionTreeNode(value_examples, new_features, self.categories, to_split, value, self, self.examples)
                new_node.decisionTreeLearn()
                self.addChild(new_node)


    #if leaf:
    #measure info gain from splitting at parent
    #prune if below threshold, recursively call on parent
    #else:
    #recursively call on child
    def pruneTree(self):
        #print "called pruneTree"
        #print self.getLeafValue()
        if self.getLeafValue() != None and self.feature != None:
            parent = self.getParent()
            cond_ent = conditionalEntropy(self.parent_examples, self.feature, self.categories)
            ent = entropy(self.parent_examples, self.categories)
            info_gain = ent - cond_ent
            if info_gain < 0.01:
                self.pruneNode()
                parent.pruneTree()
        else:
            for child in self.getChildren():
                child.pruneTree()


    #test example is feature dict
    #returns categorization for test_example
    def traverseTree(self, test_example):
        if self.getLeafValue() != None:
            return self.getLeafValue()
        else:
            split_feature = self.childNodes[0].getfeature()
            for child in self.childNodes:
                if test_example[split_feature[0]] == child.getfeatureValue():
                    return child.traverseTree(test_example)

    def printTree(self):
        if self.getfeatureValue() == None:
            print "ROOT"
        else:
            print str(self.getfeature()[0]) + " " + str(self.getfeatureValue())
        if self.getLeafValue() != None:
            print self.getLeafValue()
        for child in self.getChildren():
            print "(",
            child.printTree()
            print ")",

    #returns number of nodes in tree with this node as its root; i.e count of this node and
    #all descendants
    def countNodes(self):
        if self.getLeafValue() != None:
            return 1

        descendant_count = 0
        for child in self.getChildren():
            descendant_count += child.countNodes()

        return descendant_count + 1

def titanic_test():
    examples = [({"sex":"female", "class":"lower"}, "died"), 
    ({"sex":"female", "class":"lower"}, "survived"),
    ({"sex":"female", "class":"lower"}, "died"),
    ({"sex":"female", "class":"lower"}, "survived"),
    ({"sex":"female", "class":"lower"}, "survived"),
    ({"sex":"female", "class":"lower"}, "survived"),
    ({"sex":"female", "class":"first"}, "died"), 
    ({"sex":"female", "class":"first"}, "survived"), 
    ({"sex":"female", "class":"first"}, "survived"), 
    ({"sex":"female", "class":"first"}, "survived"), 
    ({"sex":"female", "class":"first"}, "survived"), 
    ({"sex":"male", "class":"first"}, "survived"),
    ({"sex":"male", "class":"first"}, "survived"),
    ({"sex":"male", "class":"first"}, "survived"),
    ({"sex":"male", "class":"first"}, "died"),
    ({"sex":"male", "class":"first"}, "died"),
    ({"sex":"male", "class":"lower"}, "died"),
    ({"sex":"male", "class":"lower"}, "died"),
    ({"sex":"male", "class":"lower"}, "survived"),
    ({"sex":"male", "class":"lower"}, "died")]
    #print pluralityCategory(examples)
    #print soleCategory(examples)
    categories = ["died", "survived"]
    features = [("sex", ["male", "female"]), ("class", ["first", "lower"])]


    print conditionalEntropy(examples, ("sex", ["male", "female"]), ["died", "survived"])
    print conditionalEntropy(examples, ("class", ["first", "lower"]), ["died", "survived"])  
    print entropy(examples, ["died", "survived"])
    print leastConditionalEntropy(examples, features, categories)

    test_tree = DecisionTreeNode(examples, features, categories)
    test_tree.decisionTreeLearn()
    #print test_tree.traverseTree({"sex":"female", "class":"lower"})
    #test_tree.printTree()

def spambase_test():
    examples = process.spambase_process("training.txt")
    categories = [0,1]
    features = []

    for i in range(48):
        features.append((i, [0,1,2,3,4,5]))

    for i in range(48, 55):
        features.append((i, [0,1,2,3,4,5,6]))

    features.append((55, [0,1,2,3]))
    features.append((56, [0,1,2,3]))

    tree = DecisionTreeNode(examples, features, categories)
    tree.decisionTreeLearn()
    print "NUMBER OF NODES: "
    print tree.countNodes()
    tree.pruneTree()
    print "NUMBER OF NODES AFTER PRUNING: "
    print tree.countNodes()
    
    #tree.printTree()

    
    #tree classified as spam, and was right
    spam_right = 0.0
    #and so on
    spam_wrong = 0.0
    ham_right = 0.0
    ham_wrong = 0.0

    for example in examples:
        actual = example[1]
        from_tree = tree.traverseTree(example[0])

        if from_tree == 0:
            if actual == 0:
                ham_right += 1
            else:
                ham_wrong += 1
        else:
            if actual == 1:
                spam_right += 1
            else:
                spam_wrong += 1

    print "TRAINING RESULTS:"
    print "spam_right: " + str(spam_right)
    print "spam_wrong: " + str(spam_wrong)
    print "ham_right: " + str(ham_right)
    print "ham_wrong: " + str(ham_wrong)
    print "total accuracy: " + str((spam_right + ham_right) / (spam_right + spam_wrong + ham_right + ham_wrong))
    print "spam accuracy: " + str(spam_right / (spam_right + ham_wrong))
    print "ham accuracy: " + str(ham_right / (spam_wrong + ham_right))
    print "false positive: " + str(spam_wrong / (ham_right + spam_wrong))
    print "false negative: " + str(ham_wrong / (ham_wrong + spam_right))

    print "\n"

    spam_right = 0.0
    spam_wrong = 0.0
    ham_right = 0.0
    ham_wrong = 0.0

    heldout_examples = process.spambase_process("heldout.txt")
    for example in heldout_examples:
        actual = example[1]
        from_tree = tree.traverseTree(example[0])

        if from_tree == 0:
            if actual == 0:
                ham_right += 1
            else:
                ham_wrong += 1
        else:
            if actual == 1:
                spam_right += 1
            else:
                spam_wrong += 1
    
    print "HELD OUT RESULTS:"
    print "spam_right: " + str(spam_right)
    print "spam_wrong: " + str(spam_wrong)
    print "ham_right: " + str(ham_right)
    print "ham_wrong: " + str(ham_wrong)
    print "total accuracy: " + str((spam_right + ham_right) / (spam_right + spam_wrong + ham_right + ham_wrong))
    print "spam accuracy: " + str(spam_right / (spam_right + ham_wrong))
    print "ham accuracy:: " + str(ham_right / (spam_wrong + ham_right))
    print "false positive: " + str(spam_wrong / (ham_right + spam_wrong))
    print "false negative: " + str(ham_wrong / (ham_wrong + spam_right))

    
def main():
    spambase_test()


if __name__ == "__main__":
    main()

"""
TO DO:
pruning / info gain threshold

handling sparse feature vectors (don't store every value)"""