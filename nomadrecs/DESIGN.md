Nomadrecs uses some of the finance projects code as a starting point, including login, register, some error handling, and flask. It iterates on that work, adding pages specific to the site. Upon login, a user is greated with a count of how many countries they have visited, and what percentage of countries in the world that is, using SQL to query a database called history. The history database includes data that is added by users on the add trip page, which can include the country, selected from a drop down list, the dates of the trip, and a private note the could include details about the trip. 

The history page similarly pulls from the history db to list the full details of a trip as they were added by a user. It also allows a user to delete a trip they have creaated. The maps page includes an interactive map that puts pins on the places that a user has visited as recorded in the history db. Currently only some coutries are supported, as it will take some effort to add coordinates to the list for each country, though that may be a good place for AI to assist. 

Additionally, you will see that the countries list is hard coded multiple times in the website. That would not be best practice. I did some research into how to populate the dropdown via a database, but decided it would take too much time, or a significant amount of AI help for me to implement that successfully. 

The maps page was built using the documentation from google on using their API's. A link to that documentation is in the file. I also created a google cloud account to get an API key for the map specific to nomad recs. The addition of the pins is the primary place I used AI in this project. It was able to generate a few lines of code to help add the layer on top of the map that supports multiple pins. As far as I was able to see, the google maps documentation supported one pin.

The recs page uses a separate database to store the userID of the person who added the rec, and the recommendation. The page uses a join query to pull the username and the text of the rec for the selected country. 

My primary use of AI throughout the project, with the exception of the pins on the maps was as a debugging tool. I would first write code to do what I hoped to do, then if errors came up, or I was unsure on syntax, I would ask AI to assist. 

You will see in the code that there is the base code for adding a like button to the recs page. I started work on this, and it is nearly complete, however I was unable to get it working as expected by the deadline. I left it in to show additional progress. 

The project is currently running on an EC2 instance. This semester I took a cloud class that taught us basic setup for EC2 instances, but not how to run apps such as this on EC2. I was able to watch youtube videos, and use AI instructions to run the flask app on ec2. I previously had purchased the nomadrecs.com domain, and was able to research how to set up an A record to point to a static IP address in AWS. I did not use this for any project for that class, this was only for this class. 

When I looked at final project examples at the beginning of the semester, I thought there was no way I would be able to create something like that. I am in shock at what I was able to create, albiet using the code created by cs50 staff as a starting point. 
