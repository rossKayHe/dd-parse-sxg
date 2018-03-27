# Parsing xmlgw logs with pyGrok

Installing pygrok on datadog
> sudo /opt/datadog-agent/embedded/bin/pip --proxy http://webproxysea.nordstrom.net:8181 install pygrok


Parsing metrics out of unstructured logs using dogstreams and python.  Find instructions at: <https://docs.datadoghq.com/guides/logs/>

Add to your /etc/dd-agent/datadog.conf 
> dogstreams: /pathtoyour/log/file.log:parsers:parse_function_name

When running any test, use the python embedded in the datadog agent
> /opt/datadog-agent/embedded/bin/python

To use testgrok2.py pass the line to parse as a parameter
> sudo /opt/datadog-agent/embedded/bin/python testgrok2.py 'Dec 18 15:44:59.0000 sxg0319t07-TESTDMZ-Audit [0x80000001][LogCategory_Nordstrom_MPG_RestGateway_Audit][error] mpgw(MPG_RestGateway): trans(364594903)[error][161.181.96.181] gtid(364594903): |sxg0319t07|364594903|364594903|sqttcsales|partnertransaction/sales|POST -|TEST-DMZ||EP|2017-12-18T15:44:59:224|401|Unauthorized WWW-Authenticate: Basic realm=login X-Backside-Transport: FAIL FAIL Content-Type: text/xml Connection: close|268|FP|2017-12-18T15:44:58:961|SP|2017-12-18T15:44:59:160|TP|2017-12-18T15:44:59:193||||'
