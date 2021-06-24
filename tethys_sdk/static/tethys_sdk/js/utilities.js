/*****************************************************************************
 * FILE:    utilities.js
 * DATE:    October, 19, 2018
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) Aquaveo 2018
 * LICENSE:
 *****************************************************************************/
function contains(str, sub) {
    if (str.indexOf(sub) === -1) {
        return false;
    }
    return true;
}


function in_array(item, array) {
    return array.indexOf(item) !== -1;
}


function is_defined(variable) {
    return !!(typeof variable !== typeof undefined && variable !== false);
}


function to_title_case(str) {
    return str.replace(/\w+/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}


function var_to_title_case(str) {
    str = str.replace(/_/ig, ' ');
    return to_title_case(str);
}


function compute_center(features) {
    let sum_x = 0,
        sum_y = 0,
        num_coordinates = 0;

    for (var i = 0; i < features.length; i++) {
        let feature = features[i], geometry;

        // If feature is a ol.Feature, we need to get the geometry
        if (feature instanceof ol.Feature) {
            geometry = feature.getGeometry();
        }
        // If feature is a geometry already
        else if (feature instanceof ol.geom.Geometry) {
            geometry = feature;
        }
        // Otherwise skip this "feature"
        else {
            continue;
        }

        // Get the geometry and sum up x's and y's
        let geometry_type = geometry.getType();

        if (geometry_type == 'Point') {
            let coordinate = geometry.getCoordinates();
            sum_x += coordinate[0];
            sum_y += coordinate[1];
            num_coordinates += 1;
        }
        else if (geometry_type == 'LineString'){
            let coordinates = geometry.getCoordinates();
            for (var i = 0; i < coordinates.length; i++) {
                let coordinate = coordinates[i];
                sum_x += coordinate[0];
                sum_y += coordinate[1];
                num_coordinates += 1;
            }
        }
        else if (geometry_type == 'Polygon') {
            let line_strings = geometry.getCoordinates();
            for (var i = 0; i < line_strings.length; i++) {
                let line_string = line_strings[i];

                for (var j = 0; j < line_string.length; j++) {
                    let coordinate = line_string[j];
                    sum_x += coordinate[0];
                    sum_y += coordinate[1];
                    num_coordinates += 1;
                }
            }
        }
        else if (geometry_type == 'MultiPolygon') {
            let line_strings = geometry.getCoordinates();
            for (var i = 0; i < line_strings.length; i++) {
                let line_string = line_strings[i];

                for (var j = 0; j < line_string.length; j++) {
                    let coordinate = line_string[j];
                    for (var k = 0; k < coordinate.length; k++) {
                        sum_x += coordinate[k][0];
                        sum_y += coordinate[k][1];
                        num_coordinates += 1;
                    }
                }
            }
        }
    }

    // Return null if no coordinates found
    if (num_coordinates <= 0) {
        return null;
    }

    let center_coordinates = [ sum_x / num_coordinates, sum_y / num_coordinates];
    return new ol.geom.Point(center_coordinates);
}


function copy_text_to_clipboard(text) {
    if (!navigator.clipboard) {
        _fallback_copy_text_to_clipboard(text);
        return;
    }

    navigator.clipboard.writeText(text).then(function() {
        console.log('Async: Copying to clipboard was successful!');
    }, function(err) {
        console.error('Async: Could not copy text: ', err);
    });
}


function _fallback_copy_text_to_clipboard(text) {
    // Copy hack using hidden text area
    var text_area = document.createElement('textarea');
    text_area.value = text;
    document.body.appendChild(text_area);
    text_area.focus();
    text_area.select();

    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(text_area);
}

// Utilities to convert utc time to local time.
function convert_utc_to_local(identifier) {
    let time_list = $(identifier);
    for (i=0; i < time_list.length; i++) {
        let utc_time = time_list[i].innerText;
        utc_time += " UTC";

        // Remove all commas and dots
        utc_time = utc_time.replace(/,/g, "").replace(/\./g, "");

        // Handle case where we have no minutes such as "May 4 2000 5 pm UTC"
        // This needs to be "May 4 2000 5:00 pm UTC"
        if (!utc_time.includes(":")) {
            let position = utc_time.indexOf('UTC') - 4;
            utc_time = [utc_time.slice(0, position), ":00", utc_time.slice(position)].join("");
        }

        let local_time = new Date(utc_time);
        if (!isNaN(local_time.getTime())) {
            // Update time
            time_list[i].innerText = format_output_time(local_time);
        }
    }
}

function format_output_time(date) {
    // return Date in format of MMM DD YYYY HH:MM AM/PM
    var month = date.toLocaleString('default', { month: 'long' });
    var day = date.getDate();
    var year = date.getFullYear();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    // Get local timezone
    var timezone = date.toLocaleTimeString('en-us',{timeZoneName:'short'}).split(' ')[2];
    var strTime = month + " " + day + " " + year + " " + hours + ':' + minutes + ' ' + ampm + " " + timezone;
    return strTime;
}
