
# Agent Communication
[Return to Index](README.md)

- [Manager V1 API](Manager_API_V1.md)

Communication between the agent and manager is via the manager's api server. The agent polls the manager for updates and pulls the details it needs from the manager sends it's updates back to the manager. The agent always initiates the communication as this simplifies the network communication and requires only 1 firewll rule to be opened for the manager rather than 1 firewll rule per agent as some other perfromance test tools require.

## V1 Manager API
In RFSwarm versions prior to RFSwarm V2 these api endpoints were at the root of the api server [Manager V1 API](Manager_API_V1.md)

## V2 Manager API
In RFSwarm V2 these api endpoints have been moved to the path `/api` followed by the major version number:
- `/api/v1` for the deprecated v1 api endpoints, this is retained for compatability with v1 agents during the migration to RFSwarm V2
- `/api/v2` for the new v2 api endpoints.

The details of the [Manager V2 API](Manager_API_V2.md)

