.PHONY: container
container: ## Builds container image with Python reqs
	docker build -t jams .

run: ## Invokes REPL on jams.py via ipython
	docker run \
		--device /dev/snd \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v $$PWD/assets:/code/assets \
		-e DISPLAY \
		-it jams
