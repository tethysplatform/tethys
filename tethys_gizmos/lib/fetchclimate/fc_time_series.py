import datetime, time

#------------------------------------------------------------------------------
#This class contains and manages the Fetch Climate time series data
#------------------------------------------------------------------------------
class FCTimeSeries:
  def __init__(self,temporalDomain,averageData):
    self.temporalDomain = temporalDomain
    self.averageData = averageData
    self.combinedData = [] #the average data and the time data aligned
    self.initTimeSeriesData() #combines the data
    self.combinedDataMiliSec = [] #converts time to miliseconds
    self.plots = None

  #This converts datetime time series data to miliseconds
  def timeSeriesDateToMilisecond(self):
    #added the timeshift because it seemed to be off by 7 hours?
    if self.temporalDomain.hourCellMode: 
      dt = datetime.timedelta(hours=-7)
    else:
      dt = datetime.timedelta(hours=1)
    self.combinedDataMiliSec = self.combinedData
    for point in self.combinedDataMiliSec:
      shiftedTime = point[0]+dt
      point[0] = time.mktime(shiftedTime.timetuple())*1000
    return self.combinedDataMiliSec

  #This returns if the year is a leap year
  def isLeapYear(self,year):
    return year > 1582 and (0 == year % 400 or (0 == year % 4 and not 0 == year % 100)) 

  #This function returns the number of month and day from the data
  def getNumericMonthDay(self,yearNum, dayNum):
    daysInFeb = 29 if self.isLeapYear(yearNum) else 28
    if dayNum <= 31:
      return [1,dayNum]
    elif dayNum <= (31+daysInFeb):
      return [2, dayNum - 31]
    elif dayNum <= (2*31+daysInFeb):
      return [3, dayNum - (31+daysInFeb)]
    elif dayNum <= (2*31+30+daysInFeb):
      return [4, dayNum - (2*31+daysInFeb)]
    elif dayNum <= (3*31+30+daysInFeb):
      return [5, dayNum - (2*31+30+daysInFeb)]
    elif dayNum <= (3*31+2*30+daysInFeb):
      return [6, dayNum - (3*31+30+daysInFeb)]
    elif dayNum <= (4*31+2*30+daysInFeb):
      return [7, dayNum - (3*31+2*30+daysInFeb)]
    elif dayNum <= (5*31+2*30+daysInFeb):
      return [8, dayNum - (4*31+2*30+daysInFeb)]
    elif dayNum <= (5*31+3*30+daysInFeb):
      return [9, dayNum - (5*31+2*30+daysInFeb)]
    elif dayNum <= (6*31+3*30+daysInFeb):
      return [10, dayNum - (5*31+3*30+daysInFeb)]
    elif dayNum <= (6*31+4*30+daysInFeb):
      return [11, dayNum - (6*31+3*30+daysInFeb)]
    elif dayNum <= (7*31+4*30+daysInFeb):
      return [12, dayNum - (6*31+4*30+daysInFeb)]

  #This function gets time series data size 
  def timeSeriesDataSize(self):
    #find out if it is the hour cell mode
    lenHours = len(self.temporalDomain.hours) if not self.temporalDomain.hourCellMode else 1

    #find out if it is the day cell mode
    lenDays = len(self.temporalDomain.days) if not self.temporalDomain.dayCellMode else 1

    #find out if it is year cell mode    
    lenYears = len(self.temporalDomain.years) if not self.temporalDomain.yearCellMode else 1

    return lenHours*lenDays*lenYears

  #This function initializes time series data
  def initTimeSeriesData(self):
    self.combinedData = []
    #find out if it is the hour cell mode
    hours = [0] #initialize to hr 0
    if not self.temporalDomain.hourCellMode:
      hours = self.temporalDomain.hours

    #find out if it is the day cell mode
    days = [1] #initialize to january 1st
    if not self.temporalDomain.dayCellMode:
      days = self.temporalDomain.days

    #find out if it is year cell mode
    if not self.temporalDomain.yearCellMode:
      years = self.temporalDomain.years  
      tmpData = self.averageData if self.averageData else [0 for i in range(len(years)*len(days)*len(hours))]
    else:
      years = [self.temporalDomain.years[0],self.temporalDomain.years[len(self.temporalDomain.years)-1]]

      if isinstance(self.averageData, list):  #if it is a point    
        dataValue = self.averageData[0] if self.averageData else 0
      else: #if it is a grid
        dataValue = self.averageData if self.averageData else 0
      tmpData = [dataValue for i in range(len(years)*len(days)*len(hours))]

    #combine the data with the time
    dayLen = len(days)
    hourLen = len(hours)
    for i in range(len(years)):
      for j in range(dayLen):
        for k in range(hourLen):
          monthDay = self.getNumericMonthDay(years[i], days[j])
          self.combinedData.append([datetime.datetime(years[i],monthDay[0],monthDay[1],hours[k]),tmpData[i*dayLen+j*hourLen+k]])
  
  #------------------------------------------------------------------------------
  #This function creates a time series plot
  #------------------------------------------------------------------------------
  def getTimeSeriesPlot(self, variableName, gridName, variableDescription, response = None, hashString=None):
    #set up plot parameters
    timeseries_plot_object = {
        'chart': {
            'type': 'area',
            'zoomType': 'x'
        },
        'title': {
            'text': gridName
        },
        'xAxis': {
            'maxZoom': 24 * 3600000, # 1 day in milliseconds
            'type': 'datetime'
        },
        'yAxis': {
            'title': {
                'text': variableDescription
            },
            'min': 0
        },
        'series': [{
            'name': variableDescription,
            'data': self.combinedData
        }],
        'custom':{
          'grid': gridName,
          'variable': variableName,
          'hash': hashString,
          'responseUri': response.uri if response else None
        }
    }

    return {'highcharts_object': timeseries_plot_object, 'width': '500px', 'height': '500px'}                  

