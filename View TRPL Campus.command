#!/bin/bash
# Double-click to launch the TRPL campus viewer locally from this repo folder.
cd "$(dirname "$0")"
PORT=8734
echo "Serving TRPL Campus viewer at http://localhost:$PORT/"
echo "(POI authoring: open http://localhost:$PORT/?edit and right-click the model)"
( sleep 1; open "http://localhost:$PORT/index.html" ) &
python3 -m http.server $PORT
