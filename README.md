# Carbon Intensity API
Simple carbon intensity API for the GB grid that returns the current (5 min) carbon intensity in the GB electricity grid.  Initially draws from the 'current' generation fuel mix as published by [Elexon](https://www.elexon.co.uk) via [BMRS](https://api.bmreports.com/BMRS/FUELINSTHHCUR).

For avoidance of doubt, this is unrelated to [National Grid's carbon intensity API](https://carbonintensity.org.uk/), which does not appear to be currently supported (based upon activity in the GitHub).  I have no insight into how that works, except from their methodology paper (which does not describe how to reproduce) and assumptions published by others in journals.

### Docker repository
Docker container build available on docker.com:
https://hub.docker.com/repository/docker/doig/carbonintensity/

### Environment variables
| Variable | Description |
| --- | --- |
| carbonintensity_elexonAPIKey | Personal Elexon API key, available under 'my profile’ tab under Elexon account (free registration) |
| --- | --- |
| carbonintensity_appUseDirectAPI | True/False dictates whether calls to the API are directly passed onto the Elexon API (Default, True) or whether a MySQL DB server is used to cache results (False) |
| carbonintensity_dbServer | MySQL DB server address (if any) |
| carbonintensity_dbUser | MySQL DB user name (if any) |
| carbonintensity_dbPassword | MySQL DB user password (if any) |
| carbonintensity_dbSchema | MySQL DB scheme name for caching data (if any) |
| carbonintensity_dbTable | MySQL DB table name for caching data (if any) |
| --- | --- |
| carbonintensity_port | Port on which to listen for calls to API |



## Development plan

- Caching of generation data calls to speed up API response
- Addition of parameters to return more information
- More accurate carbon intensity factors for each fuel type/source
- Incorporating TensorFlow model for providing forecasts
