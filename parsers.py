from pygrok import Grok
import time
import json
from datetime import datetime
from dateutil.parser import parse
from datadog import statsd 
import sys

def parse_sxglogs(logger, line):
    # Define the Grok patterns
    custom_pats = {'NOTPIPE' : '[^|]+'}
    pattern = '%{SYSLOGTIMESTAMP:log_timestamp} %{NOTSPACE:log_type} \\[%{USERNAME}\\]\\[%{USERNAME:event_source}\\]\\[%{USERNAME:log_level}\\] mpgw\\(%{WORD:service}\\): trans\\(%{NUMBER}\\)\\[%{WORD}\\]\\[%{IPV4}\\] gtid\\(%{NUMBER}\\): \\|%{WORD:server_name}\\|%{NOTPIPE}?\\|%{NOTPIPE}?\\|%{NOTPIPE:consumer_name}?\\|%{NOTPIPE:service_name}\\|%{NOTPIPE:operation_name}?\\|%{NOTPIPE:environment}((\\|%{NOTPIPE}?)+)?\\|EP\\|%{TIMESTAMP_ISO8601}\\|%{NOTPIPE:error_code}?\\|%{NOTPIPE:error_description}?\\|%{INT:transaction_time:int}\\|%{WORD}\\|%{TIMESTAMP_ISO8601}\\|%{WORD}?\\|%{TIMESTAMP_ISO8601}?(\\|%{WORD}\\|%{TIMESTAMP_ISO8601})?\\|%{NOTPIPE:fault_type}?\\|%{NOTPIPE}?\\|%{NOTPIPE}?(\\|)?(\\|%{NOTPIPE:errorMessage}\\|)?(\\|%{NOTPIPE})?'

    grok = Grok(pattern, custom_patterns = custom_pats)
    
    # Convert the attribute string field into a dictionary
    attr_dict = grok.match(line)

    # If unable to match with Grok, return None
    if not attr_dict:
        f=open("/tmp/grok_fail", "a+")
        f.write('no grok match-- ')
        f.write(line)
        f.write('\n')
        f.close
        return None

    # Convert the iso8601 date into a unix timestamp, assuming the timestamp
    # string is in the same timezone as the machine that's parsing it.
    date = int(time.mktime(parse(attr_dict['log_timestamp']).timetuple()))
    log_timestamp = attr_dict['log_timestamp']
    
    # Remove transaction_time from the dictionary
    transaction_time = attr_dict['transaction_time']
    attr_dict.pop('transaction_time', None)

    # Remove log_timestamp from the dictionary.  Do not send as tag
    attr_dict.pop('log_timestamp', None)

    attr_list = []
    for k,v in attr_dict.items():
        attr_list.append(str(k)+':'+str(v))
    statsd.gauge('sxg_audit.transaction_time', transaction_time, tags=attr_list)

    # Check for error_code 500 or 401
    if attr_dict['error_code'] is not None:
        if (int(attr_dict['error_code']) >= 500 and int(attr_dict['error_code']) <= 511) or int(attr_dict['error_code']) == 401: 
            attr_dict['is_error'] = 1
            attr_list.append('is_error:1')
            statsd.increment('sxg_audit.errors', value=1, tags=attr_list)

    statsd.increment('sxg_audit.events', value=1, tags=attr_list)

    # check pkgtrk
    # if attr_dict['service_name'] == 'pkgtrk':
    #     f=open("/tmp/ddparsed", "a+")
    #     f.write(log_timestamp)
    #     f.write(json.dumps(attr_list))
    #     f.write('\n')
    #     f.close

