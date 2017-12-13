import os
import sys
import time
import numpy as np
from random import shuffle

from model_factory import fit_model, get_model
from sklearn.model_selection import KFold

from candidates_creator import compute_candidates
from validation import evaluate
from word_vectorizer import WordEmbeddings


def save_results(results, output_csv_path):
    import csv
    with open(output_csv_path, 'w') as outcsv:
        # configure writer to write standard csv file
        writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL,
                            lineterminator='\n')
        writer.writerow(
            ['P_macro', 'R_macro', 'F1_macro', 'TNR_macro',
             'P_micro', 'R_micro', 'F1_micro', 'TNR_micro',
             'P_macro_t', 'R_macro_t', 'F1_macro_t', 'TNR_macro_t',
             'P_micro_t', 'R_micro_t', 'F1_micro_t', 'TNR_micro_t'])
        for item in results:
            writer.writerow(item)


def execute_experiments(dataset, w2v_model, n_splits, model_option, output_csv_path):
    results = []

    shuffle(dataset)
    folds = KFold(n_splits=n_splits, random_state=7, shuffle=False)
    splits = [(train_index, test_index) for train_index, test_index in folds.split(dataset)]

    prep_dataset = np.array([[row[0], row[1], row[2], compute_candidates(row, w2v_model)] for row in dataset])
    for train_index, test_index in splits:
        train, test = prep_dataset[train_index], prep_dataset[test_index]
        model = fit_model(model_option, train, w2v_model)
        results.append(evaluate(test, model))

    save_results(results, output_csv_path)


def main():
    args = sys.argv[1:]

    if len(args) != 6:
        print('Wrong number of arguments')
        print('Usage (relative paths!!): main.py <dataset path> <lang> <word2vec model path>'
              ' <# folds> <model option> <output csv path>')
        exit()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    dataset = [eval(line) for line in open(os.path.join(dir_path, args[0]), encoding='utf-8')]
    lang = args[1]
    start = time.time()
    w2v_model = WordEmbeddings(lang, os.path.join(dir_path, args[2]))
    end = time.time()
    print('WV loaded', (end - start))
    n_splits = int(args[3])
    model_option = get_model(args[4])
    output_csv_path = os.path.join(dir_path, args[5])

    execute_experiments(dataset, w2v_model, n_splits, model_option, output_csv_path)


if __name__ == '__main__':
    main()