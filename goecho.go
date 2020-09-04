package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
)

func main() {
	var port int64
	port = 8000

	if len(os.Args) == 2 {
		port, _ = strconv.ParseInt(os.Args[1], 10, 32)
	}

	log.Println("Listening on", port)
	panic(http.ListenAndServe(fmt.Sprintf(":%d", port), handler{}))
}

type handler struct {
}

func (h handler) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	log.Printf("=> %s %s", request.Method, request.URL)
	for key, vals := range request.Header {
		for _, val := range vals {
			log.Printf("->   %s: %s\n", key, val)
		}
	}
	_, err := io.Copy(writer, request.Body)
	if err != nil {
		log.Println(err)
	}
}
