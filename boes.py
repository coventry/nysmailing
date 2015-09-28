import  re

# Board of elections contact info, sorted in the same order as the values used for COUNTYCODE.
f = open('boes-sorted.txt')

boes = []

for line in f:
    county = line.strip()
    entry = [county]
    while True:
        line = f.next().strip()
        if not line:
            break
        entry.append(line)
    assert re.match('\(\d{3}\) \d{3}-\d{4}', entry[-1]), 'Last line is phone number'
    addr = {}
    addr['fname'] = '%s County Board of Elections' % county
    addr['lname'] = ''
    addr['state'] = 'NY'
    addr['phone'] = entry[-1]
    city, statezip = entry[-2].split(',')
    addr['city'] =  city
    state, zip_ = statezip.split()
    assert state == 'NY'
    assert re.match('\d{5}', zip_)
    addr['zip'] = zip_
    addr['street'] = '<br/>\n'.join(entry[1:-2])
    boes.append(addr)
    
