# Clutch Web Scraping


## Scrapy Setup Steps

* install scrapy ``` pip install scrapy ```

* start project ``` scrapy startproject clutch .```

* rotate proxies with  ``` pip install scrapy-rotating-proxies scrapy-proxies```

    - update settings file so as to link to proxy list (list.txt)

* create spider : clutch.py

## Installation

``` pip install -r requirements.txt```

## Scrapy Run Command

* run crawler ``` scrapy crawl clutch --nolog ```

output: json file

## File Conversion

* run ``` python clean_json.py ``` to clean json file and remove empty lists
* run ``` python json_to_csv ``` to convert json file to csv.

## Process

* first run scarpy spider
* clean json file
* convert json file to csv
