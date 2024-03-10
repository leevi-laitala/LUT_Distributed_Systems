from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

import xmlrpc.client
import xml.etree.ElementTree as ET
import requests
import datetime
import marshal
import base64

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
XMLDB = "db.xml"
TREE = ET.parse(XMLDB)
TREEROOT = TREE.getroot()

def addNewNote(topic: str, name: str, text: str) -> None:
    # Database data has the following format:
    # data
    # – topic
    #   – note          |
    #     – text        | Only construct these, and attach to given topic
    #     – timestamp   |

    note_n = ET.Element("note")
    note_n.set("name", name)

    text_n = ET.SubElement(note_n, "text")
    text_n.text = text

    time_n = ET.SubElement(note_n, "timestamp")
    time_n.text = datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")

    foundtopic = None

    # Find topic with given input
    for topic_i in TREEROOT.findall("topic"):
        if topic_i.get("name") == topic:
            foundtopic = topic_i
            break

    if foundtopic is None:
        return

    # If topic is found, append constructed note
    foundtopic.append(note_n)
    TREE.write(XMLDB) # Write changes to file

# Construct new topic 
def addNewTopic(topic: str) -> None:
    topic_n = ET.Element("topic")
    topic_n.set("name", topic)

    # Treeroot is "data" element, under which all topics are appended
    TREEROOT.append(topic_n)
    TREE.write(XMLDB) # Write changes to file

# Add new note
# Append under given topic, and construct topic if does not exist
def writeNote(topic: str, name: str, text: str) -> None:
    # Check if given topic exists
    for topic_i in TREEROOT.findall("topic"):
        if topic_i.get("name") == topic:
            # If found, add note to it
            addNewNote(topic, name, text)
            return

    # If not found, create new topic and append note to it
    addNewTopic(topic)
    addNewNote(topic, name, text)

def fetchNote(topic: str):
    foundtopic = None

    # Find topic from given topic name
    for topic_i in TREEROOT.findall("topic"):
        if topic_i.get("name") == topic:
            foundtopic = topic_i
            break

    if foundtopic is None:
        return

    ret = []        # List of lists, each index contain data of single note
    for note_i in foundtopic.findall("note"):
        # Fill array with arrays in a following format:
        # [ [ <timestamp>, <note>, <text> ], ... ]
        ret.append(["", "", ""])

        # Fill new empty array with data
        for element in note_i.iter():
            if element.tag == "timestamp":
                ret[-1][0] = element.text.strip()
            elif element.tag == "note":
                ret[-1][1] += element.get('name').strip()
            elif element.tag == "text":
                ret[-1][2] += element.text.strip()

    # Marshal array into binary data
    return marshal.dumps(ret)

# Doc https://www.mediawiki.org/wiki/API:Opensearch
def fetchWikipedia(searchterm: str):
    # Fetch 3 hits for given search term
    params = {
            "action": "opensearch",
            "namespace": "0",
            "search": searchterm,
            "limit": "3",
            "format": "json"
    }

    # Return search result as json, and None in case of error
    try:
        res = requests.get(WIKIPEDIA_API, params=params).json()
        return res
    except requests.RequestException:
        return None


if __name__ == "__main__":
    with SimpleXMLRPCServer(('localhost', 8000), allow_none=True) as server:
        server.register_introspection_functions()

        server.register_function(writeNote)
        server.register_function(fetchNote)
        server.register_function(fetchWikipedia)

        print("Control-c to quit")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            exit(0)

