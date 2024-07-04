## Geoscripting project repository.

**Title:** Assessing the monumental state of buildings to enable more targeted energy transition on a household level.\
**Team:** Teal_panther\
**Number of the topic chosen (or "own"):** 6\
**Description:** This repository retrieves information about the monumental state of Dutch buildings on a national ('rijksmonument') and municipal ('gemeentelijk monument') level and specifies whether a given building is positioned within the protected cityscape area. Based on the year of construction retrieved from the Key Register of Adresses and Buildings (BAG), the repository assigns information about whether installation of a heating pump is allowed and/or recommended. Finally, the project results in a geojson file of the user-defined area extent and an interactive map where all relevant infromation is displayed.\
**How to use:** The code asks for 4 inputs in order to generate an output. Firstly, the user needs to define the longitude and latitude coordinates of the center point of the extent they would like to investigate. In the current version, we recommend using the coordinates of one of the **example locations mentioned below only** - otherwise the code will return an error. Secondly, the user needs to define the horizontal and vertical length of the area extent. The desired inputs are multiples of 300 (meters) (e.g. 600, 900, 1200). As the script is currently only useful for the city center of Amsterdam it is suggested to use the recommended extents per location as mentioned below. Finally, the user can specify the name of the output geojson and html map file.

**The ZOO of Artis** \
Longitude: 4.915601 \
Latitude: 52.365728 \
Horizontal length of the extent: 600 \
Vertical length of the extent: 600 

**De Oude Kerk** \
Longitude: 4.8978013069 \
Latitude: 52.3742407533 \
Horizontal length of the extent: 900 \
Vertical length of the extent: 1200 

**Rijksmuseum** \
Longitude: 4.884817 \
Latitude: 52.359764 \
Horizontal length of the extent: 900 \
Vertical length of the extent: 300 

**University of Amsterdam Oudemanhuispoort (UVA)** \
Longitude: 4.895479 \
Latitude: 52.368893 \
Horizontal length of the extent: 2100 \
Vertical length of the extent: 2100 

**Data used:**

**1)** BAG: buildings from cadastre: and https://data.overheid.nl/en/dataset/basisregistratie-adressen-en-gebouwen--bag- \
*Metadata:* https://stelselvanbasisregistraties.nl/details/METADATA/BAG \
*Author:* The dutch cadastre. \
*Date:* all data is last modified on the 8th of January 2023. \
*Information about:* The BAG contains information about 5 objects: panden, verblijfsobjecten, nummeraanduidingen, openbare ruimtes en woonplaatsen. The attributes are for example, geometry, xy coordination, year of building, status, size and use. 
    
**2)** Rijksmonumenten: https://nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/eedd39d6-b427-4e11-90fd-f5054241
*Metadata:* https://nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/eedd39d6-b427-4e11-90fd-f5054241c3a7 \
*Author:* Rijksdienst voor het Cultureel Erfgoed.\
*Date:* 8th of November 2022.\
Information about: the Nationaal georegister contains data for all civil structures that are considered as ¨rijksmonument". 

**3)** Gemeentelijke monumenten: https://map.data.amsterdam.nl/maps/monumenten?REQUEST=GetFeature&SERVICE=wfs&typename=monument_coordinaten&outputformat=geojson&VERSION=2.0.0&SRSNAME=EPSG:4326
*Author:* Gemeente Amsterdam - Monumenten en Archeologie.\
*Date:* 11th of June 2017.\
*Information about:* This source gives us information about the Gemeentelijke monumenten(and also rijksmonumenten), these are monuments
which are considered from regional importance. 

**4)** Beschermd stadsgezicht: https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/4e2ef670-cddd-11dd-ad8b-0800200c9a66
*Author/responsible organisation:* Rijksdienst voor het Cultureel Erfgoed.\
*Date:* 8th of November 2022.\
*Information about:* Information about cityscapes of the Netherlands. Cityscapes (in Dutch: Rijksbeschermd Stadsgezichten) are cities with a special culturehistorical background. it is meant to keep the identity intact. 