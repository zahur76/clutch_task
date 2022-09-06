# Clutch Web Scraping

## Steps

* install scrapy ``` pip install scrapy ```

* start project ``` scrapy startproject clutch .```

* rotate proxies with  ``` pip install scrapy-rotating-proxies scrapy-proxies```

    - update settings file so as to link to proxy list (list.txt)

* create spider : clutch.py

* run crawler ``` scrapy crawl clutch --nolog ```