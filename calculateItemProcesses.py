#!/usr/bin/env python3
import os
import sys
import json as js
import processes
import items

def main():
    itemRoot = items.init()
    procRoot = processes.init(itemRoot)
    processCatI(itemRoot)
    processCat(procRoot, itemRoot)
    itemRoot.save()

def processCatI(cat):
    for c in cat.subcategories:
        processCatI(c)
    for it in cat.items:
        processItem(it)

def processItem(item):
    item.inProcess = [500000]
    item.outProcess = [500003, 500004]
    if item.isRaw:
        item.inProcess.append(500001)
    if "Planetary" in item.categories:
        item.inProcess.append(500002)
        item.inProcess.append(500005)
        item.outProcess.append(500002)
        item.outProcess.append(500005)

def processCat(cat, itemRoot):
    for c in cat.subcategories:
        processCat(c, itemRoot)
    for pr in cat.processes:
        processPr(pr, itemRoot)

def processPr(proc, itemRoot):
    if proc.type=="construct":
        for m in proc.materials:
            it = itemRoot.find(m)
            it.outProcess.append(proc.processId)
        it = itemRoot.find(proc.item)
        it.inProcess.append(proc.processId)
    elif proc.type=="refine":
        for m in proc.items:
            it = itemRoot.find(m)
            it.inProcess.append(proc.processId)
        it = itemRoot.find(proc.material)
        it.outProcess.append(proc.processId)

main()
