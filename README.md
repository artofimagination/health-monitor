# Simple health monitor
this little application is usefule for logging and monitoring some health related data and connected events. At the moment it can log blood pressure, and pulse. For each log entry an event can be added with a description, so the user can correlate between the pressure and a stressful event, sport activity, or diet change.

# Usage
The app is extremely simple. It stores all the data in csv files. By default, some of my own data is put in as an example. Please go in src/data and open data.csv and users.csv and delete all entries except the header line. Now you are ready to put in your own data.

# Setup
The whole app is written in python and is dockerized. Using VS Code, do the following steps
 - Install extensions Docker (Microsoft), Remote-containers (Microsoft)
 - Click in the green area in the bottom left corner (Open a Remote Window)
 - Reopen in container (Select from Dockerfile)
 - Run ```xhost local:docker``` in the host command line
 - If all goes well, you just need press F5 and it should start build and then the application with Debug.
