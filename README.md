scalyr-tool
===========

Command-line tool for accessing Scalyr services. Four commands are currently supported:

- **query**: Retrieve log data
- **get-file**: Fetch a configuration file
- **put-file**: Create or update a configuration file
- **list-files**: List all configuration files


# Installation

Simply download the script file and make it executable. For instance:

    curl https://raw.github.com/scalyr/scalyr-tool/master/scalyr > scalyr
    chmod u+x scalyr
    mv scalyr (some directory on your command path)

You also need to make your Scalyr API tokens available to the tool. You can specify the token
on the command line using the --token argument. However, it is more convenient to store your
tokens in environment variables. This also keeps the tokens out of your console window and
command history. On Unix systems, you can add the following to a file like .bash_profile:

    export scalyr_readlog_token='XXX'
    export scalyr_readconfig_token='YYY'
    export scalyr_writeconfig_token='ZZZ'

The values for XXX, YYY, and ZZZ can be found at [scalyr.com/keys](https://www.scalyr.com/keys) -- look
for "Read Logs", "Read Config", and "Write Config" tokens, respectively.

After adding these to .bash_profile, make sure to also paste them into your current console session so
they take effect immediately.


# Querying logs

The query command allows you to search and filter your logs, or simply retrieve raw log data. The
capabilities are similar to the regular [log view](https://www.scalyr.com/events?mode=log), though you
can retrieve more data at once and have several options for output format.

Here are some usage examples:

    # Display the last 10 log records
    scalyr query

    # Display the last 100 log records, showing only timestamp, severity, and message.
    # (Timestamp and severity are always displayed.)
    scalyr query --count=100 --columns='timestamp,severity,message'

    # Display the first 10 log records beginning at 3:00 PM today, from host100.
    scalyr query '$serverHost="host100"' --start='3:00 PM'
    
    # Display the last 1000 entries in the log tagged as source=accessLog. Print only the status and path,
    # in CSV format.
    ./scalyr query '$source="accessLog"' --output=csv --columns='status,uriPath' --count=1000


Complete argument list:

    scalyr query [filter] [options...]
        The filter specifies which log records to return. It uses the same syntax as the "Expression"
        field in the [log view](https://www.scalyr.com/events?mode=log).

    --version
        Prints the current version number of this tool.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --verbose
        Writes detailed progress information to stderr.
    --start=xxx
        Specify the beginning of the time range to query. Uses the same syntax as the "Start" field is
        the log view. Defaults to 1 day ago, or to 1 day before the end time if an end time is given.
    --end=xxx
        Specify the end of the time range to query. Uses the same syntax as the "End" field in the log
        view. Defaults to the current time, or to 1 day after the start time if a start time is given.
    --count=nnn
        How many log records to retrieve, from 1 to 5000. Defaults to 10.
    --mode=head|tail
        Whether to display log records from the start or end of the time range. Defaults to head if a
        start time is given, otherwise to tail.
    --columns="..."
        Which log attributes to display. Used mainly for logs for which you have specified a parser to
        extract attributs from the raw text. Specify one or more attribute names, separated by commas.
    --output=text|csv|json|json-pretty
        How to display the log messages (see below).

## Output formats

By default, the query command outputs log messages in a fairly verbose format designed for manual
viewing. You can get something more like a classic log view by specifying a columns list, as shown in
one of the examples above.

The csv output option emits one line per log message, in Excel comma-separated-value format. To use
this option, you must specify the columns argument.


*** notes




  parser.add_argument('--output', choices=['text', 'csv', 'json', 'jsonPretty'], default='text',
                      help='specifies the format in which matching log messages are displayed')
  args = parser.parse_args()

  columns = args.columns
  output = args.output
  if output == 'csv' and columns == '':
    print >> sys.stderr, 'For CSV output, you must supply a nonempty --columns option'
    sys.exit(1)


  # Get the API token.
  apiToken = getApiToken(args, 'scalyr_readlog_token', 'Read Logs')


  # Send the query to the server.
  response = sendRequest(args, '/api/query', {
    "token": apiToken,
    "queryType": "log",
    "filter": args.filter,
    "startTime": args.start,
    "endTime": args.end,
    "maxCount": args.count,
    "pageMode": args.pageMode,
    "columns": args.columns,
    });


  # Print the log records.
  matches = response['matches']

  if args.output == 'json':
    print responseBody
  elif args.output == 'jsonPretty':
    print json.dumps(response, sort_keys=True, indent=2, separators=(',', ': '))
  elif args.output == 'csv':
    columnList = columns.split(',')
    
    ar = [];
    for i in range(len(columnList)):
      ar.append(columnList[i])
    
    csvBuffer = StringIO.StringIO()
    csvWriter = csv.writer(csvBuffer, dialect='excel')
    csvWriter.writerow(ar)
    for i in range(len(matches)):
      match = matches[i]
      attributes = match.get('attributes')
      for i in range(len(columnList)):
        column = columnList[i]
        ar[i] = match.get(column) or attributes.get(column) or ''
      csvWriter.writerow(ar)

    print csvBuffer.getvalue()
  else:
    # Readable text format
    for i in range(len(matches)):
      match = matches[i]
      
      timestamp = datetime.datetime.fromtimestamp(long(match['timestamp']) / 1E9)
      message = match.get('message')
      if not message:
        message = ''
      attributes = match.get('attributes')

      severity = ['L', 'K', 'J', 'I', 'W', 'E', 'F'][match['severity']];

      print '%s: %s %s' % (timestamp, severity, message)
      for attrName in sorted(attributes.keys()):
        print '  %s = %s' % (attrName, attributes[attrName])





# Implement the "scalyr get-file" command.
def commandGetFile(parser):
  parser.add_argument('filepath', default='',
                      help='server pathname of the file to retrieve, e.g. "/scalyr/alerts"')
  args = parser.parse_args()

  # Send the request to the server.
  response = sendRequest(args, '/getFile', {
    "token": getApiToken(args, 'scalyr_readconfig_token', 'Read Config'),
    "path": args.filepath,
    });

  # Print the file content.
  if response['status'] == 'success/noSuchFile':
    print >> sys.stderr, 'File "%s" does not exist' % (args.filepath)
  else:
    createDate = datetime.datetime.fromtimestamp(long(response['createDate']) / 1000)
    modDate    = datetime.datetime.fromtimestamp(long(response['modDate']) / 1000)

    print >> sys.stderr, 'Retrieved file "%s", version %d, created %s, modified %s, length %s' % (args.filepath, response['version'], createDate, modDate, len(response['content']))
    print response['content']


# Implement the "scalyr put-file" command.
def commandPutFile(parser):
  # Parse the command-line arguments.
  parser.add_argument('filepath', default='',
                      help='server pathname of the file to retrieve, e.g. "/scalyr/alerts"')
  args = parser.parse_args()

  # Send the request to the server.
  content = sys.stdin.read()
  response = sendRequest(args, '/putFile', {
    "token": getApiToken(args, 'scalyr_writeconfig_token', 'Write Config'),
    "path": args.filepath,
    "content": content
    });

  # Print the file content.
  print >> sys.stderr, 'File "%s" updated' % (args.filepath)


# Implement the "scalyr list-files" command.
def commandListFiles(parser):
  # Parse the command-line arguments.
  args = parser.parse_args()

  # Send the request to the server.
  response = sendRequest(args, '/listFiles', {
    "token": getApiToken(args, 'scalyr_readconfig_token', 'Read Config')
    });

  # Print the file content.
  paths = response['paths']
  for i in range(len(paths)):
    print paths[i]






revision history
0.1: initial release
