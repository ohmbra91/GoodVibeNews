#!/bin/bash

# Correct path to the virtual environment
VENV_PATH="/home/ubuntu/scrapers/"

# Activate the virtual environment
source "/home/ubuntu/scrapers/newsvenv/bin/activate"

# Navigate to the Scrapy project directory
cd /home/ubuntu/scrapers/data-visualization-app/scrapers/tomscraper

# Run the Scrapy spiders
scrapy crawl tom_spider
scrapy crawl mt_spider
scrapy crawl tmi_spider  # Add additional spiders as needed
scrapy crawl tvm_spider
scrapy crawl lm_spider

# Deactivate the virtual environment
deactivate