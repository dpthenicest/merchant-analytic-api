the columns in the data (merchant_events) have some missing field values, but all the ids are available. I made the columns other than the ids nullable to be able to still collate the data, as not specific information was provided on how to work with missing field value.

on starting of the server, new data is populated into the database, once the server is shutdown or restarted, the data is truncated, so that new data can be populated when the server is restarted.

