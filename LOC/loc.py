import argparse
import cProfile
import math
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import matplotlib.pyplot as plt
# import mathplotlib.pyplot as plt
import pandas as pd
from pygount import ProjectSummary, SourceAnalysis, analysis

parser = argparse.ArgumentParser()
parser.add_argument('scan_path', type=str)
parser.add_argument('-o', '--out', required=False,
                    help='output file name', type=str)
args = parser.parse_args()
scan_path = args.scan_path
output_file = args.out


def to_dict(self):
    return {
        'code': self.code,
        'doc': self.documentation,
        'empty': self.empty,
        'string': self.string,
        'language': self.language,
        'path': self.path
    }


# monkey patching analysis result to be able to convert it to dataframe
SourceAnalysis.to_dict = to_dict


def first_digit(num):
    '''
    returns the first digit of a number. e.g. 54 -> 5, 0.456 -> 4
    '''
    stripped_num = str(num).lstrip('0.')
    if stripped_num:
        return stripped_num[:1]
    else:
        return None


def analyse_file(source_path):
    if not source_path.is_file():
        return

    source_analysis = SourceAnalysis.from_file(source_path, scan_path)

    if not source_analysis.state == analysis.SourceState.analyzed:
        return

    return source_analysis


def scan_code(scan_path):
    source_paths = list((Path(scan_path)).rglob('*'))

    with Pool(10) as p:
        raw_analysis = list(filter(None, p.map(analyse_file, source_paths)))

    df = pd.DataFrame.from_records([analysis.to_dict()
                                    for analysis in raw_analysis])

    return df


df = scan_code(scan_path)

# get first digit for different columns
df['code_digit'] = df['code'].map(first_digit)
df['doc_digit'] = df['doc'].map(first_digit)
df['empty_digit'] = df['empty'].map(first_digit)
df['string_digit'] = df['string'].map(first_digit)

# define useful parts to draw graphs
benford_base = pd.DataFrame([math.log10(1 + 1 / d) for d in range(1, 10)])
labels = [str(i) for i in range(1, 10)]


def normalized_count(pandas_count):
    counts = [0] * 9
    for index_str, count in zip(pandas_count.axes[0], pandas_count):
        counts[int(index_str) - 1] = count
    return counts


def print_figures(dataframe, language, output_file=None):
    # plot the different occurences
    fig, axs = plt.subplots(2, 2, constrained_layout=True)

    code_count = normalized_count(
        dataframe.groupby(['code_digit'])['code'].count())
    axs[0, 0].bar(labels, code_count)
    axs[0, 0].plot(benford_base * sum(code_count), color='red')
    axs[0, 0].set_title('code')

    doc_count = normalized_count(
        dataframe.groupby(['doc_digit'])['doc'].count())
    axs[1, 0].bar(labels, doc_count)
    axs[1, 0].plot(benford_base * sum(doc_count), color='red')
    axs[1, 0].set_title('doc')

    empty_count = normalized_count(
        dataframe.groupby(['empty_digit'])['empty'].count())
    axs[0, 1].bar(labels, empty_count)
    axs[0, 1].plot(benford_base * sum(empty_count), color='red')
    axs[0, 1].set_title('empty')

    string_count = normalized_count(
        dataframe.groupby(['string_digit'])['string'].count())
    axs[1, 1].bar(labels, string_count)
    axs[1, 1].plot(benford_base * sum(string_count), color='red')
    axs[1, 1].set_title('string')

    plt.suptitle(f'{scan_path}: {language}')

    plt.show()

    if output_file:
        fig.savefig(output_file)


for language in df.language.unique():
    language_df = df[df.language == language]

    language_output_file = None
    if output_file:
        language_output_file = f'{language}_{output_file}'

    print_figures(language_df, language, language_output_file)
