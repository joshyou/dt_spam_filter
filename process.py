"""
Includes various functions to extract example information from spambase datasets
"""

import sys
import decisiontree

#divides the feature with given index into k bins of equal size
#returns an array of lower bounds for the k bins
def discretize(examples, index, k):
    min_value = 1e300
    max_value = -1e300
    for example in examples:
        if example[0][index] < min_value:
            min_value = example[0][index]
        if example[0][index] > max_value:
            max_value = example[0][index]
    bins = []
    bin_width = (1.0*max_value - 1.0*min_value)/k
    for i in range(k):
        bins.append(min_value + i*bin_width)
    return bins

#splits feature with given index into a binary feature with threshold
#that maximizes info gain
def max_infogain(examples, index):
    min_value = 1e300
    max_value = -1e300
    for example in examples:
        if example[0][index] < min_value:
            min_value = example[0][index]
        if example[0][index] > max_value:
            max_value = example[0][index]
    feature_range = 1.0*(max_value - min_value)
    highest_IG = -1e300
    best_bin_set = None
    for i in range(1,15):
        bin_set = [min_value, min_value + i*feature_range/15]
        
        test_examples = put_into_bins_index(examples, bin_set, index)
        feature = (index, [0,1])
        categories = [0,1]
        test_info_gain = decisiontree.infoGain(test_examples, feature, categories)
        if test_info_gain > highest_IG:
            best_bin_set = bin_set
            highest_IG = test_info_gain
    return best_bin_set

def put_into_bins_index(examples, bin_set, index):
    binned_examples = []
    for example in examples:
        feature_dict = example[0]
        for j in range(len(bin_set)):
            #if we're at the last bin, then that's the correct bin
            if j == len(bin_set) - 1:
                feature_dict[index] = j
            #find bin where example value is between the bin value and the next bin value
            elif example[0][index] >= bin_set[j] and example[0][index] < bin_set[j+1]:
                feature_dict[index] = j
                break
        new_example = (feature_dict, example[1])
        binned_examples.append(new_example)
    #print binned_examples
    return binned_examples

#discretizes example features according to bin_set
def put_into_bins(examples, bin_sets):
    binned_examples = []
    for example in examples:
        feature_dict = {}
        for i in range(57):

            for j in range(len(bin_sets[i])):
                #if we're at the last bin, then that's the correct bin
                if j == len(bin_sets[i]) - 1:
                    feature_dict[i] = j
                #find bin where example value is between the bin value and the next bin value
                elif example[0][i] >= bin_sets[i][j] and example[0][i] < bin_sets[i][j+1]:
                    feature_dict[i] = j
                    break
        new_example = (feature_dict, example[1])
        binned_examples.append(new_example)
    return binned_examples


def spambase_process_bins(filename, k):
    f = open(filename, 'r')
    examples = []
    for line in f:
        features = line.split(",")
        feature_dict = {}
        category = int(features[57])
        for i in range(len(features)-1):
            feature_dict[i] = float(features[i])
        example = (feature_dict, category)
        examples.append(example)
    bin_sets = []
    #create bins for each attribute
    for i in range(57):
        bin_sets.append(discretize(examples, i, k))
        
    return put_into_bins(examples, bin_sets)

def spambase_process_infogain(filename):
    f = open(filename, 'r')
    examples = []
    for line in f:
        features = line.split(",")
        feature_dict = {}
        category = int(features[57])
        for i in range(len(features)-1):
            feature_dict[i] = float(features[i])
        example = (feature_dict, category)
        examples.append(example)
    bin_sets = []
    #create bins for each attribute
    for i in range(57):
        bin_sets.append(max_infogain(examples, i))
    return put_into_bins(examples, bin_sets)


#just keep original continuous values
def spambase_process_continuous(filename):
    f = open(filename, 'r')
    examples = []
    for line in f:
        features = line.split(",")
        feature_dict = {}
        category = int(features[57])
        for i in range(len(features)-1):
            feature_dict[i] = float(features[i])
        example = (feature_dict, category)
        examples.append(example)
    return examples