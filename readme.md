multi-user text editor

host session: 
# mtedit -H [file_path]
connect to session:
# mtedit -C [conn_ip]

message format:
    [sender_username] -E [printed] [startpos] / user edited
    [sender_username] -M [newpos] / user position shifted
    [sender_username] -T [text] / file text
    [sender_username] -C [sender_username] / new user connected to session