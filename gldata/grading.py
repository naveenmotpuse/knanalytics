from collections import defaultdict, namedtuple

# for testing purposes...
correct_answers = [{'date':'date1', 'transaction': 1, 'subTransaction': 0, 'account':"10100 - Cash", 'description':"", 'debit':"59000", 'credit':""},
    {'date':'date1', 'transaction': 1, 'subTransaction': 1, 'account':"30100 - ???", 'description':"", 'debit':"", 'credit':"59000"},

    {'date':'date2', 'transaction': 2, 'subTransaction': 0, 'account':"11000 - Land", 'description':"", 'debit':"37000", 'credit':""},
    {'date':'date2', 'transaction': 2, 'subTransaction': 1, 'account':"10100 - Cash", 'description':"", 'debit':"", 'credit':"37000"},

    {'date':'date3', 'transaction': 3, 'subTransaction': 0, 'account':"10650 - Supplies", 'description':"", 'debit':"1700", 'credit':""},
    {'date':'date3', 'transaction': 3, 'subTransaction': 1, 'account':"20100 - 'account's Payable", 'description':"", 'debit':"", 'credit':"1200"},
    {'date':'date3', 'transaction': 3, 'subTransaction': 2, 'account':"10100 - Cash", 'description':"", 'debit':"", 'credit':"500"}]

student_answers = [

    {'date':'date3', 'transaction': 3, 'subTransaction': 0, 'account':"10650 - Supplies", 'description':"", 'debit':"1700", 'credit':""},
    {'date':'date3', 'transaction': 3, 'subTransaction': 1, 'account':"20100 - 'account's Payable", 'description':"", 'debit':"", 'credit':"1200"},
    {'date':'date3', 'transaction': 3, 'subTransaction': 2, 'account':"10100 - Cash", 'description':"", 'debit':"", 'credit':"500"},
#    {'date':'date3', 'transaction': 3, 'subTransaction': 2, 'account':"10100 - Cash", 'description':"", 'debit':"", 'credit':"500"},

#    {'date':'date1', 'transaction': 2, 'subTransaction': 0, 'account':"10100 - Cash", 'description':"", 'debit':"59000", 'credit':""},
#    {'date':'date1', 'transaction': 2, 'subTransaction': 1, 'account':"30100 - ???", 'description':"", 'debit':"", 'credit':"59000"},

    {'date':'date1', 'transaction': 4, 'subTransaction': 0, 'account':"10100 - Cash", 'description':"", 'debit':"59000", 'credit':""},
    {'date':'date1', 'transaction': 4, 'subTransaction': 1, 'account':"30100 - ???", 'description':"", 'debit':"", 'credit':"59000"},

    {'date':'date2', 'transaction': 1, 'subTransaction': 0, 'account':"10100 - Cash", 'description':"", 'debit':"", 'credit':"37000"},
    {'date':'date2', 'transaction': 1, 'subTransaction': 1, 'account':"11000 - Land", 'description':"", 'debit':"37000", 'credit':""},

                   ]

def collect_transactions(entry_list):
    transactions = defaultdict(list)
    for idx, entry in enumerate(entry_list):
        transactions[entry['transactionId']].append({'entry':entry, 'row':idx})
    return transactions.values()

def entriesMatch(e1, e2):
    for k in ['date', 'account', 'amount']:
        if str(e1[k]) != str(e2[k]):
            return False
    return True

def transactionsSubset(t1, t2):

    for entry1 in t1:
        hasMatch = False
        for entry2 in t2:
            if entriesMatch(entry1['entry'], entry2['entry']):
                hasMatch = True
                break
        if not hasMatch:
            return False

    return True
    
def grade(student_answers, correct_answers):
    Results = namedtuple('Results', ['rowStatus', 'expectedTransactions', 'transactionsCorrect', 'transactionsIncorrect', 'score'])

    student = collect_transactions(student_answers)
    correct = collect_transactions(correct_answers)
    
    submittedTransactions = len(student)
    expectedTransactions = len(correct)
    transactionsCorrect = 0
    transactionsIncorrect = 0

    rowStatus = [False]*len(student_answers)

    for trans1 in student:

        hasMatch = False
        for idx, trans2 in enumerate(correct):
            # logic valid unless both the student and correct transactions are multisets with different
            # duplicate entries; but a correct answer never has a transaction with duplicate entries
            if len(trans1)==len(trans2) and transactionsSubset(trans1, trans2) and transactionsSubset(trans2, trans1):
                hasMatch = True
                transactionsCorrect += 1
                del correct[idx]
                break

        if not hasMatch:
            transactionsIncorrect += 1

        for entry in trans1:
            rowStatus[entry['row']] = hasMatch
    if submittedTransactions <= expectedTransactions:
        score = float(transactionsCorrect) / max(1, expectedTransactions)
    else:
        score = max(0, float(transactionsCorrect - transactionsIncorrect)) / max(1, expectedTransactions)

    return Results(rowStatus, expectedTransactions, transactionsCorrect, transactionsIncorrect, score)

if __name__=='__main__':
    print grade(student_answers, correct_answers)

    
