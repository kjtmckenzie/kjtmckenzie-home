# Where to push the docker image.
REGISTRY ?= gcr.io/kjtmckenzie-home-fs
PROJECT ?= kjtmckenzie-home-fs
LOCAL_CREDENTIALS ?= `pwd`/`ls kjtmckenzie-home-fs-*`
ARTIFACT_REGION ?= us-docker.pkg.dev
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
	&& gcloud app deploy app.yaml --promote --stop-previous-version \
	&& sed -i -e 's/google-python-cloud-debugger/$(HASHMARK)google-python-cloud-debugger/' requirements.txt \
       && rm -rf requirements.txt-e

docker-build:
	cd ~/personal/kjtmckenzie-home/ \
	&& docker build -t $(REGISTRY)/$(PROJECT):latest --platform linux/amd64 .  

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
	docker tag $(REGISTRY)/$(PROJECT) $(ARTIFACT_REGION)/$(PROJECT)/$(REGISTRY):latest\
	&& docker push $(ARTIFACT_REGION)/$(PROJECT)/$(REGISTRY):latest

cloud-run-deploy:
	gcloud config set project $(PROJECT) \
	&& gcloud run deploy $(PROJECT) --image $(REGISTRY)/$(PROJECT) --platform managed --region us-central1 --update-env-vars CLOUD_RUN=True
	




