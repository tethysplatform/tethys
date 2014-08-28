'''
********************************************************************************
* Name: dataset_tools.py
* Author: Nathan Swain
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''
import ckan.plugins as p
from datetime import datetime
import shutil, zipfile, StringIO, pprint
from os import path
from ckan import model
from ckanext.tethys_apps.lib import ckanclient_ppp as ckanclient

import urllib2, os, requests, json

def get_resource_by_field_value(query):
    '''
    Retrieve a list of resources by the value of a field
    
    query is a string list of field-value pairs::
    
        query = '{field}:{value}, {field}:{value},...'
        
    This is just a veneer on the resource_search() action. See the 
    CKAN action API for more detail about the method.
    '''
    # Get plugins toolkit
    t = p.toolkit
    return t.get_action('resource_search')(data_dict={'query': query})

def get_resource(id):
    '''
    Retrieve a resource by id
    '''
    # Get plugins toolkit
    t = p.toolkit
    return t.get_action('resource_show')(context={'model': model},
                                         data_dict={'id': id})
    
def get_resource_attribute(resource_id, attribute):
    '''
    Retrieve the value of a resource attribute
    '''
    resource = get_resource(resource_id)
    return resource[attribute]

def get_resource_url_name(resource_id):
    '''
    Retrieve resource name and return it in lower case
    with spaces replaced by '-'
    '''
    resource = get_resource(resource_id)
    name = resource['name']
    return '-'.join(name.lower().split())

def get_package_name_for_resource(resource_id):
    '''
    Retrieve package for given resource_id
    '''
    t = p.toolkit
    context = {'model': model}
    
    package_list = t.get_action('package_list')(context)
    
    for package in package_list:
        query = 'name:%s'% package
        results = t.get_action('package_search')(context=context,
                                                 data_dict={'q': query})
        pkg = results['results'][0]
        package_resources = pkg['resources']
        
        for resource in package_resources:
            if resource['id'] == resource_id:
                return package
    return None

def upload_file_back_to_package (base_location, context, resource_id, file_path, name, **kwargs):
    '''
    Upload file to filestore using Filestore API via a modified version of CkanClient.
    The file is uploaded to the package that the orignal resource belonged too. The
    
    context = context object (c)
    file_path = path to file to upload
    name = name of resource that will be created
    resource_id = id of original resource
    name = name of new resource being created
    **kwargs =  key value resource attributes
    
    Returns the Response object of the request.
    '''
    # Create ckan client objectj
    file_path = str(file_path) # Make sure path is a string  
    user = context.userobj
    api_key= user.apikey
    http_user = user.name
    http_pass = user.password
    client = ckanclient.CkanClient(base_location=base_location,
                                   api_key=api_key,
                                   is_verbose=True,
                                   http_user=http_user,
                                   http_pass=http_pass)
     
    # Add resource to original package
    kwargs['name'] = name
    package = get_package_name_for_resource(resource_id)
    result = client.add_package_resource(package, file_path, **kwargs)
    return result



def add_file_to_package (base_location, context, package_name, file_path, name, **kwargs):
    '''
    Upload file to a dataset (package) filestore using Filestore API via a modified version of CkanClient.
    
    base_location = url of the api endpoint (e.g. http://www.myckan.org/api)
    context = context object (c)
    file_path = path to file to upload
    name = name of resource that will be created
    package_name = name of the pacakge to upload to
    name = name of new resource being created
    **kwargs =  key value resource attributes
    
    Returns the Response object of the request.
    '''
    # Create ckan client objectj
    file_path = str(file_path) # Make sure path is a string  
    user = context.userobj
    api_key= user.apikey
    http_user = user.name
    http_pass = user.password
    client = ckanclient.CkanClient(base_location=base_location,
                                   api_key=api_key,
                                   is_verbose=True,
                                   http_user=http_user,
                                   http_pass=http_pass)
     
    # Add resource to original package
    kwargs['name'] = name
    package = package_name
    result = client.add_package_resource(package, file_path, **kwargs)
    return result

def append_file_to_package(api_endpoint, context, package_name, file_path, name, **kwargs):
    '''
    Upload file to package using the FileStore API directly.
    
    api_endpoint = url of the api endpoint (e.g. http://www.myckan.org/api)
    context = context object (c)
    file_path = path to file to upload
    name = name of resource that will be created
    package_name = name of the pacakge to upload to
    name = name of new resource being created
    **kwargs =  key value resource attributes
    
    Returns the the json response object from the response.
    '''
    # Construct url for request
    if api_endpoint[-1] == '/':
        api_create_resource = api_endpoint + 'action/resource_create'
    else:
        api_create_resource = api_endpoint +'/action/resource_create'
    
    # Construct data payload   
    data = {'package_id': package_name,
            'name': name}
    
    # Append kwargs to data payload
    for key, value in kwargs.iteritems():
        data[key] = value
    
    # Create headers with API key
    headers = {'X-CKAN-API-Key': context.userobj.apikey}
    
    # Prepare file for upload
    f_dir, f_name = os.path.split(file_path)
    os.chdir(f_dir)
    files = [('upload', file(f_name))]
    
    # Submit request
    result = requests.post(api_create_resource,
                           data=data,
                           headers=headers,
                           files=files)
    
    # Default result is unsuccessful
    json_result = {'success': False}
    
    if (result.status_code == 200):
        json_result = result.json()
    
    return json_result  

def delete_directory(directory):
    '''
    Delete directory in workspace.
    
    directory = path to directory in workspace
    '''
    shutil.rmtree(directory)

def extract_zip_from_url(user_id, download_url, workspace):
    '''
    Extract zip directory to workspace in a directory 
    with a unique name consisting of a timestamp and user id.
    
    user_id =  id of user performing operation
    download_url = url where zip archive can be downloaded
    workspace = location to extract file
    
    returns extract_path
    '''
    # Setup workspace
    time_stamp = datetime.isoformat(datetime.now()).split('.')[0]
    
    # Replace chars
    for char in (':', '-', 'T'):
        time_stamp = time_stamp.replace(char, '')
    
    normalized_id = user_id.replace('-', '')
    unique_dir = ''.join((time_stamp, normalized_id))    

    # Extract
    extract_path = path.join(workspace, unique_dir)    
    zip_file = urllib2.urlopen(download_url)
    zf = zipfile.ZipFile(StringIO.StringIO(zip_file.read()))
    zf.extractall(extract_path)
    
    return extract_path, unique_dir
    
    
    
    


