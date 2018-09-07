# Define your handoff handlers here
# for more information, see:
# http://docs.tethysplatform.org/en/dev/tethys_sdk/handoff.html

import os
import requests


def csv(request, csv_url):
    """
    Handoff handler for csv files.
    """
    # Get a filename in the current user's workspace
    user_workspace = request.workspace
    filename = os.path.join(user_workspace, 'hydrograph.csv')

    # Initiate a GET request on the CSV URL
    response = requests.get(csv_url, stream=True)

    # Stream content into a file
    with open(filename, 'w') as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)

    return 'hydrograph_plotter:plot_csv'
