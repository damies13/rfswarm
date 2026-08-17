import argparse
from rfswarm_agent.run import run_agent

def configuration():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
    parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
    parser.add_argument('-i', '--ini', help='path to alternate ini file')
    parser.add_argument('-m', '--manager', help='The manager to connect to e.g. http://localhost:8138/')
    parser.add_argument('-d', '--agentdir', help='The directory the agent should use for files')
    parser.add_argument('-r', '--robot', help='The robot framework executable')
    parser.add_argument('-x', '--xmlmode', help='XML Mode, fall back to pasing the output.xml after each iteration', action='store_true')
    parser.add_argument('-a', '--agentname', help='Set agent name')
    parser.add_argument('-p', '--property', help='Add a custom property, if multiple properties are required use this argument for each property e.g. -p property1 -p "Property 2"', action='append')
    parser.add_argument('-c', '--create', help='ICON : Create application icon / shortcut')

    args = parser.parse_args()

    return args


def main():
    args = configuration()
    run_agent(args)

if __name__ == "__main__":
    main()
