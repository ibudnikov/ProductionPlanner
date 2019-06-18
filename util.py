def sign(x):
    if x>0:
        return 1
    if x<0:
        return -1
    return 0

def setNodesLevels(schema):
    for x in schema.nodes:
        if x.type=="planet":
            x.level = 3
            x.sublevel = 1
        elif x.type=="item":
            if "Planetary" in x.item.categories:
                hasExp = False
                hasImp = False
                hasCons = False
                ins = [y for y,z in zip(schema.connectionsA, schema.connectionsB) if z==x.nodeId]
                outs = [z for y,z in zip(schema.connectionsA, schema.connectionsB) if y==x.nodeId]

                for y in ins:
                    proc = schema.getNodeById(y)
                    if proc.type == "process" and proc.subtype=="input" and proc.subtype2=="export":
                        hasExp = True
                        break
                for y in outs:
                    proc = schema.getNodeById(y)
                    if proc.type == "process" and proc.subtype=="output" and proc.subtype2=="import":
                        hasImp = True
                    if proc.type == "process" and proc.subtype=="construct":
                        hasCons = True
                    if hasImp and hasCons:
                        break
                if not hasCons and not hasExp:
                    x.level = 1
                    x.sublevel = 0
                elif hasImp:
                    x.level = 3
                    x.sublevel = 0
                else:
                    x.level = 5
                    x.sublevel = 1
            else:
                level, sublevel = getLevel(x)
                x.level = level
                x.sublevel = sublevel

    for x in schema.nodes:
        if x.type == "process":
            if x.subtype == "refine":
                x.level = 8
                x.sublevel = 2
            elif x.subtype == "input" and x.subtype2 == "export":
                plItem = [z for y,z in zip(schema.connectionsA, schema.connectionsB) if y==x.nodeId][0]
                plNode = schema.getNodeById(plItem)
                if plNode.level==3:
                    x.level = 3
                    x.sublevel = 0
                else:
                    x.level = 4
                    x.sublevel = 1
            elif x.subtype == "output" and x.subtype2 == "import":
                plItem = [y for y,z in zip(schema.connectionsA, schema.connectionsB) if z==x.nodeId][0]
                plNode = schema.getNodeById(plItem)
                if plNode.level==3:
                    x.level = 3
                    x.sublevel = 0
                else:
                    x.level = 2
                    x.sublevel = 0
            elif x.subtype == "input" or x.subtype=="construct":
                item = [z for y,z in zip(schema.connectionsA, schema.connectionsB) if y==x.nodeId][0]
                node = schema.getNodeById(item)
                x.level = node.level - 1
                x.sublevel = node.sublevel
            elif x.subtype == "output":
                item = [y for y,z in zip(schema.connectionsA, schema.connectionsB) if z==x.nodeId][0]
                node = schema.getNodeById(item)
                x.level = node.level + 1
                x.sublevel = node.sublevel
    for x in schema.nodes:
        if x.type == "question":
            itemOut = [z for y,z in zip(schema.connectionsA, schema.connectionsB) if y==x.nodeId]
            itemIn = [y for y,z in zip(schema.connectionsA, schema.connectionsB) if z==x.nodeId]
            if len(itemOut)==1:
                node = schema.getNodeById(itemOut[0])
                x.level = node.level - 1
                x.sublevel = node.sublevel
            elif len(itemIn)==1:
                node = schema.getNodeById(itemIn[0])
                x.level = node.level + 1
                x.sublevel = node.sublevel

def getLevel(itemNode):
    item = itemNode.item
    if item.categories[0]=="Manufacture&Research":
        if item.categories[1]=="Components":
            if item.categories[2]=="Fuel blocks":
                return (11,0)
            elif item.categories[2]=="Subsystem Components":
                return (15,1)
            elif item.categories[2]=="R.A.M.":
                return (15,2)
            else: return (-1,-1)
        elif item.categories[1]=="Materials":
            if item.categories[2]=="Planetary":
                return (1,0)
            elif item.categories[2]=="Raw materials":
                if item.categories[3]=="Standard ores":
                    if item.name.startswith("Compressed"):
                        return (7,2)
                    else: return (5,2)
                elif item.categories[3]=="Ice ores":
                    if item.name.startswith("Compressed"):
                        return (7,0)
                    else: return (5,0)
                else: return (-1,-1)
            elif item.categories[2]=="Reaction Materials":
                return (13,4)
            elif item.categories[2]=="Salvage materials":
                return (13,3)
            elif item.categories[2]=="Ice products":
                return (9,0)
            elif item.categories[2]=="Minerals":
                return (9,5)
            elif item.categories[2]=="Gas Clouds Materials":
                return (11,1)
            else: return (-1,-1)
        elif item.categories[1]=="Research Equipment":
            if item.categories[2]=="Ancient Relics":
                return (13,1)
            elif item.categories[2]=="Datacores":
                return (13,2)
            elif item.categories[2]=="Decryptors":
                return (13,0)
            else: return (-1,-1)
        else: return -1
    elif item.categories[0]=="Ship and module modifications":
        return (17,0)
    elif item.categories[0]=="Ships":
        return (17,1)
    elif item.categories[0]=="Bpc":
        return (15,0)
    else: return (-1,-1)
