## Systems Practicum

### App
Entry point is app.py that right now runs on port 4998. It is the frontend part of the website where the user
enters the docker_image path and application_id.

Now the things are sent to another flask proxy server that actually manages all the created applications right now.
Delete the application, or create a new application, everything is handled by it.
