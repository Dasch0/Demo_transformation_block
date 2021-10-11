#!/usr/bin/env python
import numpy as np
import math, os, sys, argparse, json, hmac, hashlib, time, random
import pandas as pd

# these are the three arguments that we get in
parser = argparse.ArgumentParser(description='Organization transformation block')
parser.add_argument('--in-directory', type=str, required=True)
parser.add_argument('--out-directory', type=str, required=True)

args, unknown = parser.parse_known_args()

json_data = {
    "protected": {
        "ver": "v1",
        "alg": "none",
    },
    "signature": "0000000000000000000000000000000000000000000000000000000000000000",
    "payload": {
        "device_name": "Dataset for Sensorless Drive Diagnosis",
        "device_type": "Dataset",
        "interval_ms": 0.1,
        "sensors": [
            { "name": "Current", "units": "A" },
        ],
        "values": []
    }
}

# verify that the input file exists and create the output directory if needed
if not os.path.exists(args.in_directory):
    print('--in-file argument', args.in_directory, 'does not exist', flush=True)
    exit(1)

if not os.path.exists(args.out_directory):
    os.makedirs(args.out_directory)

# load and parse the input file
print('Loading input', args.in_directory, flush=True)

files = [f for f in os.listdir(args.in_directory) if f.endswith(".txt")]

for f in files: 
    in_file = os.path.join(args.in_directory, f)
    data_frame = pd.read_csv(in_file, delim_whitespace=True)

    # remove monotonic increasing first column
    data_frame.drop(data_frame.columns[0], axis=1, inplace=True)

    # sum axis together to get a combined audio signal
    summed_signal = (data_frame.to_numpy()[::10].sum(axis=1)).tolist()

    # Take a random 10% of each sample for test data.
    rand_slice_start = int(random.uniform(0, 90000))
    rand_slice_end = rand_slice_start + 10000
    training_before = summed_signal[:rand_slice_start]
    test =  summed_signal[rand_slice_start:rand_slice_end]
    training_after = summed_signal[rand_slice_end:]

    # store training data
    json_copy = json_data.copy()
    json_copy['payload']['values'] = training_before
    # and store as new file in the output directory
    # new file name is classN.parameterN.json
    out_file = os.path.join(args.out_directory, os.path.splitext(os.path.basename(in_file))[0].replace('_', '.') + '.training_0.json')

    with open(out_file, 'w+') as f:
        json.dump(json_copy, f)

    print('Written .json file', out_file, flush=True)

    # store training data
    json_copy = json_data.copy()
    json_copy['payload']['values'] = training_after
    # and store as new file in the output directory
    # new file name is classN.parameterN.json
    out_file = os.path.join(args.out_directory, os.path.splitext(os.path.basename(in_file))[0].replace('_', '.') + '.training_1.json')

    with open(out_file, 'w+') as f:
        json.dump(json_copy, f)

    print('Written .json file', out_file, flush=True)

    # store test data
    json_copy = json_data.copy()
    json_copy['payload']['values'] = test
    # and store as new file in the output directory
    # new file name is classN.parameterN.json
    out_file = os.path.join(args.out_directory, os.path.splitext(os.path.basename(in_file))[0].replace('_', '.') + '.test.json')

    with open(out_file, 'w+') as f:
        json.dump(json_copy, f)

    print('Written .json file', out_file, flush=True)
