# Where to push the docker image.
REGISTRY ?= gcr.io/kjtmckenzie-home-fs
PROJECT ?= kjtmckenzie-home-fs
LOCAL_CREDENTIALS ?= `pwd`/kjtmckenzie-home-fs-e95cb6b832bf.json
HASHMARK = \#
PORT ?= 8080
DEV_FLASK_SECRET ?= `cat dev_flask_secret.txt`


.PHONY: rebuild-local local app-engine-deploy docker-build docker-run docker-push cloud-run-deploy

rebuild-local:
	cd ~/personal/kjtmckenzie-home/ \
	&& rm -rf env \
	&& virtualenv -p python3 env \
	&& source env/bin/activate \
	&& pip install -r requirements.txt

local: 
	cd ~/personal/kjtmckenzie-home/ \
	&& source env/bin/activate \
	&& export GOOGLE_APPLICATION_CREDENTIALS=$(LOCAL_CREDENTIALS) \
	&& python main.py

app-engine-deploy: 
	cd ~/personal/kjtmckenzie-home/ \
	&& sed -i -e 's/#google-python-cloud-debugger/google-python-cloud-debugger/' requirements.txt \
	&& gcloud app deploy \
	&& sed -i -e 's/google-python-cloud-debugger/$(HASHMARK)google-python-cloud-debugger/' requirements.txt \
       && rm -rf requirements.txt-e

docker-build:
	cd ~/personal/kjtmckenzie-home/ \
	&& docker build -t $(REGISTRY)/$(PROJECT):latest .  

docker-run:
	cd ~/personal/kjtmckenzie-home/ \
	&& export GOOGLE_APPLICATION_CREDENTIALS=$(LOCAL_CREDENTIALS) \
	&& DEV_FLASK_SECRET=`cat dev_flask_secret.txt` \
	&& PORT=8080 && docker run \
		-p 8080:${PORT} \
		-e PORT=${PORT} \
		-e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/$(LOCAL_CREDENTIALS) \
		-e DEV_FLASK_SECRET=${DEV_FLASK_SECRET} \
		-v ${LOCAL_CREDENTIALS}:/tmp/keys/$(LOCAL_CREDENTIALS):ro \
		$(REGISTRY)/$(PROJECT)

docker-push:
	docker push $(REGISTRY)/$(PROJECT):latest

cloud-run-deploy:
	gcloud beta run deploy $(PROJECT) --image $(REGISTRY)/$(PROJECT) --update-env-vars CLOUD_RUN=True
	




