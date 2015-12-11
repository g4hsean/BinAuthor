__author__ = 'titan'
import random
import binascii
import pickle
import os

string1 = "Shakespeare produced most of his known work between 1589 and 1613"
string2 = "Shakespeare produced most of his work after 1589"

numOfShingles = 3
numOfUniqueHashCodes = 200
hashNumbers = []
maxShingleID = 2**32-1
nextPrime = 4294967311
numHashes = numOfUniqueHashCodes

stringShinglesDict = {"string1":[string1,set(),[]],"string2":[string2,set(),[]]}

path = os.path.dirname(os.path.realpath(__file__))
coeffA = pickle.load( open( path + "\coeffA.p", "rb" ) )#pickRandomCoeffs(numHashes)
coeffB = pickle.load( open( path + "\coeffB.p", "rb" ) )#pickRandomCoeffs(numHashes)

def minHash(documentShingles):
    global maxShingleID
    global nextPrime
    global coeffA
    global coeffB

    minHashes = []

    #print '\nGenerating MinHash signatures for all documents...'

    # List of documents represented as signature vectors
    signatures = []

    # Rather than generating a random permutation of all possible shingles,
    # we'll just hash the IDs of the shingles that are *actually in the document*,
    # then take the lowest resulting hash code value. This corresponds to the index
    # of the first shingle that you would have encountered in the random order.

    # For each document...

    # Get the shingle set for this document.
    shingleIDSet = documentShingles

    # The resulting minhash signature for this document.
    signature = []

    # For each of the random hash functions...
    for i in range(0, numHashes):

        # For each of the shingles actually in the document, calculate its hash code
        # using hash function 'i'.

        # Track the lowest hash ID seen. Initialize 'minHashCode' to be greater than
        # the maximum possible value output by the hash.
        minHashCode = nextPrime + 1

        # For each shingle in the document...
        for shingleID in shingleIDSet:
            # Evaluate the hash function.
            hashCode = (coeffA[i] * shingleID + coeffB[i]) % nextPrime

            # Track the lowest hash code seen.
            if hashCode < minHashCode:
                minHashCode = hashCode

        # Add the smallest hash code value as component number 'i' of the signature.
        minHashes.append(minHashCode)

      # Store the MinHash signature for this document.
    return minHashes

def pickRandomCoeffs(k):
  global maxShingleID
  # Create a list of 'k' random values.
  randList = []

  while k > 0:
    # Get a random shingle ID.
    randIndex = random.randint(0, maxShingleID)

    # Ensure that each random number is unique.
    while randIndex in randList:
      randIndex = random.randint(0, maxShingleID)

    # Add the random number to the list.
    randList.append(randIndex)
    k = k - 1

  return randList

def createShingles(documentString):
    items = documentString.split(" ")
    counter = 0
    shingles = set()
    for item in items:
        #print counter
        if (counter+2) < len(items):
            shingle = items[counter] + " " + items[counter+1] + " " + items[counter+2]
            crc = binascii.crc32(shingle) & 0xffffffff
            shingles.add(crc)
        counter += 1
    return shingles

def similarity(document1Minhashes,document2Minhashes):
    count = 0
    for k in range(0,numHashes):
        count = count + (document1Minhashes[k] == document2Minhashes[k])
    return (count/float(numHashes))


def test():
    stringShinglesDict["string1"][1] = createShingles(stringShinglesDict["string1"][0])
    stringShinglesDict["string2"][1] = createShingles(stringShinglesDict["string2"][0])

    stringShinglesDict["string1"][2] = minHash(stringShinglesDict["string1"][1])
    stringShinglesDict["string2"][2] = minHash(stringShinglesDict["string2"][1])

    print stringShinglesDict["string1"][2]
    print stringShinglesDict["string2"][2]
    print similarity(stringShinglesDict["string1"][2],stringShinglesDict["string2"][2])

