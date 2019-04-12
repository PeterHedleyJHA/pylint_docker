FROM tiangolo/uwsgi-nginx-flask:python3.7

# copy over our requirements.txt file
COPY requirements.txt /tmp/

# upgrade pip and install required python packages
RUN pip3 install -r /tmp/requirements.txt


# copy over our app code
COPY ./app /app
#RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/common.conf

# set an environmental variable, MESSAGE,
# which the app will use and display
ENV MESSAGE "hello from Docker"
