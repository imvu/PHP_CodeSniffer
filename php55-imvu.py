#!/bin/python

import os
import os.path
import subprocess
import string
import json
import sys

try:
    import argparse
except e:
    print "please install python argparse"
    print "apt-get install python-argparse or pip install argparse"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile-dest', default=os.path.expanduser(os.path.join('~', 'test_results')), dest='outfile_dest')
    parser.add_argument('--file', dest='file')
    parser.add_argument('--print-json', action='store_true')
    parser.add_argument('--print-full', action='store_true')
    args = parser.parse_args()


    try:
        os.makedirs(os.path.expanduser(args.outfile_dest))
    except OSError as e:
        pass
    process = subprocess.Popen(['scripts/phpcs', '--standard=PHPCompatibility', '--runtime-set', 'testVersion', '5.5', '--report-json', '--report-full', args.file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                    )
    stdout, stderr = process.communicate()

    print("PHP_Compatibility_Processing {file}".format(file=args.file))
    parsed = string.split(stdout, '\n', 1)
    json_out = None
    rest = None
    try:
        json_out, rest = parsed
    except ValueError as e:
        json_out = parsed[0]

    if rest is not None:
        with open(os.path.expanduser(os.path.join(args.outfile_dest, '{file}.stdout'.format(file=string.replace(args.file, '/', '_')))), 'w') as f:
            f.write(rest)
        if args.print_full:
            print(rest)
            print('----')

    try:
        data = json.loads(json_out)
    except ValueError as e:
        data = {}
        print("Bad json {0!r}".format(json.out))
        sys.exit(0)

    total_errors = data['totals']['errors']
    total_warnings = data['totals']['warnings']
    
    if (total_errors + total_warnings) > 0:
        with open(os.path.expanduser(os.path.join(args.outfile_dest, '{file}.json'.format(file=string.replace(args.file, '/', '_')))), 'w') as f:
            f.write(json_out)
        if args.print_json:
            print(json_out)
            print('----')



    keys = []
    for x,_ in data['files'].iteritems():
        keys.append(x)

    def message_data(key):
        list_messages = data['files'][key]['messages']
        return map(lambda x: (x['type'], x['message'], x['line']), list_messages)

    messages = map(lambda x: (x, message_data(x)), keys)
    if (total_errors + total_warnings) > 0:
        messages = [('FILE', [('TYPE', 'MESSAGE', 'LINE')])] + messages
        for (file, in_data) in messages:
            for (type, message, line) in in_data:
                print("{file}, {type}, {message}, {line}\n".format(
                    file=file,
                    type=type,
                    message=message,
                    line=line
                    )
                )

