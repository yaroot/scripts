package main

import (
	"errors"
	"flag"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strings"
)

func postTo(zurl, auth, to, subject, content string) error {
	form := make(url.Values)
	form.Add("type", "stream")
	form.Add("to", to)
	form.Add("subject", subject)
	form.Add("content", content)
	req, err := http.NewRequest("POST", zurl, strings.NewReader(form.Encode()))
	if err != nil {
		return err
	}
	authz := strings.Split(auth, ":")
	req.SetBasicAuth(authz[0], authz[1])
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	r, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	resp, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return err
	}
	log.Printf("Responed %d %s", r.StatusCode, string(resp))
	return nil
}

func main() {
	bind := flag.String("bind", "0.0.0.0:8000", "listening address")
	zurl := flag.String("zulip_url", "", "eg. example.zulip.com/api/v1/messages")
	auth := flag.String("auth", "", "user:password")
	defaultTo := flag.String("to", "bot", "default channel")
	defaultSubject := flag.String("subject", "uncategorized", "default subject")
	flag.Parse()

	authz := strings.Split(*auth, ":")
	if len(authz) != 2 {
		panic(errors.New("invalid auth input"))
	}

	http.DefaultServeMux.HandleFunc("/post", func(w http.ResponseWriter, r *http.Request) {
		err := r.ParseForm()
		if err != nil {
			log.Println(err.Error())
			w.WriteHeader(400)
			return
		}
		to := r.Form.Get("to")
		subject := r.Form.Get("subject")
		content := r.Form.Get("content")
		if content == "" {
			w.WriteHeader(400)
			return
		}

		if to == "" {
			to = *defaultTo
		}
		if subject == "" {
			subject = *defaultSubject
		}

		log.Printf("Sending to '%s' '%s': %s\n", to, subject, content)

		err = postTo(*zurl, *auth, to, subject, content)
		if err != nil {
			log.Printf("Error: %s\n", err.Error())
			w.WriteHeader(500)
		} else {
			w.WriteHeader(200)
		}
	})

	err := http.ListenAndServe(*bind, nil)
	if err != nil {
		panic(err)
	}
}

// TODO CF-Connecting-IP
