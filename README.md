# Project 1: Data crawler for Jingdong e-commerce platform

# requirements.txt
Python libraries are needed to run the crawler.

# launch.py
The interface through which the data crawler runs.

# settings.py
For simplicity, this file contains only settings considered important or commonly used. You can find more settings consulting the documentation: http://doc.scrapy.org/en/latest/topics/settings.html; http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html; http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

# pipelines.py
Define your item pipelines here.Don't forget to add your pipeline to the ITEM_PIPELINES setting. See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# middlewares.py
Define here the models for your spider middleware. See documentation in: http://doc.scrapy.org/en/latest/topics/spider-middleware.html

# item.py
Define the data items you want to collect in the form of classes in this file.

# proxy.py
IP and port proxy for the crawler.

# JDSpider.py
The data crawler parses the code of the website pages.
