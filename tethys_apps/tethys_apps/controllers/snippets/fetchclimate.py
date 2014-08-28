#external imports
from pylons.decorators import jsonify
import inspect,requests,json 

#ckan imports
import ckan.plugins as p
from ckan.lib.base import BaseController

#imports from this app
from ...lib.FetchClimate.FCGrid import FCGrid 
from ...lib.FetchClimate.FCResponse import FCResponse 
from ...lib.FetchClimate.FCRequest import FCRequest 
from ...lib.FetchClimate.FCTimeSeries import FCTimeSeries 
from ...lib.FetchClimate.FCTemporalDomain import FCTemporalDomain 

#------------------------------------------------------------------------------
#file global functions
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#This class contains the configuration for FetchClimate variables
#------------------------------------------------------------------------------
class FCConfiguration:
  def __init__(self, options):
    self.config = []
    self.timeout = 180000 # 3 minute timeout for configuration request
    self.options = options if options else {}
    self.serviceUrl = options['serviceUrl'] if 'serviceUrl' in options else ""
    self.getConfiguration()

  # Returns FetchClimate configuration for given timestamp or latest configuration
  # if timestamp is not specified
  def getConfiguration(self):
    timestamp = "/api/configuration?timestamp=" + self.options['timestamp'] if 'timestamp' in self.options else "/api/configuration"
    headers={'data-type':'json'}
    r = requests.get(self.serviceUrl + timestamp, headers=headers, timeout=self.timeout)
    if r.status_code == requests.codes.ok: #requests.codes.ok is 200
      self.config = r.json()
    else:
      self.config = "Error: " + str(r.status_code)

  def getDataSourceByID(self, source_id):
    dataSource = self.config['DataSources']
    for source in dataSource:
      if source['ID'] == int(source_id):
        return source['Name']
    return None

  def getDataSources(self, variable_src_ids):
    if(len(variable_src_ids)>0):
      dataSources = []
      for i in range(0,len(variable_src_ids)):
        dataSources.append(self.getDataSourceByID(variable_src_ids[i]))
    else:
      dataSources = None
    return dataSources

  def getDataDescriptionByName(self, name):
    environmentalVariables = self.config['EnvironmentalVariables']
    for source in environmentalVariables:
      if source['Name'] == name:
        return source['Description']
    return None

  def getDataUnitsbyName(self, name):
    environmentalVariables = self.config['EnvironmentalVariables']
    for source in environmentalVariables:
      if source['Name'] == name:
        return source['Units']
    return None

#------------------------------------------------------------------------------
#This class is the main class for the Fetch Climate controller
#------------------------------------------------------------------------------
class FetchClimateSnippetController(BaseController):
  """
  Docs
  """
  def __init__(self):
    self.timeout = 180000
    self.plots = [] #the plots of the data
    self.data = {} #the grid data
    self.means = {} #the means of the data
    self.temporalDomain = None

  def initRequest(self):
    variable_src_ids = [int(src_id) for src_id in self.variable_data['sources']] if isinstance(self.variable_data['sources'],list) else [] 
    return FCRequest({"spatial": self.grid, "temporal": self.temporalDomain,
        "variable": self.variable_data['name'], "dataSources": self.FCConfig.getDataSources(variable_src_ids)})

  #this function initializes request process based on grid and variable
  def initDataRequest(self):
    print "Request Ready for grid: " +self.grid.name+ ", variable: " + self.variable_data['name'] + ". Posting!"
    request = self.initRequest()
    return request.doPost()

  #this function gets the grid data and finds the data means
  def getDataFromResponse(self, response):
    success = False
    if response:
      self.data[self.variable_data['name']] = {}
      self.data[self.variable_data['name']][self.grid.name] = response.getData()
      self.means[self.variable_data['name']] = {}
      self.means[self.variable_data['name']][self.grid.name] = response.findDataMean()
      success = True
    else:
      self.means[self.variable_data['name']] = {}
      self.means[self.variable_data['name']][self.grid.name] = None
    return {"data": self.means[self.variable_data['name']][self.grid.name],
            "success": success}

  #loads data into the class from the post data
  def initFromPost(self, post_info):
    #update service url
    self.serviceUrl =  post_info['serviceUrl'] if len(post_info['serviceUrl'])>0 else "http://fetchclimate2.cloudapp.net" 
    self.FCConfig = FCConfiguration({'serviceUrl':self.serviceUrl})
    #initialize temporal domain
    time_data = json.loads(post_info['time'])
    self.temporalDomain = FCTemporalDomain(time_data['years'],time_data['yc'],
          time_data['days'],time_data['dc'],time_data['hours'],time_data['hc'])
    #initialize grids
    grid_data = json.loads(post_info['grid'])
    if grid_data['gridType']=='CellGrid':
      grid_points = grid_data['gridData']['boundingBox']
      grid_resolution = grid_data['gridData']['gridResolution']
      self.grid = FCGrid('CellGrid',grid_points[0],grid_points[1],grid_resolution[0],
          grid_points[2],grid_points[3],grid_resolution[1],grid_data['gridData']['title'])
    elif grid_data['gridType']=='Points':      
      grid_points = grid_data['gridData']['location']
      self.grid = FCGrid('Points',[grid_points[0]],[grid_points[1]],None,
          None,None,None,grid_data['gridData']['title'])
    #get variable data
    self.variable_data = json.loads(post_info['variable'])

  #this handles the request for data for a single plot
  @jsonify
  def dataRequestSingle(self):
    # Tools
    t = p.toolkit

    post_info =  t.request.POST
    #init class data from post
    self.initFromPost(post_info)
    #initialize request
    response = self.initDataRequest()
    #get data from response
    data = self.getDataFromResponse(response)
    timeseries = FCTimeSeries(self.temporalDomain, data['data'])
    if data['success']:
      return {'data' : timeseries.timeSeriesDateToMilisecond(),
            'dataName':self.FCConfig.getDataDescriptionByName(self.variable_data['name']),
            'dataUnits':self.FCConfig.getDataUnitsbyName(self.variable_data['name']),
            'dataSize':timeseries.timeSeriesDataSize()} 
    return False

  #checks the status of the request
  @jsonify
  def statusCheck(self):
    # Tools
    t = p.toolkit
    post_info =  t.request.POST
    #init class data from post
    self.initFromPost(post_info)
    #init request
    request = self.initRequest()
    #get the response info
    answer = post_info['responseUri']
    #check to see what is in the hash
    hashIdx = answer.find("Blob=") 
    hashIdx = answer.find("hash=") if (hashIdx == -1) else hashIdx
    if (hashIdx == -1):
      print "No hash found in response: " + answer
    else:
      request.hash = answer[hashIdx + 5:].strip()
    response = request.doStatusCheck()
    return response if not inspect.isclass(type(response)) else {'status' : 'receiving', 'statusData' : 100}

  #this is to check the data size
  @jsonify
  def checkDataSize(self):
    # Tools
    t = p.toolkit
    c = t.c
    _ = t._

    #initialize temporal domain
    time_data = json.loads(post_info['time'])
    self.temporalDomain = FCTemporalDomain(time_data['years'],time_data['yc'],
          time_data['days'],time_data['dc'],time_data['hours'],time_data['hc'])
    #check to see if there is an order too large
    dataSize = FCTimeSeries(self.temporalDomain, None).timeSeriesDataSize()
    error = ""
    if dataSize > 1000:
      error = 'Data Size Too Big (' + str(dataSize) + ')'
    return error


