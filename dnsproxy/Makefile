
all: clean build

clean:
	rm -f dnsproxy

fmt:
	go fmt

build: fmt
	go build -o dnsproxy main.go
	strip dnsproxy


.PHONY: all clean fmt build

