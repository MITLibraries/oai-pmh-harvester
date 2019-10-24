.PHONY: install dist update publish promote
SHELL=/bin/bash
ECR_REGISTRY=672626379771.dkr.ecr.us-east-1.amazonaws.com
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)


help: ## Print this message
	@awk 'BEGIN { FS = ":.*##"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*##/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:
	pipenv install

dist: ## Build docker container
	docker build -t $(ECR_REGISTRY)/oaiharvester-stage:latest \
		-t $(ECR_REGISTRY)/oaiharvester-stage:`git describe --always` \
		-t oaiharvester .

update: install ## Update all Python dependencies
	pipenv clean
	pipenv update --dev

publish: ## Push and tag the latest image (use `make dist && make publish`)
	$$(aws ecr get-login --no-include-email --region us-east-1)
	docker push $(ECR_REGISTRY)/oaiharvester-stage:latest
	docker push $(ECR_REGISTRY)/oaiharvester-stage:`git describe --always`

promote: ## Promote the current staging build to production
	$$(aws ecr get-login --no-include-email --region us-east-1)
	docker pull $(ECR_REGISTRY)/oaiharvester-stage:latest
	docker tag $(ECR_REGISTRY)/oaiharvester-stage:latest $(ECR_REGISTRY)/oaiharvester-prod:latest
	docker tag $(ECR_REGISTRY)/oaiharvester-stage:latest $(ECR_REGISTRY)/oaiharvester-prod:$(DATETIME)
	docker push $(ECR_REGISTRY)/oaiharvester-prod:latest
	docker push $(ECR_REGISTRY)/oaiharvester-prod:$(DATETIME)
