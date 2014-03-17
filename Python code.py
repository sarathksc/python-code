import sys
import re
import nltk
import csv
import replacers
from geopy import geocoders
from suds.client import Client
from collections import namedtuple
from decimal import *
import esri_geocode_su
import re
import difflib
import enchant
import utlisForTextProcesss

class LocationFinder:
        len=0
        replacerState=None
        replacerStreetDirection=None
        replacerStreetSuffix=None
        replacerSecUnitRequired=None
        replacerSecUnitOptional=None
        replacerOtherAbbreviations=None
        stateList=[]
        aptList=[]
        streetList=[]
        foundZip=[]
        foundState=[]
        foundStreet=[]
        foundPOBox=[]
        foundApt=[]
        foundMultipleMatches=[]
        foundTokens=[]
        
        def __init__(self):
                self.replacerState = replacers.CsvWordReplacer('us-state-abreviations.csv')
                self.replacerStreetDirection = replacers.CsvWordReplacer('street-direction-abbreviations.csv')
                self.replacerStreetSuffix = replacers.CsvWordReplacer('street-suffix-abbreviations.csv')
                self.replacerSecUnitRequired = replacers.CsvWordReplacer('secondary-units-abbreviations-required-follow-number.csv')
                self.replacerSecUnitOptional = replacers.CsvWordReplacer('secondary-units-abbreviations-optional-follow-number.csv')
                self.replacerOtherAbbreviations = replacers.CsvWordReplacer('other-address-abbreviations.csv')
                #read and store statelist(2 letter) from csv
                #read and store streetlist from csv
                #read and store apartmentlist from csv

        def format_token(self,token):
                #i have added entries offcial name, self to be able to handle the case where the record use offical name
                if token !=  self.replacerStreetDirection.replace(token):
                    if self.replacerStreetDirection.replace(token) =="self":
                        return token
                    else:
                        return self.replacerStreetDirection.replace(token)
                elif token !=  self.replacerStreetSuffix.replace(token):
                    if self.replacerStreetSuffix.replace(token) =="self":
                        return token
                    else:
                        return self.replacerStreetSuffix.replace(token)
                elif token !=  self.replacerState.replace(token):
                    if self.replacerState.replace(token) =="self":
                        return token
                    else:
                        return self.replacerState.replace(token)
                elif token !=  self.replacerSecUnitRequired.replace(token):
                    if self.replacerSecUnitRequired.replace(token) =="self":
                        return token
                    else:
                       return self.replacerSecUnitRequired.replace(token)
                elif token !=  self.replacerSecUnitOptional.replace(token):
                    if self.replacerSecUnitOptional.replace(token) =="self":
                        return token
                    else:
                        return self.replacerSecUnitOptional.replace(token)
                elif token !=  self.replacerOtherAbbreviations.replace(token):
                    return self.replacerOtherAbbreviations.replace(token)
                else:
                     return token
            

        def identifyAddress(token,arrayIndex):
                
                index=testZipCode(token)
                baseIndex=index;
                if(index>0):
                        baseIndex=index
                        addToZipCode(token,index,arrayIndex)
                index=testStateBeforeIndex(token,index,arrayIndex)
                if(index>0):
                        if(baseIndex<0):
                                baseIndex=index
                        addToStateAddress(token,index,arrayIndex)
                index=testApartmentBeforeIndex(token,index,arrayIndex)
                if(index>0):
                        if(baseIndex<0):
                                baseIndex=index
                        addToApartment(token,index,arrayIndex)
                index=testPOBoxBeforeIndex(token,index,arrayIndex)
                if(index>0):
                        if(baseIndex<0):
                                baseIndex=index
                        addToPOBox(token,index,arrayIndex)
                index=testStreetName(token,index,arrayIndex)
                if(index>0):
                        if(baseIndex<0):
                                baseIndex=index
                        addToStreetName(token,index,arrayIndex)
                        
                if(baseIndex>0&&baseIndex<index):
                        foundZipCode.insert(arrayIndex,token[index,baseIndex])         
                         
                #check for zip code and directions from database(regex)
                #return the index of zipcode if found and change len to Length of zipcode 
                #
                #else return -1
        def testZipCode(token):
                global len
                zippattern= r'.*(\d{5}(\-\d{4})?)$'
                m = re.search(zippattern, item1)
                
                if(m is not None):
                        len=token.len()
                        return string.find(token,m)
                return -1        
                

                #check for state names from database(regex)
                #return the index of state name if found and change len to Length of State Name 
                #else return -1
        def testStateBeforeIndex(token,index,arrayIndex):
                global len
                len=2
                for state in stateList
                      if(string.find(token,state,0,index)>0):  
                        return string.find(token,state,0,index)
                return -1
                
                #check for apartment name from database(regex)
                #return the index of apartment name if found and change len to Length of Apartment
                #else return -1
        def testApartmentBeforeIndex(token,index,arrayIndex):
                global len
                
                for apt in aptList
                      if(string.find(token,apt,0,index)>0):  
                        index1=string.find(token,apt,0,index)
                        index2=string.find(token," ",0,index1-1)
                        len=index1-index2
                        return index2

                        
                return -1

                #check for PO Box from database(regex)
                #return the index of PO Box if found and change len to Length of POBox
                #else return -1
        def testPOBoxBeforeIndex(token,index,arrayIndex):
                global len
                
                if(string.find(token,"PO Box",0,index)>0):  
                        index1=string.find(token,"PO Box",0,index)
                        index2=string.find(token," ",index1+1)
                        len=index2-index1
                        return index2
                        
                return -1

                #check for street names and directions from database(regex)
                #return the index of street name if found and change len to Length of StreetName
                #else return -1

        def testStreetName(token,index,arrayIndex):
                global len
                for street in streetList
                      if(string.find(token,street,0,index)>0):  
                        index1=string.find(token,street,0,index)
                        index2=string.find(token," ",0,index1-1)
                        len=index1-index2
                        return index2

        def addToStateAddress(token,index,arrayIndex):
                global len
                foundStates.insert(arrayIndex,token[index-len,len])
                #streetName.insert(arrayIndex,token[index-len,len]
                
        def addToApartment(token,index,arrayIndex):
                global len
                foundApartments.insert(arrayIndex,token[index-len,len])
                #apartment.insert(arrayIndex,token[index-len,len]
                
        def addToPOBox(token,index,arrayIndex):
                global len
                foundPOBox.insert(arrayIndex,token[index-len,len])
                #pobox.insert(arrayIndex,token[index-len,len]
                
        def addToStreetName(token,index,arrayIndex)	:
                global len
                foundStreets.insert(arrayIndex,token[index-len,len])
                #streetName.insert(arrayIndex,token[index-len,len]
                        
        def addToZipCode(token,index,arrayIndex):
                global len
                foundZipCode.insert(arrayIndex,token[index-len,len])
                if(foundZipCode[arrayIndex]!=None):
                        #print line
                        foundMultipleMatches.insert(arrayIndex,token)
                        
                #zipcode.insert(arrayIndex,token[index-len,len]

