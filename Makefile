.PHONY: install test lint dist update publish promote
SHELL=/bin/bash
ECR_REGISTRY=222053980223.dkr.ecr.us-east-1.amazonaws.com
DATETIME:=$(shell date -u +%Y%m%dT%H%M%SZ)

help: ## Print this message
	@awk 'BEGIN { FS = ":.*##"; print "Usage:  make <target>\n\nTargets:" } \
/^[-_[:alpha:]]+:.?*##/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install script and dependencies
	pipenv install --dev

test: ## Run tests and print a coverage report
	pipenv run coverage run --source=harvester -m pytest
	pipenv run coverage report -m

coveralls: test
	pipenv run coverage lcov -o ./coverage/lcov.info

### Linting commands ###
lint: bandit black flake8 isort mypy ## Lint the repo

bandit:
	pipenv run bandit -r harvester

black:
	pipenv run black --check --diff .

flake8:
	pipenv run flake8 .

isort:
	pipenv run isort . --diff

mypy:
	pipenv run mypy harvester

update: install ## Update all Python dependencies
	pipenv clean
	pipenv update --dev

### Docker commands ###
dist-dev: ## Build docker image
	docker build --platform linux/amd64 -t $(ECR_REGISTRY)/timdex-oaiharvester-dev:latest \
		-t $(ECR_REGISTRY)/timdex-oaiharvester-dev:`git describe --always` \
		-t oaiharvester:latest .

publish-dev: dist-dev ## Build, tag and push
	docker login -u AWS -p $$(aws ecr get-login-password --region us-east-1) $(ECR_REGISTRY)
	docker push $(ECR_REGISTRY)/timdex-oaiharvester-dev:latest
	docker push $(ECR_REGISTRY)/timdex-oaiharvester-dev:`git describe --always`
