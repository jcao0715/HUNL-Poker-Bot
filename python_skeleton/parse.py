import ast
from tqdm import tqdm
import pickle

with open('python_skeleton/auction_strat.txt', 'r') as f:
    strategy = f.read()

lines = strategy.split('\n')

def process_line(line):
    parts = line.split('  ')
    parts = [part for part in parts if part != '']
    parts = [part.lstrip() for part in parts]
    if len(parts) > 2:
        parts[2] = '-1' if parts[2] == 'A 0' else parts[2]

    if len(parts) == 3 and not parts[1].isdigit():
        freq = ast.literal_eval(parts.pop())
        freq = [float(x) for x in freq]

        bucket = tuple(map(int, parts[0]))
        board = parts[1]
        return bucket, board, freq
    else:
        last = parts.pop().split(' ', 1)
        last[-1] = ast.literal_eval(last[-1])
        last[-1] = [float(x) for x in last[-1]]

        bucket = tuple(map(int, parts))
        return bucket, last[0], last[1]

parsed_lines = [process_line(line) for line in tqdm(lines) if '?' in line]
strategy_dict = {}
for bucket, board, freq in parsed_lines:
    if bucket not in strategy_dict:
        strategy_dict[bucket] = {}
    strategy_dict[bucket][board] = freq





# print('new_freq', new_freq)
# print(parsed_lines)

new_parsed = []
for a, b, freq in parsed_lines:
    new_freq = [0]*len(freq)
    high_index = freq.index(max(freq))
    for val in range(len(freq)):

        if freq[val] < 0.06:
            new_freq[high_index] += freq[val]
            
        else:
            new_freq[val] += freq[val]
    
    new_parsed.append((a, b, new_freq))

strategy_dict = {}
for bucket, board, freq in new_parsed:
    if bucket not in strategy_dict:
        strategy_dict[bucket] = {}
    strategy_dict[bucket][board] = freq

with open('python_skeleton/strategy_dict.pkl', 'wb') as f:
    pickle.dump(strategy_dict, f)