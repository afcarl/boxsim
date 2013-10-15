import re

def format_sensory_data(data):
    """Format raw list of data into list of relevant subgroups if necessary"""
    return data

    fmtdata = {}
    for key, value in data:
        match = re.search(r'(.*)_(.+)', key)
        if match is None:
            fmtdata[key] = value
        else:
            suffix = match.groups()[-1]
            if suffix in ['pos', 'vel', 'acc']:
                assert len(data) % 2 == 0
                fmtdata[key] = tuple((data[2*i], data[2*i+1]) for i in range(len(data)/2))
            else:
                fmtdata[key] = value

    return fmtdata
