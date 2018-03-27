from pygrok import Grok
import time
from datetime import datetime
from dateutil.parser import parse
import sys
from copy import deepcopy

custom_pats = {'NOTPIPE' : '[^|]+'}
    
pattern = '%{SYSLOGTIMESTAMP:log_timestamp} %{NOTSPACE:log_type} \\[%{USERNAME}\\]\\[%{USERNAME:event_source}\\]\\[%{USERNAME:log_level}\\] mpgw\\(%{WORD:service}\\): trans\\(%{NUMBER}\\)\\[%{WORD}\\]\\[%{IPV4}\\] gtid\\(%{NUMBER}\\): \\|%{WORD:server_name}\\|%{NOTPIPE}?\\|%{NOTPIPE}?\\|%{NOTPIPE:consumer_name}?\\|%{NOTPIPE:service_name}\\|%{NOTPIPE:operation_name}?\\|%{NOTPIPE:environment}\\|%{NOTPIPE}?\\|%{WORD}\\|%{TIMESTAMP_ISO8601}\\|%{NOTPIPE:error_code}?\\|%{NOTPIPE:error_description}?\\|%{INT:transaction_time:int}\\|%{WORD}\\|%{TIMESTAMP_ISO8601}\\|%{WORD}?\\|%{TIMESTAMP_ISO8601}(\\|%{WORD}\\|%{TIMESTAMP_ISO8601})?\\|%{NOTPIPE:fault_type}?\\|%{NOTPIPE}?\\|%{NOTPIPE}?(\\|)?(\\|%{NOTPIPE:errorMessage}\\|)?(\\|%{NOTPIPE})?'
 
grok = Grok(pattern, custom_patterns = custom_pats)
# Convert the attribute string field into a dictionary
attr_dict = grok.match(sys.argv[1])
if not attr_dict:
    print('error parsing  --' + sys.argv[1])
    sys.exit(0)

# Add svc_csmr_op field for searching on
if  attr_dict['service_name'] is not None:
    attr_dict['svc_csmr_op'] = attr_dict['service_name']+':'+str(attr_dict['consumer_name'])+':'+str(attr_dict['operation_name'])

# Add metric_type
attr_dict['metric_type'] = 'counter'
attr_trans = deepcopy(attr_dict)
attr_trans['metric_type'] = 'guage'

# Convert the iso8601 date into a unix timestamp, assuming the timestamp
# string is in the same timezone as the machine that's parsing it.
date = time.mktime(parse(attr_dict['log_timestamp']).timetuple())

# Set the metric name
metric_name = "sxg_audit.events"

# Return the output as a tuple
tup_events = (metric_name, date, 1, attr_dict)
tup_trans = ('sxg_audit.transaction_time', date, long(attr_trans['transaction_time']), attr_trans)
rtn = [tup_trans, tup_events]
# Check for error_code 500 or 411
if (int(attr_dict['error_code']) >= 500 and int(attr_dict['error_code']) <= 511) or int(attr_dict['error_code']) == 411: 
    attr_dict['is_error'] = 1
    tup_errors = ('sxg_audit.errors' ,date, 1, attr_dict)
    rtn = [tup_trans, tup_events, tup_errors]
print(rtn)
