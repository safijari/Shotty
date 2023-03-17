all:
	docker build -t shotty-tmp-docker-image .
	docker run -v $(shell pwd):/backend shotty-tmp-docker-image
	docker rmi -f shotty-tmp-docker-image