#!/usr/bin/env python3

import cgi
import cgitb
cgitb.enable()  # Enables error reporting in the browser

# Parse form data
form = cgi.FieldStorage()

# Get values
description = form.getvalue("description")
image = form['image'] if 'image' in form else None

# Print HTTP headers
print("Content-Type: text/html\n")

# Show submission back in browser
print("<html><body>")
print("<h1>Form Submission Received!</h1>")
print(f"<p>Description: {description}</p>")

if image:
    filename = image.filename
    filecontent = image.file.read()  # Reads uploaded file content
    with open(f"./uploads/{filename}", "wb") as f:
        f.write(filecontent)
    print(f"<p>Uploaded file saved as: {filename}</p>")
else:
    print("<p>No image uploaded.</p>")

print("</body></html>")