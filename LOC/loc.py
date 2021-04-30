import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
# import mathplotlib.pyplot as plt
import pandas as pd
from pygount import ProjectSummary, SourceAnalysis, analysis

parser = argparse.ArgumentParser()
parser.add_argument('scan_path', type=str)
parser.add_argument('-o', '--out', required=False, help='output file name', type=str)
args = parser.parse_args()
scan_path = args.scan_path
output_file = args.out

# monkey patching analysis result to be able to convert it to dataframe


def to_dict(self):
    return {
        'code': self.code,
        'doc': self.documentation,
        'empty': self.empty,
        'string': self.string,
        'language': self.language,
        'path': self.path
    }


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


source_paths = list(Path(scan_path).rglob('*'))

df = pd.DataFrame()
project_summary = ProjectSummary()
raw_analysis = []
for source_path in source_paths:
    if not source_path.is_file():
        continue

    source_analysis = SourceAnalysis.from_file(source_path, scan_path)

    if not source_analysis.state == analysis.SourceState.analyzed:
        continue

    project_summary.add(source_analysis)
    raw_analysis.append(source_analysis)

df = pd.DataFrame.from_records([analysis.to_dict()
                               for analysis in raw_analysis])


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


# plot the different occurences
fig, axs = plt.subplots(2, 2, constrained_layout=True)

code_count = normalized_count(df.groupby(['code_digit'])['code'].count())
axs[0, 0].bar(labels, code_count)
axs[0, 0].plot(benford_base * sum(code_count), color='red')
axs[0, 0].set_title('code')

doc_count = normalized_count(df.groupby(['doc_digit'])['doc'].count())
axs[1, 0].bar(labels, doc_count)
axs[1, 0].plot(benford_base * sum(doc_count), color='red')
axs[1, 0].set_title('doc')

empty_count = normalized_count(df.groupby(['empty_digit'])['empty'].count())
axs[0, 1].bar(labels, empty_count)
axs[0, 1].plot(benford_base * sum(empty_count), color='red')
axs[0, 1].set_title('empty')

string_count = normalized_count(df.groupby(['string_digit'])['string'].count())
axs[1, 1].bar(labels, string_count)
axs[1, 1].plot(benford_base * sum(string_count), color='red')
axs[1, 1].set_title('string')

plt.suptitle(scan_path)

plt.show()

if output_file:
    fig.savefig(output_file)