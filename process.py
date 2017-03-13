import sys

#for spambase data
#returns list of examples in (feature_dict, category) format from given filename
def spambase_process(filename): 
    f = open(filename, 'r')
    examples = []
    for line in f:
        features = line.split(",")
        #print len(features)
        feature_dict = {}
        #example = []
        category = int(features[57])
        for i in range(len(features)):
            #convert first 48 to binary features
            if i < 48:
                if float(features[1]) > 2:
                    feature_dict[i] = 5
                elif float(features[1]) > 1:
                    feature_dict[i] = 4
                elif float(features[1]) > 0.6:
                    feature_dict[i] = 3
                elif float(features[1]) > 0.3:
                    feature_dict[i] = 2
                elif float(features[1]) > 0.1:
                    feature_dict[i] = 1
                else:
                    feature_dict[i] = 0
            #convert char percentages to ternary features
            elif i < 54:
                if float(features[i] > 1):
                    feature_dict[i] = 6
                elif float(features[i] > 0.6):
                    feature_dict[i] = 5
                elif float(features[i] > 0.3):
                    feature_dict[i] = 4
                elif float(features[i] > 0.1):
                    feature_dict[i] = 3
                elif float(features[i] > 0.01):
                    feature_dict[i] = 2
                elif float(features[i] > 0):
                    feature_dict[i] = 1
                else:
                    feature_dict[i] = 0
            elif i == 54:
                if float(features[i] > 5.0):
                    feature_dict[i] = 3
                elif float(features[i] > 3.0):
                    feature_dict[i] = 2
                elif float(features[i] > 2.0):
                    feature_dict[i] = 1
                else:
                    feature_dict[i] = 0
            elif i == 55:
                if int(features[i]) > 100:
                    feature_dict[i] = 3
                elif int(features[i]) > 50:
                    feature_dict[i] = 2
                elif int(features[i]) > 10:
                    feature_dict[i] = 1
                else:
                    feature_dict[i] = 0
            elif i == 56:
                if int(features[i]) > 2000:
                    feature_dict[i] = 3
                elif int(features[i]) > 1000:
                    feature_dict[i] = 2
                elif int(features[i]) > 100:
                    feature_dict[i] = 1
                else:
                    feature_dict[i] = 0
        example = (feature_dict, category)
        examples.append(example)
    return examples

def spambase_process_continuous(filename):
    f = open(filename, 'r')
    examples = []
    for line in f:
        features = line.split(",")
        #print features
        #print len(features)
        feature_dict = {}
        #example = []
        category = int(features[57])
        for i in range(len(features)-1):
            feature_dict[i] = float(features[i])
        example = (feature_dict, category)
        examples.append(example)
    return examples



#print spambase_process("training.txt")