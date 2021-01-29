# Carbon Intensity API
Simple carbon intensity API for the GB grid that returns the current (5 min) carbon intensity in the GB electricity grid.  Initially draws from the 'current' generation fuel mix as published by Elexon via BMRS (1).

For avoidance of doubt, this is unrelated to National Grid's carbon intensity API (2), which does not appear to be currently supported (based upon activity in the GitHub).  I have no insight into how that works, except from their methodology paper (which does not describe how to reproduce) and assumptions published by others in journals.


Docker container build available on docker.com:
https://hub.docker.com/repository/docker/doig/carbonintensity/

Environment variables:

elexonAPIKey = Elexon API key availabe (available under 'my profile’ tab under Elexon account). 




Links:
(1) https://api.bmreports.com/BMRS/FUELINSTHHCUR

(2) https://carbonintensity.org.uk/
