package main

import (
	"net/http"
	"strings"
	"os"
	"io"
	"log"
)

func write(w http.ResponseWriter, content string) {
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(content))
}

func writeFile(dst *os.File, src io.Reader) {
	defer dst.Close()
	_, err := io.Copy(dst, src)
	if err != nil {
		panic(err)
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		reader, err := r.MultipartReader()
		if err != nil {
			panic(err)
		}

		for {
			part, err := reader.NextPart()
			if err == io.EOF {
				break
			}
			if err != nil {
				panic(err)
			}
			if part.FileName() == "" || strings.Contains(part.FileName(), "..") {
				write(w, "filename illegal")
				return
			}

			f, err := os.Create("./" + part.FileName())
			if err != nil {
				panic(err)
			}
			log.Println("Accepting file", part.FileName())
			writeFile(f, part)
		}
	}

	content := `<form enctype="multipart/form-data" method="post" action="/">
<input type="file" name="files" multiple />
<input type="submit" value="upload"/>
</form>`

	write(w, content)
}

func main() {
	http.HandleFunc("/", uploadHandler)
	err := http.ListenAndServe(":5005", nil)
	if err != nil {
		panic(err)
	}
}