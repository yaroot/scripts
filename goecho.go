package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"sort"
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
	keys := make([]string, 0, len(request.Header))
	for k := range request.Header {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	for _, key := range keys {
		for _, val := range request.Header.Values(key) {
			log.Printf("->   %s: %s\n", key, val)
		}
	}
	_, err := io.Copy(writer, request.Body)
	if err != nil {
		log.Println(err)
	}
}
