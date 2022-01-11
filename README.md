# Short Analysis of West Los Angeles Housing

#### Back Story

Shortly before Christmas 2021 I was poking around Zillow, and I noticed
that every apartment I looked at had a Zestimate that looked like this:

![Zillow Example](resources/zillow_example.png?raw=true "A Zestimate")

Huh, it looks like housing prices are in some kind of plateau.  Why?
Zillow has been in the [news](https://www.cnn.com/2021/11/09/tech/zillow-ibuying-home-zestimate/index.html)
[lately](https://podcasts.apple.com/au/podcast/is-zillow-really-buying-all-the-houses/id1346207297?i=1000542271091)
for shuttering their house trading business because they overbid on
the houses they were buying.  I'm pretty skeptical of the Zestimate.

So, I decided to go get my own data for West Los Angeles.

## Los Angeles Housing Data

It turns out that, if you want to know what is going on with 
Los Angeles  housing, that the Los Angeles Assessor's (LAA) office
has an easily searched database.  Unfortunately, the search function
isn't very smart.  You can't just put in a zip code and scrape all 
the data. It isn't *THAT* easy.

So, I found a list of Los Angeles Addresses, filtered for the zip 
codes I wanted and then searched those addresses on the LAA website.

That list can be found in Addresses_in_the_City_of Los Angeles.csv.
Then I turned this into a zip-code-filtered pandas dataframe.

#### __main__.py
After I have a list of addresses, I searched them one-by-one on the 
LAA website.  Instead of looking for specific hits, I'd just search
and then scrape all the addresses with the correct zip codes.  By
filtering for Assessor Identification Number (AIN), I don't get any
duplicate records.
This created a pandas dataframe of something like 30k unique AINs.

Now, I scrape the LAA website by AIN.  This allows me to directly
retrieve the JSON files from their back end.  I save all the information
in separate JSON files.  I've had some bad experiences with corrupted
files and I wanted each to be separate when saved while scraping
over a few days and nights.

#### json_reader.py

I combine the JSON files into a pandas dataframe, filter for 
ambiguous cases (what is a '2+' bedroom, anyway?) and do type
conversion on the various data types.

I also had to get some inflation adjustment.  I got three indexes from
the [Bureau of Labor Statistics](https://data.bls.gov/pdq/SurveyOutputServlet):

- CWUR0000SAH1 = CPI for Urban Wage Earners and Clerical Workers (CPI-W
- CWSR0000SAH1 = Shelter in U.S. city average, urban wage earners and clerical workers, seasonally adjusted
- CWURS49ASA0 = All items in Los Angeles-Long Beach-Anaheim, CA, urban wage earners and clerical workers, not seasonally adjusted

These seem like reasonable indexes: wages, shelter in the urban US, and
the cost of goods in Los Angeles.

#### plots.py

Finally, I can plot the data I want to see.  Let me simply dump the plots
here, first.

![CPIW](resources/zipcode_CPIW.png?raw=true "CPI-W")
![UrbanShelter](resources/zipcode_CPIW.png?raw=true "Urban Shelter")
![LAGoods](resources/zipcode_CPIW.png?raw=true "LA Goods")

I've plotted the sales price for 1, 2, and 3 bedroom housing in the 
three listed zip codes.  The dashed line shows the median for each
scatter plot for the year of 2006.  That year is the peak of the 
[Case-Schiller Index for Los Angeles](https://fred.stlouisfed.org/series/LXXRSA)
around the peak of the housing bubble.