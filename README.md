# Carbon Intensity API
Simple carbon intensity API for the GB grid that returns the current (last 5 min) carbon intensity (gCO2/kWh) in the GB electricity grid.  Initially draws from the 'current' generation fuel mix as published by [Elexon](https://www.elexon.co.uk) via [BMRS](https://api.bmreports.com/BMRS/FUELINSTHHCUR).

For avoidance of doubt, this is unrelated to [National Grid's carbon intensity API](https://carbonintensity.org.uk/), which does not appear to be currently supported (based upon activity in the GitHub).  I have no insight into how that works, except from their methodology paper (which does not describe how to reproduce) and assumptions published by others in journals.

### Example API response
```
{
    "response": {
        "Average Carbon Intensity (gCO2/kWh)": 223.2,
        "Data Last Updated": "2021-01-31 17:15:00"
    }
}
```

### Docker repository
Docker container build available on docker.com:
https://hub.docker.com/repository/docker/doig/carbonintensity/

### Environment variables
Configuration of the API can be made via environmment variables either in the Docker container or system.
| Environment variable | Description |
| ------------- | ------------- |
| `carbonintensity_port` | Port on which to listen for calls to API (default: 8812) |
| `carbonintensity_serverFolder` | Server folder on which to listen for calls to API (default: \carbon) |
| `carbonintensity_elexonAPIKey` | Personal Elexon API key, available under 'my profile’ tab under Elexon account (free registration) |
| `carbonintensity_appUseDirectAPI` | True/False dictates whether calls to the API are directly passed onto the Elexon API (True) or whether a MySQL DB server is used to cache results (False) (default: True) |
| `carbonintensity_dbServer` | MySQL DB server address (if any) |
| `carbonintensity_dbUser` | MySQL DB user name (if any) |
| `carbonintensity_dbPassword` | MySQL DB user password (if any) |
| `carbonintensity_dbSchema` | MySQL DB scheme name for caching data (if any) |
| `carbonintensity_dbTable` | MySQL DB table name for caching data (if any) |




## Development plan

- Caching of generation data calls to speed up API response
- Addition of parameters to return more information
- More accurate carbon intensity factors for each fuel type/source
- Incorporating TensorFlow model for providing forecasts


## Example API response (showsources=True)
```
{
    "response": {
        "Average Carbon Intensity (gCO2/kWh)": 215.7,
        "Data Last Updated": "2021-02-02 12:10:00",
        "Sources": [
            {
                "fuelType": "CCGT",
                "currentMW": 15855,
                "carbonIntensity": 394
            },
            {
                "fuelType": "OCGT",
                "currentMW": 0,
                "carbonIntensity": 651
            },
            {
                "fuelType": "OIL",
                "currentMW": 0,
                "carbonIntensity": 935
            },
            {
                "fuelType": "COAL",
                "currentMW": 1567,
                "carbonIntensity": 937
            },
            {
                "fuelType": "NUCLEAR",
                "currentMW": 5215,
                "carbonIntensity": 0
            },
            {
                "fuelType": "WIND",
                "currentMW": 10820,
                "carbonIntensity": 0
            },
            {
                "fuelType": "PS",
                "currentMW": 0,
                "carbonIntensity": 0
            },
            {
                "fuelType": "NPSHYD",
                "currentMW": 233,
                "carbonIntensity": 0
            },
            {
                "fuelType": "OTHER",
                "currentMW": 148,
                "carbonIntensity": 300
            },
            {
                "fuelType": "INTFR",
                "currentMW": 2003,
                "carbonIntensity": 48
            },
            {
                "fuelType": "INTIRL",
                "currentMW": 251,
                "carbonIntensity": 426
            },
            {
                "fuelType": "INTNED",
                "currentMW": 0,
                "carbonIntensity": 513
            },
            {
                "fuelType": "INTEW",
                "currentMW": 339,
                "carbonIntensity": 426
            },
            {
                "fuelType": "BIOMASS",
                "currentMW": 1742,
                "carbonIntensity": 120
            },
            {
                "fuelType": "INTNEM",
                "currentMW": 999,
                "carbonIntensity": 132
            },
            {
                "fuelType": "INTIFA2",
                "currentMW": 0,
                "carbonIntensity": 48
            },
            {
                "fuelType": "INTNSL",
                "currentMW": 0,
                "carbonIntensity": 0
            }
        ]
    }
}
```

