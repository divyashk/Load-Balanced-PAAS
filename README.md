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

