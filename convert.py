import sys
import importlib

extensions = ['docx', 'html', 'mediawiki']

def error(message):
    print message
    print "Usage: python convert.py [inputfile.{%s}] [output filename (optional, defaults to inputfil.md)]" % ','.join(extensions)
    exit(1)

def valid_inputfile(filename):
    correct_extension = lambda filename: any([filename.endswith('.' + extension) for extension in extensions])
    return not filename.startswith('.') and correct_extension(filename)

def get_output_filename(input_filename):
    return input_filename[:input_filename.rfind('.')] + '.md'
# There must always be at least one argument (the input filename)
if len(sys.argv) < 2:
    error("Please enter an input filename")

input_filename = sys.argv[1]
if not valid_inputfile(input_filename):
    error("Invalid input filename - missing file, or missing extension?")

if len(sys.argv) > 2:
    # The output filename is specified, so save that
    output_filename = sys.argv[2]
else:
    # Otherwise, it should be everything before the last . plus .md
    output_filename = get_output_filename(input_filename)

try:
    input_file = open(input_filename, 'rt')
    input_content = input_file.read()
except IOError:
    error("Cannot open the input file. Does it not exist?")
output_file = open(output_filename, 'wt')

# Now figure out what format the input file is in
for extension in extensions:
    if input_filename.endswith('.' + extension):
        input_format = extension

markdownify = importlib.import_module('formats.' + input_format).markdownify

output_file.write(markdownify(input_content))

print "Successfully converted contents of %s into markdown (saved as %s)" % (input_filename, output_filename)
