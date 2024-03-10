import xmlrpc.client
import marshal

CONNECTION = xmlrpc.client.ServerProxy('http://localhost:8000')

def prompt(prompt: str) -> str:
    return input(f"\n{prompt}\n : ")

# "writeNote" request creates topic if one does not exist
# then appends to existing topic the given note and text.
# Server adds timestamp to the note
def addNote():
    topic = prompt("Topic name")
    name = prompt("Note name")
    text = prompt("Note")
    
    # Any field cannot be empty
    if len(topic) and len(name) and len(text):
        try:
            # Attempt "writeNote" server request with given input
            ret = CONNECTION.writeNote(topic, name, text)

        except ConnectionRefusedError:
            ret = "ERR : Cannot connect to server"
    else:
        # Construct error with info on missing fields
        ret = "ERR : Invalid input"
        ret += ", missing Topic"        if not len(topic) else ""
        ret += ", missing Note name"    if not len(name) else ""
        ret += ", missing Note"         if not len(text) else ""
    
    return ret

# "fetchNote" function returns a formatted string of the topics
def getTopic():
    topic = prompt("Topic name")

    if not len(topic):
        return "ERR : Invalid input"
    
    try:
        # Attempt "fetchNote" server request with given topic
        binarydata = CONNECTION.fetchNote(topic)

    except ConnectionRefusedError:
        return "ERR : Cannot connect to server"
    
    if binarydata is None:
        return "ERR : Topic not found"

    # Unmarshal binary data to list object
    return prettifyNotes(marshal.loads(binarydata.data))

# Print list object
def prettifyNotes(notes) -> str:
    # getTopic can return error as a string, or a list of notes on success
    if not isinstance(notes, list):
        return notes # Passthrough error string if such is given

    # Note is format of [ [ <timestamp>, <note>, <text> ], ... ]
    ret = "" # Append all notes into single string

    for note in notes:
        ret += f"\n{note[0]}\n\n\t:: {note[1]}\n\n\t{note[2]}\n"
    
    return ret

def fetchWikipedia() -> str:
    searchterm = prompt("Searchterm")

    if not len(searchterm):
        return "ERR : Invalid input"

    try:
        data = CONNECTION.fetchWikipedia(searchterm)

    except ConnectionRefusedError:
        return "ERR : Cannot connect to server"
    
    if data is None:
        return f"ERR : Couldn't fetch '{searchterm}'"

    ret = ""
    for i in range(len(data[1])):
        ret += f"{data[1][i]} :: {data[3][i]}\n"

    return ret


if __name__ == "__main__":
    running = True

    while running:
        cmd = prompt("1) Add note\n2) Get topic\n3) Search wikipedia\n4) End")
        ret = ""
        
        if cmd in ("1", "add"):
            ret = addNote()

        elif cmd in ("2", "get"):
            ret = getTopic()

        elif cmd in ("3", "wiki", "search", "wikipedia"):
            ret = fetchWikipedia()

        elif cmd in ("4", "exit", "quit"):
            running = False

        else:
            ret = "ERR : Invalid command"
        
        print(f"\n{ret}")

