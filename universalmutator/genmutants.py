import sys
import shutil
import mutator

import python_handler
import python3_handler
import c_handler
import cpp_handler
import java_handler
import swift_handler
import subprocess

import os

def nullHandler(tmpMutantName, mutant, sourceFile, uniqueMutants):
    return "VALID"

def cmdHandler(tmpMutantName, mutant, sourceFile, uniqueMutants):
    global cmd

    with open("mutant_output",'w') as file:
        r = subprocess.call([cmd.replace("MUTANT",tmpMutantName)],shell=True,stderr=file,stdout=file)
    if r == 0:
        return "VALID"
    else:
        return "INVALID"

def main():
    global cmd

    try:
        import custom_handler
    except:
        pass

    args = sys.argv
    
    if "--help" in args:
        print "USAGE: mutate <file> [--noCheck] [<language>] [<rule1> <rule2>...] [--cmd <command string>]"
        print "       --noCheck: skips compilation/comparison and just generates mutant files"
        print "       --cmd executes command string, replacing MUTANT with the mutant name, and uses return code"
        print "             to determine mutant validity"
        sys.exit(0)

    noCheck = False
    if "--noCheck" in args:
        noCheck = True
        args.remove("--noCheck")

    cmd = None
    cmdpos = args.index("--cmd")
    if cmdpos != -1:
        cmd = args[cmdpos+1]
        args.remove("--cmd")
        args.remove(cmd)

    handlers = {"python": python_handler,
                "python3": python3_handler,
                "c": c_handler,
                "c++": cpp_handler,
                "cpp": cpp_handler,            
                "java": java_handler,
                "swift": swift_handler}

    languages = {".c": "c",
                 ".cpp": "cpp",
                 ".c++": "cpp",             
                 ".py": "python",
                 ".java": "java",
                 ".swift": "swift"}    

    cLikeLanguages = ["c","java","swift", "cpp", "c++"]

    try:
        handlers["custom"] == "custom_handler"
    except:
        pass

    sourceFile = args[1]
    ending = "." + sourceFile.split(".")[-1]

    if len(args) < 3:
        language = languages[ending]
        otherRules = []
    else:
        language = args[2]
        otherRules = args[3:]

    base = ".".join((sourceFile.split(".")[:-1]))

    if language in cLikeLanguages:
        otherRules.append("c_like.rules")

    rules = ["universal.rules",language + ".rules"] + otherRules

    source = []

    with open(sourceFile,'r') as file:
        for l in file:
            source.append(l)

    mutants = mutator.mutants(source, rules = rules)

    print len(mutants),"MUTANTS GENERATED BY RULES"

    validMutants = []
    invalidMutants = []
    redundantMutants = []
    uniqueMutants = {}

    if not noCheck:
        if cmd != None:
            handler = cmdHandler
        else:
            handler = handlers[language].handler
    else:
        handler = nullHandler

    mutantNo = 0
    for mutant in mutants:
        tmpMutantName = "tmp_mutant" + ending
        print "PROCESSING MUTANT:",str(mutant[0])+":",source[mutant[0]-1][:-1]," ==> ",mutant[1][:-1],"...",
        mutator.makeMutant(source, mutant, tmpMutantName)
        mutantResult = handler(tmpMutantName, mutant, sourceFile, uniqueMutants)
        print mutantResult,
        mutantName = base + ".mutant." + str(mutantNo) + ending
        if mutantResult == "VALID":
            print "[written to",mutantName+"]",
            shutil.copy(tmpMutantName, mutantName)
            validMutants.append(mutant)
            mutantNo += 1
        elif mutantResult == "INVALID":
            invalidMutants.append(mutant)
        elif mutantResult == "REDUNDANT":
            redundantMutants.append(mutant)
        print

    print len(validMutants),"VALID MUTANTS"
    print len(invalidMutants),"INVALID MUTANTS"
    print len(redundantMutants),"REDUNDANT MUTANTS"

if __name__ == '__main__':
    main()

