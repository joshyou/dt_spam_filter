import math
import process
import time
import random
import sys

global error_threshold
global k 

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

def infoGain(examples, feature, categories):
    cond_ent = conditionalEntropy(examples, feature, categories)
    ent = entropy(examples, categories)
    return ent - cond_ent

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
    """
    Represents a decision tree node with given examples, feature list, and category list
    Examples represent by a list of tuples: (feature dictionary, category)
    I call it "category" because "class" is a python keyword
    Features is list of tuples: (feature_name, [possible feature values])
    """
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

    #computes error estimate at at this node
    #using z = 0.69, suggested by http://www.saedsayad.com/decision_tree_overfitting.htm
    def errorEstimate(self):
        N = len(self.examples)
        if N == 0:
            return 0
        error = 0.0

        #uses leaf value if this node is a leaf, otherwise uses plurality category
        if self.leafValue != None:
            assigned_category = self.leafValue
        else:
            assigned_category = pluralityCategory(self.examples)
        for example in self.examples:
            if example[1] != assigned_category:
                error += 1
        error_rate = error / N
        z = 0.69
        numerator = (error_rate + (z*z)/(2*N) + z*math.pow(error_rate/N - (error_rate*error_rate)/N + (z*z)/(4*N*N), 0.5))
        denominator = 1 + (z*z)/N
        return numerator / denominator


    #recursively splits up the data based on the feature with the most information gain
    def decisionTreeLearn(self):
        #base cases for terminating recursion
        if len(self.examples) == 0:
            self.setLeafValue(pluralityCategory(self.parent_examples))
            return self.leafValue
        elif soleCategory(self.examples):
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

            #create copy of features without the split feature
            new_features = list(self.features)
            new_features.remove(to_split)
            feature_name = to_split[0]
            #create new tree and recursively call for each value of the split feature
            for value in to_split[1]:
                value_examples = []
                for example in self.examples:
                    if example[0][feature_name] == value:
                        value_examples.append(example)
                new_node = DecisionTreeNode(value_examples, new_features, self.categories, to_split, value, self, self.examples)
                new_node.decisionTreeLearn()
                self.addChild(new_node)


    #prunes tree from bottom-up based on info gain from splitting at parent
    #I ended up using other pruning method
    def pruneTreeInfoGain(self):
        if self.getLeafValue() != None and self.feature != None:
            parent = self.getParent()
            cond_ent = conditionalEntropy(self.parent_examples, self.feature, self.categories)
            ent = entropy(self.parent_examples, self.categories)
            info_gain = ent - cond_ent
            if info_gain < 0.01:
                self.pruneNode()
                parent.pruneTreeInfoGain()
                return True
        else:
            for child in self.getChildren():
                #if one child is pruned, they're all pruned
                pruned = child.pruneTreeInfoGain()
                if pruned:
                    return

    #Recurses downward until it finds nodes where all children are leaves
    def pruneTreeDownError(self):
        if len(self.childNodes) == 0:
            return
        all_leaves = True
        for child in self.childNodes:
            if child.getLeafValue() == None:
                all_leaves = False
        if all_leaves:
            self.pruneTreeUpError()
        else:
            for child in self.childNodes:
                child.pruneTreeDownError()

    #Recursively prunes node based on comparing error estimate with error estimate
    #of child nodes
    def pruneTreeUpError(self):
        #don't prune leaves
        if len(self.childNodes) == 0:
            return

        #call this on nodes where all children are leaf nodes
        all_leaves = True
        for child in self.childNodes:
            if child.getLeafValue() == None:
                all_leaves = False

        if all_leaves:
            parent = self.getParent()
            error = self.errorEstimate()
            children_error = 0.0
            weight_sum = 0.0
            for child in self.childNodes:
                child_error = child.errorEstimate()
                weight = 1.0*len(child.getExamples())/len(self.examples)
                weight_sum += weight
                children_error += (child_error * weight)
            global error_threshold
            if children_error >= error + error_threshold:
                self.removeChildren()
                self.setLeafValue(pluralityCategory(self.examples))
                #recursively call on parents
                if parent != None:
                    parent.pruneTreeUpError()


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

def spambase_test(arg_k, arg_error_threshold):
    #number of bins
    global k 
    k = arg_k
    global error_threshold
    error_threshold = arg_error_threshold
    examples = process.spambase_process_bins("training.txt", k)
    categories = [0,1]
    features = []
    feature_values = []

    for i in range(k):
        feature_values.append(i)
    
    for i in range(57):
        features.append((i, feature_values))
    
    tree = DecisionTreeNode(examples, features, categories)
    tree.decisionTreeLearn()
    print "NUMBER OF BINS:"
    print k
    print "NUMBER OF NODES: "
    print tree.countNodes()
    time1 = time.time()
    tree.pruneTreeDownError()
    print "NUMBER OF NODES AFTER PRUNING: "
    print tree.countNodes()
    time2 = time.time()
    print "TIME TO PRUNE: "
    print str(time2 - time1)
    
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

    heldout_examples = process.spambase_process_infogain("heldout.txt")
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
    print "\n"

    test_examples = process.spambase_process_infogain("test.txt")
    for example in test_examples:
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
    
    print "TEST RESULTS:"
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
    spambase_test(int(sys.argv[1]), float(sys.argv[2]))


if __name__ == "__main__":
    main()