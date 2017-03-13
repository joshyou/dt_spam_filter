import process
import random

#examples is a list of tuples: (feature dictionary, category)
#features is list of tuples: (name, [feature values])

#returns dot product of vectors stored as dictionaries
def dotproduct(d1, d2):
    if len(d1) != len(d2):
        return 1/0
    product = 0.0
    for key in d1:
        product += d1[key]*d2[key]
    return product

#returns sum of two vectors stored as dictionaries
def addvectors(d1, d2, coeff = 1.0):
    if len(d1) != len(d2):
        return 1/0
    sumdict = {}
    for key in d1:
        sumdict[key] = d1[key] + coeff*d2[key]
    return sumdict

#def subvectors(d1, d2):

def train(features, examples):
    weights = {}
    for feature in features:
        weights[feature[0]] = 1

    for i in range(2000):
        for example in examples:
            #assigned = 0
            true_label = example[1]
            #print true_label
            activation = dotproduct(weights, example[0])
            if activation > 0:
                assigned = 1
            else:
                assigned = 0
            #tup = (assigned, true_label)
            #print tup
            if assigned != true_label:
                if true_label == 1:
                    #print "added to weights"
                    weights = addvectors(weights, example[0])
                else:
                    #print "subtracted from weights"
                    weights = addvectors(weights, example[0], -1.0)

    return weights

def classify(example_dict, weights):
    activation = dotproduct(weights, example_dict)
    #print activation
    if activation > 0:
        return 1
    else:
        return 0

def spambase_test():
    examples = process.spambase_process_continuous("training.txt")
    #print examples[0]
    #print len(examples[0])
    #randomize order of examples
    examples = random.sample(examples, len(examples))


    categories = [0,1]
    features = []

    for i in range(48):
        features.append((i, [0,1,2,3,4,5]))

    for i in range(48, 55):
        features.append((i, [0,1,2,3,4,5,6]))

    features.append((55, [0,1,2,3]))
    features.append((56, [0,1,2,3]))

    weights = train(features, examples)
    #print weights
    spam_right = 0.0
    #and so on
    spam_wrong = 0.0
    ham_right = 0.0
    ham_wrong = 0.0

    for example in examples:
        #print example
        actual = example[1]
        assigned = classify(weights, example[0])

        if assigned == 0:
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

    print weights

    heldout_examples = process.spambase_process("heldout.txt")

    spam_right = 0.0
    spam_wrong = 0.0
    ham_right = 0.0
    ham_wrong = 0.0

    for example in heldout_examples:
        actual = example[1]
        assigned = classify(weights, example[0])

        if assigned == 0:
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