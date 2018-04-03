

def add_geoserver_rest_to_endpoint(endpoint):
    parts = endpoint.split('//')
    protocol = parts[0]
    parts2 = parts[1].split(':')
    host = parts2[0]
    port_and_path = parts2[1]
    port = port_and_path.split('/')[0]

    return '{0}//{1}:{2}/geoserver/rest/'.format(protocol, host, port)
