build-and-publish:
	sudo podman build -t test_build .
	sudo podman tag test_build ghcr.io/kyrluckechuck/spotify-library-manager:latest
	sudo podman push ghcr.io/kyrluckechuck/spotify-library-manager:latest
