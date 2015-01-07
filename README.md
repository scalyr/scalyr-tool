scalyr-tool
===========

Command-line tool for accessing Scalyr services. Seven commands are currently supported:

- **query**: Retrieve log data
- **numeric-query**: Retrieve numeric / graph data
- **facet-query**: Retrieve common values for a field
- **timeseries-query**: Retrieve numeric / graph data from a timeseries
- **create-timeseries**: Create a timeseries for fast numeric queries
- **get-file**: Fetch a configuration file
- **put-file**: Create or update a configuration file
- **list-files**: List all configuration files


## Installation

Simply download the script file and make it executable. For instance:

    curl https://raw.githubusercontent.com/scalyr/scalyr-tool/master/scalyr > scalyr
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
    scalyr query '$source="accessLog"' --output=csv --columns='status,uriPath' --count=1000

Complete argument list:

    scalyr query [filter] [options...]
        The filter specifies which log records to return. It uses the same syntax as the "Expression"
        field in the [log view](https://www.scalyr.com/events?mode=log).

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
    --version
        Prints the current version number of this tool.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --verbose
        Writes detailed progress information to stderr.

#### Output formats

By default, the query command outputs log records in a fairly verbose format designed for manual
viewing. You can get something more like a classic log view by specifying a columns list, as shown in
one of the examples above.

The 'singleline' output option is similar to the default, but places all of a record's attributes on
a single line. This is denser, but can be harder to read.

The 'csv' output option emits one line per log record, in Excel comma-separated-value format. To use
this option, you must specify the columns argument.

The 'json' output option emits the raw JSON response from the server, as documented at
https://www.scalyr.com/help/api#query.

The 'json-pretty' output option also emits the JSON response from the server, but prettyprinted.

#### Usage limits

Your command line and API queries are limited to 30,000 milliseconds of server processing time,
replenished at 36,000 milliseconds per hour. If you exceed this limit, your queries will be intermittently
refused. (Your other uses of Scalyr, such as log uploading or queries via the web site, will not be impacted.)
If you need a higher limit, drop us a line at support@scalyr.com.


## Fetching numeric data

The "numeric-query" command allows you to retrieve numeric data, e.g. for graphing. You can count the
rate of events matching some criterion (e.g. error rate), or retrieve a numeric field (e.g. response
size).

If you will be be invoking the same query repeatedly (e.g. in a script), you may want to use the
create-timeseries command to create a timeseries for your query. Timeseries queries execute near-
instantaneously, and avoid exhausting your query execution limit (see below).

Here are some usage examples:

    # Count the rate (per second) of occurrences of "/login" in all logs, in each of the last 24 hours
    scalyr numeric-query '"/login"' --start 24h --buckets 24
    
    # Display the average response size of all requests in the last hour
    scalyr numeric-query '$dataset="accesslog"' --function 'bytes' --start 1h

Complete argument list:

    scalyr numeric-query [filter] --start xxx [options...]
        The filter specifies which log records to process. It uses the same syntax as the "Expression"
        field in the [log view](https://www.scalyr.com/events?mode=log).

    --function=xxx
        The value to compute from the matching events. You can use any function listed in
        https://www.scalyr.com/help/query-language#graphFunctions, except for fraction(expr). For
        example: 'mean(x)' or 'median(responseTime)', if x and responseTime are fields of your log.
        You can also specify a simple field name, such as 'responseTime', to return the mean value of
        that field. If you omit the function argument, the rate of matching events per second will be
        returned. Specifying 'rate' yields the same result.
    --start=xxx
        Specify the beginning of the time range to query. Uses the same syntax as the "Start" field is
        the log view. You must specify this argument.
    --end=xxx
        Specify the end of the time range to query. Uses the same syntax as the "End" field in the log
        view. Defaults to the current time.
    --buckets=nnn
        The number of numeric values to return. The time range is divided into this many equal slices.
        For instance, suppose you query a four-hour period, with buckets = 4. The query will return four
        numbers, each covering a one-hour period. You may specify a value from 1 to 5000; 1 is the default.
    --output=csv|json|json-pretty
        How to display the results. 'csv' prints all values on a single line, separated by commas.
        'json' prints the raw JSON response from the server, as documented at
        https://www.scalyr.com/help/api#numericQuery. 'json-pretty' also prints the JSON response,
        but prettyprinted.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --version
        Prints the current version number of this tool.
    --verbose
        Writes detailed progress information to stderr.

## Fetching facet counts

The "facet-query' command allows you to retrieve the most common values for a field. For instance, you can
find the most common URLs accessed on your site, the most common user-agent strings, or the most common
response codes returned. (If a very large number of events match your search criteria, the results will be
based on a random subsample of at least 500,000 matching events.)

Here are some usage examples:

    curl 'https://www.scalyr.com/api/facetQuery?queryType=facet&field=uriPath&startTime=1h&token=XXX'

    # Display the most common HTTP request URLs in the last 24 hours.
    scalyr facet-query '$dataset="accesslog"' uriPath --start 24h
    
    # Display the most common HTTP response codes for requests to index.html.
    scalyr facet-query 'uriPath="/index.html"' status --start 24h

Complete argument list:

    scalyr facet-query filter field --start xxx [options...]
        The filter specifies which log records to process. It uses the same syntax as the "Expression"
        field in the [log view](https://www.scalyr.com/events?mode=log).

    --count=nnn
        How many distinct values to return. You may specify a value from 1 to 1000; 100 is the default.
    --start=xxx
        Specify the beginning of the time range to query. Uses the same syntax as the "Start" field is
        the log view. You must specify this argument.
    --end=xxx
        Specify the end of the time range to query. Uses the same syntax as the "End" field in the log
        view. Defaults to the current time.
    --output=csv|json|json-pretty
        How to display the results. 'csv' prints all values on a single line, separated by commas.
        'json' prints the raw JSON response from the server, as documented at
        https://www.scalyr.com/help/api#numericQuery. 'json-pretty' also prints the JSON response,
        but prettyprinted.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --version
        Prints the current version number of this tool.
    --verbose
        Writes detailed progress information to stderr.


#### Usage limits

Your command line and API queries are limited to 30,000 milliseconds of server processing time,
replenished at 36,000 milliseconds per hour. If you exceed this limit, your queries will be intermittently
refused. (Your other uses of Scalyr, such as log uploading or queries via the web site, will not be impacted.)
If you need a higher limit, drop us a line at support@scalyr.com.


## Fetching numeric data using a timeseries

The "timeseries-query" command allows you to retrieve numeric data using a timeseries defined using the
create-timeseries command. (Note that the [Scalyr API](https://www.scalyr.com/help/api#timeseriesQuery)
allows multiple timeseries queries in a single API invocation, but the command-line tool only supports
one query at a time.)

Usage is similar to the numeric-query command, but you specify a timeseries ID instead of a filter and/or
function. For example:

    scalyr timeseries-query --timeseries 'xxxxxxx' --start 24h --buckets 24
    
(where 'xxxxxxx' is a timeseries ID generated by the create-timeseries command.)

Complete argument list:

    scalyr timeseries-query timeseriesid --start xxx [options...]

    --start=xxx
        Specify the beginning of the time range to query. Uses the same syntax as the "Start" field is
        the log view. You must specify this argument.
    --end=xxx
        Specify the end of the time range to query. Uses the same syntax as the "End" field in the log
        view. Defaults to the current time.
    --buckets=nnn
        The number of numeric values to return. The time range is divided into this many equal slices.
        For instance, suppose you query a four-hour period, with buckets = 4. The query will return four
        numbers, each covering a one-hour period. You may specify a value from 1 to 5000; 1 is the default.
    --output=csv|json|json-pretty
        How to display the results. 'csv' prints all values on a single line, separated by commas.
        'json' prints the raw JSON response from the server, as documented at
        https://www.scalyr.com/help/api#numericQuery. 'json-pretty' also prints the JSON response,
        but prettyprinted.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --version
        Prints the current version number of this tool.
    --verbose
        Writes detailed progress information to stderr.


## Creating timeseries

The "create-timeseries" command allows you to create a timeseries, for later use in the timeseries-query
command. A timeseries precomputes a numeric query, allowing you to execute queries almost instantaneously.
This is useful for queries that you execute repeatedly. If you are using the Scalyr API to feed a home-built
dashboard, alerting system, or other automated tool, timeseries are for you.

It may take up to half an hour for a timeseries to be fully created. During that time, you can query the
timeseries, but queries may not execute as quickly. Recent data is accelerated before older data.

Here are some usage examples:

    # Count the rate (per second) of occurrences of "/login" in all logs
    scalyr create-timeseries '"/login"'
    
    # Compute the average response size of all requests
    scalyr create-timeseries '$dataset="accesslog"' --function 'bytes'

Complete argument list:

    scalyr create-timeseries [filter] [options...]
        The filter specifies which log records to process. It uses the same syntax as the "Expression"
        field in the [log view](https://www.scalyr.com/events?mode=log).

    --function=xxx
        The value to compute from the matching events. You can use any function listed in
        https://www.scalyr.com/help/query-language#graphFunctions, except for fraction(expr). For
        example: 'mean(x)' or 'median(responseTime)', if x and responseTime are fields of your log.
        You can also specify a simple field name, such as 'responseTime', to return the mean value of
        that field. If you omit the function argument, the rate of matching events per second will be
        returned. Specifying 'rate' yields the same result.
    --token=xxx
        Specify the API token. For this command, should be a "Read Logs" token.
    --version
        Prints the current version number of this tool.
    --verbose
        Writes detailed progress information to stderr.


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
