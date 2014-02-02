##############################################

def mb_checksum(s):
    i = 1
    l = len(s)
    sout = ord(s[0])
	
    while (i<l):
	    sout ^= ord(s[i]) 
	    i+=1

    return chr(sout)

##############################################

tests = {
    'A': 0x41,
    'OK': 0x04,
    'Test': 0x36,
    'Hello, world': 0x2c,
    "OK @system::2014/01/16 11:44:59:: Don't kiss an elephant on the lips today.::@system::2014/01/16 11:45:02:: You will be run over by a truck.": 0x1a,
}

for s,csum in tests.iteritems():
    print "Checking {}".format(s)
    computed = mb_checksum(s)
    if chr(csum) == computed:
        print "Checksum for {} looks ok".format(s)
    else:
        print "Checksum for {} isn't correct: you got {} but it should have been {}".format(s, hex(ord(computed)), hex(csum))
    

