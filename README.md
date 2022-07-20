# Systems Practicum Project
Docker Deployment system that can deploy any application created, just using the docker image form docker hub and the port on which the app runs. This scalable systems project has one host machine that has many machines connected to it on which the docker image can be deployed. If the load on one machine increases, another instance of the app will be deployed on the another machine to balance the load.

### Features
1. Mulitple Machienes Architecture, Load balancing by creating bash file for Nginx
2. Local DNS configuration for subdomains, so that apps have a good looking domain name
3. We use Fork call while creating instances so that the user experience will be great and he gets updates in the background if the app if deployed successfully.
4. Building Docker container on different machines using just the docker image
5. Choosing best machine for instance creation, Machine Statistics and charts
6. A terminal with limited access using socket communication. so that users can access the machine and check logs for their app.
7. Heath_checker that runs in background and creates another instance if one instance gets failed. Thus increasing availability.

### Architecture
![image](https://user-images.githubusercontent.com/56730716/180038481-9e114d32-1c3b-4c5e-9c48-e696c1742aba.png)

### Flow and Information
![image](https://user-images.githubusercontent.com/56730716/180038908-70caf705-bf53-41fe-8bdc-8f4c09dd1785.png)

![image](https://user-images.githubusercontent.com/56730716/180038968-bd243d65-fcac-48a4-bbe8-26f999110773.png)

![image](https://user-images.githubusercontent.com/56730716/180039053-a36f1c40-9e04-4d2c-89bd-3d137bcf6f4a.png)

![image](https://user-images.githubusercontent.com/56730716/180039167-22e7d6ac-d506-4d0d-842d-061a4a95c029.png)

![image](https://user-images.githubusercontent.com/56730716/180039219-c7c81865-b821-4169-b900-841e64f8dd43.png)

### Tech Stack Used
- Flask – Different flask apps run on both the backend machines and the master machine responsible for proper functioning of the service
- HTML/CSS/JS – To create the various frontends
- tinydb – No sql database of choice to save information about the various running instances/applications
- Sockets – To host instances on free ports of the server machines
- nginx – To provide load balancing functionality over separate instances of the same docker app
- os module (Python) – To provide various functionalities such as fork(), terminal access on server machines, machine health, etc.

### Improvements that can be done
![image](https://user-images.githubusercontent.com/56730716/180039393-3da91e87-ae78-4274-b178-1514e3c962df.png)


