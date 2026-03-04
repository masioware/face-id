FROM nginx:latest

COPY /frontend/index.html /usr/share/nginx/html/index.html
COPY /frontend/enroll.html /usr/share/nginx/html/enroll.html
COPY /frontend/styles.css /usr/share/nginx/html/styles.css

EXPOSE 80