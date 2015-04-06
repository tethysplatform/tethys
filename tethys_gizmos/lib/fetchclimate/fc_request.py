import datetime,json,re,requests
from fc_response import FCResponse
#------------------------------------------------------------------------------
#This class holds the data for the request to the Fetch Climate server
#------------------------------------------------------------------------------
class FCRequest:
  def __init__(self, options=None):
    self.status = "new" # Status is "new" | "pending" | "calculating" | "receiving" | "completed" | "failed"
    self.statusData = None # Status data is null | position in queue (may be NaN) | progress 0..100 | uri of blob | error message
    self.dataSources = {};
    self.timeout = options["timeout"] if "timeout" in options else 180000 # Default ajax timeout is 3 minutes
    self.pollInterval = options["pollingInterval"] if "pollingInterval" in options else 10000 # Default polling interval is 10 seconds
    self.serviceUrl = options["serviceUrl"] if "serviceUrl" in options else "http://fetchclimate2.cloudapp.net"
    self.hash = ""
    if "rawJSON" in options:
      self.requestJSON = options.rawJSON
    else:
      self.spatial = options["spatial"]
      self.temporal = options["temporal"]
      self.variable = options["variable"]
      self.requestJSON = {
        "EnvironmentVariableName": str(self.variable), 
        "Domain": {"Mask":None},
        "ParticularDataSources" : options["dataSources"] if "dataSources" in options else [],
        "ReproducibilityTimestamp": options["timestamp"] if "timestamp" in options else 253404979199999
        }
      self.spatial.fillFetchRequest(self.requestJSON)
      self.temporal.fillFetchRequest(self.requestJSON)

  def positionInQueue(self):
    return float('nan') if self.status != "pending" else self.statusData

  def percentCompleted(self):
    if (self.status == "calculating"):
      return self.statusData
    elif (self.status == "receiving" or self.status == "completed" or self.status == "failed"):
      return 100
    else:
      return 0

  def errorMessage(self):
    return "" if self.status != "failed" else self.statusData

  def resultUrl(self):
    return None if self.status != "completed" else self.statusData

  def onAjaxSuccess(self, answer):
    # Expected values on stat5: 'pendi' | 'progr' | 'compl' | 'fault'
    stat5 = answer[0:min(len(answer), 5)]
    print str(datetime.datetime.now()) + ": Status received " + answer

    if (stat5 == "pendi" or stat5 == "progr"):
      # 'pending', 'progress' responses contain hash.
      hashIdx = answer.find("hash=")

      if (hashIdx == -1): 
        #failRequest("No hash found in response: " + answer);
        print "No hash found in response: " + answer
      else:
        self.hash = answer[hashIdx + 5:].strip()

      if stat5 == "pendi":
        self.status = "pending"
        self.statusData = int(re.findall("pending=(\d+);",answer)[0])
      elif stat5 == "progr":
        self.status = "calculating"
        self.statusData = int(re.findall("progress=(\d+)%;",answer)[0])

      return {'status' : self.status, 'statusData' : self.statusData}

    elif (stat5 == "compl"):
      self.status = "receiving";
      self.statusData = answer[10:]
      hashIdx = answer.find("Blob=")
      if (hashIdx != -1):
        self.hash = answer[hashIdx + 5:].strip()
      return FCResponse(self,self.statusData)

    elif (stat5 == "fault"):
      # 'fault' responses contain hash.
      hashIdx = answer.find("hash ")

      if (hashIdx == -1) :
        print "No hash found in response: " + answer
      else:
        self.hash = answer[hashIdx + 5:].strip()
      return None

  #request info from FetchClimate Server
  def doPost(self):
    self.status = "pending"
    self.statusData = float('nan')
    headers={'content-type':'application/json; charset=utf-8', 'data-type':'json'}
    r = requests.post(self.serviceUrl + "/api/compute", 
      data=json.dumps(self.requestJSON),headers=headers, 
      timeout=self.timeout)
    if r.status_code == requests.codes.ok:
      return self.onAjaxSuccess(r.json())
    return "Error: " + r.status_code

  #checks status of request to FetchClimate Server
  def doStatusCheck(self):
    print str(datetime.datetime.now()) + ": Getting state for " + self.hash
    r = requests.get(self.serviceUrl + "/api/status?hash=" + self.hash, 
      timeout=self.timeout)
    if r.status_code == requests.codes.ok:
      return self.onAjaxSuccess(r.json())
    return "Error: " + r.status_code


