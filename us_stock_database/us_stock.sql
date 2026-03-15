DROP DATABASE IF EXISTS financial_app;
CREATE DATABASE financial_app;
USE financial_app;

CREATE TABLE financial_instrument_table (
    Instrument_Name VARCHAR(255) PRIMARY KEY,
    Instrument_Type VARCHAR(255)
);
LOAD DATA LOCAL INFILE 'C:\\Users\\yz564\\Desktop\\Yinan_Zhou\\Analytics\\ITC6000\\US_stock\\tables\\financial_instrument_table.csv'
INTO TABLE financial_app.financial_instrument_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

CREATE TABLE stock_table (
    Stock_ID VARCHAR(255),
    Date DATE,
    Instrument_Name VARCHAR(255),
    Price DECIMAL(10, 2),
    Volume INTEGER,
    PRIMARY KEY (Stock_ID, Date),
    FOREIGN KEY (Instrument_Name) REFERENCES financial_instrument_table(Instrument_Name)
);
LOAD DATA LOCAL INFILE 'C:\\Users\\yz564\\Desktop\\Yinan_Zhou\\Analytics\\ITC6000\\US_stock\\tables\\stock_table.csv'
INTO TABLE financial_app.stock_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(Stock_ID, Date, Instrument_Name, Price, Volume);


CREATE TABLE cryptocurrency_table (
    Crypto_ID VARCHAR(255),
    Date DATE,
    Instrument_Name VARCHAR(255),
    Price DECIMAL(20, 2),
    Volume INTEGER,
    PRIMARY KEY (Crypto_ID, Date),
    FOREIGN KEY (Instrument_Name) REFERENCES financial_instrument_table(Instrument_Name)
);
LOAD DATA LOCAL INFILE 'C:\\Users\\yz564\\Desktop\\Yinan_Zhou\\Analytics\\ITC6000\\US_stock\\tables\\cryptocurrency_table.csv'
INTO TABLE financial_app.cryptocurrency_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(Crypto_ID, Date, Instrument_Name, Price, Volume);

CREATE TABLE index_table (
    Index_ID VARCHAR(255),
    Date DATE,
    Instrument_Name VARCHAR(255),
    Price DECIMAL(20, 2),
    Volume INTEGER,
    PRIMARY KEY (Index_ID, Date),
    FOREIGN KEY (Instrument_Name) REFERENCES financial_instrument_table(Instrument_Name)
);
LOAD DATA LOCAL INFILE 'C:\\Users\\yz564\\Desktop\\Yinan_Zhou\\Analytics\\ITC6000\\US_stock\\tables\\index_table.csv'
INTO TABLE financial_app.index_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(Index_ID, Date, Instrument_Name, Price, Volume);

CREATE TABLE commodity_table (
    Commodity_ID VARCHAR(255),
    Date DATE,
    Instrument_Name VARCHAR(255),
    Price DECIMAL(20, 3),
    Volume INTEGER,
    PRIMARY KEY (Commodity_ID, Date),
    FOREIGN KEY (Instrument_Name) REFERENCES financial_instrument_table(Instrument_Name)
);
LOAD DATA LOCAL INFILE 'C:\\Users\\yz564\\Desktop\\Yinan_Zhou\\Analytics\\ITC6000\\US_stock\\tables\\commodity_table.csv'
INTO TABLE financial_app.commodity_table
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(Commodity_ID, Date, Instrument_Name, Price, Volume);

-- Union Query for Index and Commodity Data
SELECT 
i.Date, i.Index_ID, i.Instrument_Name AS Index_Name, i.Price AS Index_Price, i.Volume AS Index_Volume,
c.Commodity_ID, c.Instrument_Name AS Commodity_Name, c.Price AS Commodity_Price, c.Volume AS Commodity_Volume
FROM index_table i
JOIN commodity_table c 
ON i.Date = c.Date
WHERE i.Index_ID = 'Index_1' AND c.Commodity_ID = 'Commodity_1';

-- Union Query for Cryptocurrency and Commodity Data
SELECT 
r.Date, r.Crypto_ID, r.Instrument_Name AS Crypto_Name, r.Price AS Crypto_Price, r.Volume AS Crypto_Volume,
c.Commodity_ID, c.Instrument_Name AS Commodity_Name, c.Price AS Commodity_Price, c.Volume AS Commodity_Volume
FROM cryptocurrency_table r
JOIN commodity_table c 
ON r.Date = c.Date
WHERE r.Crypto_ID = 'Crypto_1' AND c.Commodity_ID = 'Commodity_3';

-- What is the average price of natural gas over the specified time period (2023-01-01 to 2023-12-31)?
SELECT AVG(Price) AS Average_Price
FROM commodity_table
WHERE Instrument_Name = 'Natural_Gas'
AND Date BETWEEN '2023-01-01' AND '2023-12-31';

-- Which day had the highest volume of crude oil traded?
SELECT Date, Volume AS Highest_Volume
FROM commodity_table
WHERE Volume = (
    SELECT MAX(Volume)
    FROM commodity_table
    WHERE Instrument_Name = 'Crude_Oil'
);

-- Which stock had the largest percentage change in price from the beginning of the dataset to the end?
SELECT Stock_ID, Instrument_Name AS Stock_Name, ((MAX(Price) - MIN(Price)) / MIN(Price)) * 100 AS Percentage_Change
FROM stock_table
GROUP BY Stock_ID, Instrument_Name
ORDER BY Percentage_Change DESC
LIMIT 1;








