scalyr-tool
===========

Command-line tool for accessing Scalyr services. Four commands are currently supported:

- **query**: Retrieve log data
- **get-file**: Fetch a configuration file
- **put-file**: Create or update a configuration file
- **list-files**: List all configuration files


## Installation

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


## Querying logs

The "query" command allows you to search and filter your logs, or simply retrieve raw log data. The
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
    
    # Display the last 1000 entries in the log tagged as source=accessLog. Print only the status
    # and path, in CSV format.
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
    --output=multiline|singleline|csv|json|json-pretty
        How to display the log records (see below).

#### Output formats

By default, the query command outputs log records in a fairly verbose format designed for manual
viewing. You can get something more like a classic log view by specifying a columns list, as shown in
one of the examples above.

The 'singleline' output option is similar to the default, but places all of a record's attributes on
a single line. This is denser, but can be harder to read.

The 'csv' output option emits one line per log record, in Excel comma-separated-value format. To use
this option, you must specify the columns argument.

The 'json' output option emits the raw JSON response from the server, as documented at
https://www.scalyr.com/logapihttp (look for discussion of the Query method).

The 'json-pretty' output option also emits the JSON response from the server, but prettyprinted.


## Retrieving configuration files

The "get-file" command allows you to retrieve a configuration file, writing the file text to stdout.
Configuration files are used to define log parsers, dashboards, alerting rules, and more. Any page
on the Scalyr web site which contains a full-page text editor, is editing a configuration file.

Using the get-file command is simple:

    # Display the alerts file
    scalyr get-file /scalyr/alerts

    # Display the "Foo" dashboard
    scalyr get-file /scalyr/dashboards/Foo

Complete argument list:

    scalyr get-file file-path [options...]

    --version
        Prints the current version number of this tool.
    --token=xxx
        Specify the API token. For this command, should be a "Read Config" token.
    --verbose
        Writes detailed progress information to stderr.


## Creating or updating configuration files

The "put-file" command allows you to create or overwrite a configuration file, taking the new
file content from stdin.

Using the put-file command is simple:

    # Overwrite the alerts file
    scalyr put-file /scalyr/alerts < alerts.json

    # Create or overwrite the "Foo" dashboard
    scalyr put-file /scalyr/dashboards/Foo < fooDashboard.json

Complete argument list:

    scalyr put-file file-path [options...]

    --version
        Prints the current version number of this tool.
    --token=xxx
        Specify the API token. For this command, should be a "Write Config" token.
    --verbose
        Writes detailed progress information to stderr.


## Listing configuration files

The "list-files" command lists all configuration files:

    scalyr list-files

Complete argument list:

    scalyr list-files [options...]

    --version
        Prints the current version number of this tool.
    --token=xxx
        Specify the API token. For this command, should be a "Read Config" token.
    --verbose
        Writes detailed progress information to stderr.


## Revision History

#### Feb. 21, 2014: version 0.1

Initial release.