#------------------------------------------------------------------------------
#This class holds the data for the grids in the request
#------------------------------------------------------------------------------
class FCGrid:
  # CellGrid is constructed either from arrays of lats and lons or
  # from six arguments: latmin, latmax, latcount, lonmin, lonmax, loncount
  def __init__(self, regionType, a, b, c, d, e, f, name="",g_hash=""):
    self.spatialRegionType = regionType
    self.name = name
    self.hash = g_hash
    if self.spatialRegionType == "Points":
      if (not b):
        if (not isinstance(a,list)):
          raise Exception("Argument must be an array")
        self.lats = []
        self.lons = []
        for i in range(0,len(a)):
          self.lats.append(a[i]['lat'])
          self.lons.append(a[i]['lon'])
      else:
        if (not isinstance(a,list) or not isinstance(b,list) or not (len(a) == len(b))):
          raise Exception("Lats and lons must be arrays of same length")
        self.lats = a
        self.lons = b
    else:    
      if (isinstance(a,list) and isinstance(b,list) and not c and not d and not e and not f):
        self.lats = a
        self.lons = b
      else:
        #treat it as a point if only one row & one col
        if c == 1 and f == 1:
          self.spatialRegionType = "Points"

        self.lats = []
        #if only one row, repeat center lat for num of cols
        if c == 1:
          for i in range(0,f):
            self.lats.append((a + b)/2)
        else:
          for i in range(0,c):
            self.lats.append(a + (b - a) * i / (c - 1))

        self.lons = []
        #if only one row, repeat center lon for num of cols
        if f == 1:
          for i in range(0,c):
            self.lons.append((d + e)/2)
        else:
          for i in range(0,f):
            self.lons.append(d + (e - d) * i / (f - 1))

  #this function fills the data from the class into the request
  def fillFetchRequest(self, request):
    if "Domain" not in request:
      request["Domain"] = {}
    request["Domain"]["SpatialRegionType"] = self.spatialRegionType
    request["Domain"]["Lats"] = self.lats
    request["Domain"]["Lons"] = self.lons
    request["Domain"]['Lats2'] = None
    request["Domain"]['Lons2'] = None    

