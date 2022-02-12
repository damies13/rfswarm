
[Index](README.md)

## Agent Communication

In this page the generic host names manager and myagent are used, replace manager with the host name of the machine that is running rfswarm.py and myagent with the host name of the machine that is running rfswarm_agent.py

- [Get /](#Get-)
- [POST /AgentStatus](#POST-AgentStatus)
- [POST /Jobs](#POST-Jobs)
- [POST /Scripts](#POST-Scripts)
- [POST /File](#POST-File)
- [POST /Result](#POST-Result)
- [POST /Metric](#post-metric)

### Get /
HTTP GET http://manager:8138/

Response Body:
```
{
    "POST": {
        "AgentStatus": {
            "URI": "/AgentStatus",
            "Body": {
                "AgentName": "<Agent Host Name>",
                "Status": "<Agent Status>",
                "AgentIPs": [
                    "<Agent IP Address>",
                    "<Agent IP Address>"
                ],
                "Robots": "<sum>",
                "CPU%": "0-100",
                "MEM%": "0-100",
                "NET%": "0-100"
            }
        },
        "Jobs": {
            "URI": "/Jobs",
            "Body": {
                "AgentName": "<Agent Host Name>"
            }
        },
        "Scripts": {
            "URI": "/Scripts",
            "Body": {
                "AgentName": "<Agent Host Name>"
            }
        },
        "File": {
            "URI": "/File",
            "Body": {
                "AgentName": "<Agent Host Name>",
                "Action": "<Upload/Download/Status>",
                "Hash": "<File Hash, provided by /Scripts>"
            }
        },
        "Result": {
            "URI": "/Result",
            "Body": {
                "AgentName": "<Agent Host Name>",
                "ResultName": "<A Text String>",
                "Result": "<PASS | FAIL>",
                "ElapsedTime": "<seconds as decimal number>",
                "StartTime": "<epoch seconds as decimal number>",
                "EndTime": "<epoch seconds as decimal number>",
                "ScriptIndex": "<Index>",
                "Robot": "<user number>",
                "Iteration": "<iteration number>",
                "Sequence": "<sequence number that ResultName occurred in test case>"
            }
        },
        "Metric": {
            "URI": "/Metric",
            "Body": {
                "PrimaryMetric": "<primary metric name, e.g. AUT Hostname>",
                "MetricType": "<metric type, e.g. AUT Web Server>",
                "MetricTime": "<epoch time the metric was recorded>",
                "SecondaryMetrics": {
                    "Secondary Metric Name, e.g. CPU%": "<value, e.g. 60>",
                    "Secondary Metric Name, e.g. MEMUser": "<value, e.g. 256Mb>",
                    "Secondary Metric Name, e.g. MEMSys": "<value, e.g. 1Gb>",
                    "Secondary Metric Name, e.g. MEMFree": "<value, e.g. 2Gb>",
                    "Secondary Metric Name, e.g. CPUCount": "<value, e.g. 4>"
                }
            }
        }
    }
}
```

### POST /AgentStatus
HTTP POST http://manager:8138/AgentStatus

Request Body:
```
{
    "AgentName": "myagent",
    "Status": "Ready",
    "AgentIPs": ["192.168.1.150", "fe80::1c80:a965:7be5:d524"],
    "Robots": "0",
    "CPU%": "3.4",
    "MEM%": "20.51",
    "NET%": "0.01"
}
```

Response Body:
```
{
    "AgentName": "myagent",
    "Status": "Updated"
}
```

### POST /Jobs
HTTP POST http://manager:8138/Jobs

Request Body:
```
{
    "AgentName": "myagent"
}
```

Response Body:
```
{
    "AgentName": "myagent",
    "StartTime": 1572057404,
    "EndTime": 1572064628,
    "RunName": "Scenario_1572057404",
	"Abort": false,
	"UploadMode": "err",
    "Schedule": {
        "1_1": {
            "ScriptHash": "c4307dee904afe7df89fa33d193a7d30",
            "Test": "Browse Store Products",
            "StartTime": 1572057416,
            "EndTime": 1572064616,
            "id": "1_1"
        },
        "1_2": {
            "ScriptHash": "c4307dee904afe7df89fa33d193a7d30",
            "Test": "Browse Store Products",
            "StartTime": 1572057428,
            "EndTime": 1572064628,
            "id": "1_2"
        }
    }
}
```

### POST /Scripts
HTTP POST http://manager:8138/Scripts

Request Body:
```
{
    "AgentName": "myagent"
}
```

Response Body:
```
{
    "AgentName": "myagent",
    "Scripts": [
        {
            "File": "OC_Demo.robot",
            "Hash": "c4307dee904afe7df89fa33d193a7d30"
        },
        {
            "File": "resources/OC_Demo.resource",
            "Hash": "904afec4307dee7df89fa33d193a7d30"
        },
        {
            "File": "resources/perftest.resource",
            "Hash": "33d193a7d30904afec4307dee7df89fa"
        }
    ]
}
```

### POST /File
HTTP POST http://manager:8138/File

Request Bodies:
```
{
    "AgentName": "myagent",
    "Action": "Download",
    "Hash": "33d193a7d30904afec4307dee7df89fa"
}

{
    "AgentName": "myagent",
    "Action": "Status",
    "Hash": "33d193a7d30904afec4307dee7df89fa"
}

{
    "AgentName": "myagent",
    "Action": "Upload",
    "Hash": "33d193a7d30904afec4307dee7df89fa"
    "File": "resources/perftest.resource",
    "FileData": <This field will contain a string that is a base64 encoded
                lzma (7zip) compressed version of the file. The agent will
                lzma compress, base64 encode the string>
}
```

Response Body:
```
{
    "AgentName": "myagent",
    "Hash": "33d193a7d30904afec4307dee7df89fa",
    "File": "resources/perftest.resource",
    "FileData": <This field will contain a string that is a base64 encoded
                lzma (7zip) compressed version of the file. The agent will base64
                decode the string, lzma decompress, then save to a file using the
                relative file path above relative to the agents temp directory>
}

{
    "AgentName": "myagent",
    "Hash": "33d193a7d30904afec4307dee7df89fa",
    "Exists": "<True/False>"
}

{
    "AgentName": "myagent",
    "Hash": "33d193a7d30904afec4307dee7df89fa",
    "Result": "Saved"
}
```

### POST /Result
HTTP POST http://manager:8138/Result

Request Body:
```
{
    "AgentName": "myagent",
    "ResultName": "Page title is \"Your Store\".",
    "Result": "PASS",
    "ElapsedTime": 0.003000020980834961,
    "StartTime": 1572435546.383,
    "EndTime": 1572435546.386,
    "ScriptIndex": "1",
    "Robot": "1",
    "Iteration": 5,
    "Sequence": 2
}
```

Response Body:
```
{
    "AgentName": "myagent",
    "Result": "Queued"
}
```

### POST /Metric
HTTP POST http://manager:8138/Metric

Request Body:
```
{
    "PrimaryMetric": "my_aut_server",
    "MetricType": "AUT Web",
    "MetricTime": "1609924920",
    "SecondaryMetrics": {
        "vmstat: Mach Virtual Memory Statistics": "(page size of 4096 bytes)",
        "vmstat: Pages free": "5091.",
        "vmstat: Pages active": "269271.",
        "vmstat: Pages inactive": "269384.",
        "vmstat: Pages speculative": "113.",
        "vmstat: Pages throttled": "0.",
        "vmstat: Pages wired down": "226965.",
        "vmstat: Pages purgeable": "2108.",
        "vmstat: Translation faults": "12387345.",
        "vmstat: Pages copy-on-write": "493339.",
        "vmstat: Pages zero filled": "5337415.",
        "vmstat: Pages reactivated": "13285594.",
        "vmstat: Pages purged": "70090.",
        "vmstat: File-backed pages": "104388.",
        "vmstat: Anonymous pages": "434380.",
        "vmstat: Pages stored in compressor": "624330.",
        "vmstat: Pages occupied by compressor": "277482.",
        "vmstat: Decompressions": "1351065.",
        "vmstat: Compressions": "2174715.",
        "vmstat: Pageins": "1582188.",
        "vmstat: Pageouts": "166068.",
        "vmstat: Swapins": "296166.",
        "vmstat: Swapouts": "315460."
    }
}
```

Response Body:
```
{
    "Metric": "my_aut_server",
    "Result": "Queued"
}
```
