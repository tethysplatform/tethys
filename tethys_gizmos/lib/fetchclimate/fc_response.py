#external imports
import datetime,requests,urllib

#------------------------------------------------------------------------------
#file global functions
#------------------------------------------------------------------------------
#this function determines the maximum depth of an array
def arrayDepth(l):
  if isinstance(l, list):
    return 1 + max(arrayDepth(item) for item in l)
  else:
    return 0
#------------------------------------------------------------------------------
#This class holds the data from the response from the Fetch Climate server
#------------------------------------------------------------------------------
class FCResponse:
  def __init__(self, request, resultUri):
    self.rq = request
    self.uri = resultUri
    self.values = []

  #POINT REARRANGE MEAN ARRAY FUNCTIONS
  #gets the point mean array if ARRAY DEPTH 3
  def rearrangeMeanDataMultYrDayPoint(self):
    arrayAvg = []
    for yearArray in self.values:
      for dayArray in yearArray:
        for dayData in dayArray:
          arrayAvg.append(dayData)
    return arrayAvg    

  #gets the point mean array if ARRAY DEPTH 4
  def rearrangeMeanDataMultYrDayHourPoint(self):
    arrayAvg = []
    for yearArray in self.values:
      for dayArray in yearArray:
        for hourArray in dayArray:
          for hourData in hourArray:
            arrayAvg.append(hourData)
    return arrayAvg    

  #GRID MEAN FUNCTIONS
  #gets the mean of grid if ARRAY DEPTH 2
  def findDataMeanAvgGrid(self):
    numValuesInSum = 0
    arraySum = [0 for i in range(len(self.values[0]))]
    for array in self.values:
      for i in range(len(array)):
        if array[i]:
          arraySum[i] += array[i]
        else: #add the average if missing data
          arraySum[i] += arraySum[i]/(numValuesInSum+1)
      numValuesInSum += 1
    return [x/float(numValuesInSum) for x in arraySum]

  #gets the mean of grid if ARRAY DEPTH 3
  def findDataMeanMultYrGrid(self):
    numValuesInSum = 0
    arraySum = [0 for i in range(len(self.values[0][0]))]
    for array in self.values:
      for yearArray in array:
        for i in range(len(yearArray)):
          if yearArray[i]:
            arraySum[i] += yearArray[i]
          else: #add the average if missing data
            arraySum[i] += arraySum[i]/(numValuesInSum+1)
        numValuesInSum += 1
    return [x/float(numValuesInSum) for x in arraySum]

  #gets the mean of grid if ARRAY DEPTH 4
  def findDataMeanMultYrDayGrid(self):
    dayLen = len(self.values[0][0][0])
    arraySum = [0 for i in range(dayLen*len(self.values[0][0]))]
    numValuesInSum = 0
    for array in self.values:
      for yearArray in array:
        for yearIndex,dayArray in enumerate(yearArray):
          for i in range(dayLen):
            if dayArray[i]:
              arraySum[yearIndex*dayLen+i] += dayArray[i]
            else: #add the average if missing data
              arraySum[yearIndex*dayLen+i] += arraySum[yearIndex*dayLen+i]/float(numValuesInSum+1)
        numValuesInSum += 1
    return [x/float(numValuesInSum) for x in arraySum]

  #gets the mean of grid if ARRAY DEPTH 5
  def findDataMeanMultYrDayHourGrid(self):
    numValuesInSum = 0
    dayLen = len(self.values[0][0][0])
    hourLen = len(self.values[0][0][0][0])
    arraySum = [0 for i in range(len(self.values[0][0])*dayLen*hourLen)]
    for array in self.values:
      for yearArray in array:
        for yearIndex,dayArray in enumerate(yearArray):
          for dayIndex,hourArray in enumerate(dayArray):
            #if any(x is None for x in hourArray):
              #return None
            for i in range(hourLen):
              if hourArray[i]:
                arraySum[(yearIndex*dayLen+dayIndex)*hourLen+i] += hourArray[i]
              else: #add the average if missing data
                arraySum[(yearIndex*dayLen+dayIndex)*hourLen+i] += \
                  arraySum[(yearIndex*dayLen+dayIndex)*hourLen+i]/float(numValuesInSum+1)
        numValuesInSum += 1
    return [x/float(numValuesInSum) for x in arraySum]    

  #main function to find data mean
  def findDataMean(self, isPoint=False):
    if any(x is None for x in self.values):
      return None
    depth = arrayDepth(self.values)
    #IF IT IS A POINT
    if len(self.values) == 1:
      if depth == 1:
        #ARRAY DEPTH 1
        #if there is avg of years, days, hours of values
        return self.values
      if depth == 2:
        #ARRAY DEPTH 2
        #if there are individual years
        #if there is one year, individual days
        #if there is one year, one day, individual hours
        return self.values[0]
      if depth == 3:
        #ARRAY DEPTH 3
        #if there are individual years and days 
        #if there is one year, individual days, individual hours 
        return self.rearrangeMeanDataMultYrDayPoint()
      if depth == 4:
        #ARRAY DEPTH 4
        #if there are individual days, years, and hours
        return self.rearrangeMeanDataMultYrDayHourPoint()
      
    #IF IT IS A GRID
    if depth == 3:
      #ARRAY DEPTH 3
      #if there are individual years
      #if there is one year, individual days
      #if there is one year, one day, individual hours
      return self.findDataMeanMultYrGrid()
    if depth == 4:
      #ARRAY DEPTH 4
      #if there are individual years and days 
      #if there is one year, individual days, individual hours 
      return self.findDataMeanMultYrDayGrid()
    if depth == 5:
      #ARRAY DEPTH 5
      #if there are individual days, years, and hours
      return self.findDataMeanMultYrDayHourGrid()
    #GRID - ARRAY DEPTH 2
    #if there is avg of years, days, hours of values
    return self.findDataMeanAvgGrid()

  def getData(self, names=None):
    if (not names):
      #if (this.request.dataSources.length == 1):
      names = ["values", "sd"]
      #else:
      #names = ["values", "provenance", "sd"]

    print str(datetime.datetime.now()) + ": Requesting " + str(names) + " of " + self.uri

    variables = "";
    for i in range(0,len(names)):
      if(len(variables) > 0):
        variables = variables + ",";
      variables += names[i]

    headers = {'data-type':'json'}
    r = requests.get(self.rq.serviceUrl + "/jsproxy/data?uri=" + \
      urllib.quote(self.uri.encode("utf-8")) + "&variables=" + \
      urllib.quote(variables.encode("utf-8")), 
      headers=headers, 
      timeout=self.rq.timeout)
    data = []
    if r.status_code == requests.codes.ok:
      data = r.json()
      self.values = data["values"]
    return self.values

