import requests
import json
import time
import urllib.request, urllib.parse, urllib.error
from collections import defaultdict

class GetEarthquakeInfo:
    def __init__(self,startDate, endDate):
        # Looks like: https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2014-01-01&endtime=2014-01-02
        earthquakeURL =  "http://earthquake.usgs.gov/fdsnws/event/1/query?"
        paramD = dict()
        paramD["format"] = "geojson"     # the format the data will be in
        paramD["starttime"] = startDate  # the minimum date/time that might be retrieved
        paramD["endtime"] = endDate      # the maximum date/time that might be retrieved
        ## Note that the next two params might eliminate any data coming back if the magnitude isn't high enough
        # paramD["minmag"] = 6           # the smallest earthquake magnitude to return
        # paramD["limit"] = 5            # the maximum number of earthquakes to return
        params = urllib.parse.urlencode(paramD)
        print('Retrieving', earthquakeURL+params)
        self.usgsEarthquakeApi = requests.get(earthquakeURL+params) 
        time.sleep(1)

    def getEarthquakeData(self, theJSON):
        r=self.usgsEarthquakeApi
        if r.status_code != 200:
            print ("Problem connecting with USGS Earthquake API at https://earthquake.usgs.gov/earthquakes.")
            exit
        earthquakeList = []
        try:
            theJSON = json.loads(r.content)
        except:
            theJSON = None
                
        if not theJSON or 'type' not in theJSON :
            print('==== Failure To Retrieve ====')
            print(r.content)

        reportCount=theJSON["metadata"]["count"] #using this as the row count
        propertyList=["mag", "place", "felt", "tsunami", "sig", "type", "title"] #A list of the properties I want
        for i in theJSON["features"]:
            propertyListCtr=0
            row = []
            for aRow in i["properties"]: #aRow is the actual property name
                tempProp=propertyList[propertyListCtr]
                tempVal=i["properties"][tempProp]
                if aRow == tempProp:
                    row.append(tempVal)
                    propertyListCtr+=1
            earthquakeList.append(row) #appending the entire row of data once to the list
        return earthquakeList
    
    def averageMagnitude(self, data, sizeOfReturnedData):
        totalMag=float(0)
        for i in range(sizeOfReturnedData):
            totalMag=totalMag+float(data[i][0])
        averageMag=totalMag/sizeOfReturnedData
        return averageMag
    
    def anyTsunami(self, data, sizeOfReturnedData):
        totalTsunamiCount=int(0)
        for i in range(sizeOfReturnedData):
            if data[i][3] != 0:
                totalTsunamiCount=totalTsunamiCount+data[i][3]
        return totalTsunamiCount
    
    def countryCount(self, data, sizeOfReturnedData):
        countryList = defaultdict(int) # Initialize dictionary
        for i in range(sizeOfReturnedData):
            # placeDescription='90 km SSW of Bengkulu, Indonesia'
            placeDescription=data[i][1]
            place=placeDescription.split(",")
            placeListSize=len(place)
            name=str(place[placeListSize-1])
            countryName=name.strip()
            countryList[countryName] += 1
        return countryList
    
    def countryWithMostEarthquakes(self, countryData):
        max_val = max(countryData.values())
        res = list(filter(lambda x: countryData[x] == max_val, countryData))
        return res[0]

#Calling a class to parse thru the API json and creates a text file of the info for the schedule
startDate='2024-06-01'
endDate='2024-06-02'
a=GetEarthquakeInfo(startDate, endDate)
eqData=a.getEarthquakeData(a) #Data brought back: "mag", "place", "felt", "tsunami", "sig", "type", "title"
try:
    sizeOfReturnedData=len(eqData)
except:
    print("The data list is empty.")
    exit
averageMagnitudeValue=a.averageMagnitude(eqData, sizeOfReturnedData) #Typical Values [-1.0, 10.0]
print("The average magnitude",format(averageMagnitudeValue, '.2f'))
tsunamiCnt=a.anyTsunami(eqData, sizeOfReturnedData)
print("The number of Tsunami's triggered during this timeframe is:",tsunamiCnt)
countryList=a.countryCount(eqData, sizeOfReturnedData) # Parse the countries and get a count per country
maxEarthquakes=a.countryWithMostEarthquakes(countryList)
print("Country(s) with maximum earthquakes for this timeframe is(are): " + str(maxEarthquakes))
# Maybe add a graph of the data?
time.sleep(1)
