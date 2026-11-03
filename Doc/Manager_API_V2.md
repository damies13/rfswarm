# Manager API V2
[Return to Index](README.md)

What's new with the v2 api:
- REST compliant API
- all data can be accessed via the api so that the webui can use this api to render it's data



/scenario - everything related to the test plan

    /scenario/settings
    /scenario/plan/
    /scenario/monitoring/

/agent - agent registration and communication

    /agent/jobs

/jobs - list all job id's

    /jobs/<job_id> - job details

/result - read/write all result related info
/metric - read/write all metric related info