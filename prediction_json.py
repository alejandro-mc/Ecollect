#makes a sample temp prediction json string that will be sent to the server
with open('weatherdata','r') as f:
     lines = f.readlines()



splitlines = map(lambda x: x.split(',') ,lines)
kjrb = filter(lambda x : x[1]=='KJRB',splitlines)
jsonlines = map(lambda x: "{{'datetime':'{0}','temp':{1} }}".format(x[0],x[2]),kjrb)


qstring = '['

for i in range(24):
    qstring += next(jsonlines) + ','



qstring = qstring[:-1]+']'


print (qstring)


