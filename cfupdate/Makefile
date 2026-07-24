.PHONY: all
all:
	CGO_ENABLED=0 go build -o ./bin/cfupdate .
	GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o ./bin/cfupdate-linux-amd64 .
