# Car Scraper

A  web scraping application for the AutoRia platform that automatically collects and stores car listing data.

## Structure

### /app - source code

### /dumps - folder for database backup files

 ### dockerfile - Docker image definition

 ### docker-compose - Docker orchestration
 
 ### .env.example - example of data in .env

 ### requirements.txt  - Python dependencies

## Installation & Setup

### 1) Clone the repository:

bashgit clone <repository-url>
cd car_scraper

### 2) Configure environment variables in .env file:

envDB_HOST=localhost

DB_PORT=5432

DB_NAME=car_scraper

DB_USER=your_username

DB_PASSWORD=your_password

### 3) Adjust amount of pages you want to scrape by changing return values in function (optional)

### 4) Run scripts from folder 

python app/scraping_data_async.py

#### or

### Launch the application using Docker Compose:

docker-compose up --build
