"""Share one virtual layer per native anchor/offset across area-specific actors.

MesenCE keeps at most four sprites at a pixel, including invisible additions.
Separate blank area-specific layers can therefore clip a nearby visible actor.
"""
def coalesce_additions(header,rules):
    anchors={};aliases={};out=[];removed=0
    for line in header:
        if not line.startswith('<addition>'):
            out.append(line);continue
        a=line[10:].split(',');anchor=tuple(a[:4]+a[6:]);virtual=tuple(a[4:6])
        if anchor in anchors:
            aliases[virtual]=anchors[anchor];removed+=1
        else:
            anchors[anchor]=virtual;out.append(line)
    virtuals=set(anchors.values());active=[];fallback={}
    for line in rules:
        guard,body=line.split(']',1) if line.startswith('[') else ('',line)
        a=body[6:].split(',');kp=tuple(a[1:3])
        if kp in aliases:a[1:3]=aliases[kp]
        kp=tuple(a[1:3]);line=(guard+']' if guard else '')+'<tile>'+','.join(a)
        if not guard and kp in virtuals:
            if kp in fallback:assert fallback[kp]==line,'Conflicting virtual fallback'
            fallback[kp]=line
        else:active.append(line)
    assert virtuals==set(fallback)
    return out,active+list(fallback.values()),removed
