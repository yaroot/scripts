package main

import (
	"fmt"
	"github.com/cheggaaa/pb/v3"
	"github.com/spf13/cobra"
	"github.com/xanzy/go-gitlab"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/user"
	"path"
	"strconv"
	"strings"
	"text/tabwriter"
	"time"
)

func lerror(err error) {
	if err != nil {
		log.Println(err.Error())
		os.Exit(-1)
	}
}

func fmtTime(t *time.Time) string {
	return t.Format(time.RFC3339)
}

func main() {
	privateToken := readToken()
	client, err := gitlab.NewClient(privateToken)
	if err != nil {
		lerror(err)
	}
	cmd := &cobra.Command{
		Use:  "gl",
		Long: "\n Access token: use `GITLAB_TOKEN` or $HOME/.gitlab_token",
	}

	ci := &cobra.Command{Use: "ci"}
	cmd.AddCommand(ci)

	ci.AddCommand(&cobra.Command{
		Use:     "ls <user/repo>",
		Aliases: []string{"list"},
		Args:    cobra.ExactArgs(1),
		Run: func(_ *cobra.Command, args []string) {
			repo := args[0]
			jobs, response, err := client.Jobs.ListProjectJobs(repo, nil)
			lerror(err)
			log.Printf("%+v\n", response)

			w := new(tabwriter.Writer)
			w.Init(os.Stdout, 8, 8, 0, '\t', 0)
			defer w.Flush()

			fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n", "status", "job-id", "name", "pipeline", "created-at", "dura", "ref")

			for _, job := range jobs {
				_, err = fmt.Fprintf(
					w,
					"%s\t%d\t%s\t%d\t%s\t%s\t%s\t\n",
					strings.ToUpper(job.Status),
					job.ID,
					job.Name,
					job.Pipeline.ID,
					fmtTime(job.CreatedAt),
					time.Duration(job.Duration)*time.Second,
					job.Ref,
				)
				if err != nil {
					panic(err)
				}
			}
		},
	})

	ci.AddCommand(&cobra.Command{
		Use:     "download <user/repo> <Job ID>",
		Aliases: []string{"d", "dl"},
		Args:    cobra.ExactArgs(2),
		Run: func(_ *cobra.Command, args []string) {
			repo := args[0]
			jobId, err := strconv.ParseInt(args[1], 10, 32)
			lerror(err)

			localFileName := fmt.Sprintf("artifacts-%s-%d.zip", strings.ReplaceAll(repo, "/", "-"), jobId)
			downloadUrl := fmt.Sprintf("https://gitlab.com/api/v4/projects/%s/jobs/%d/artifacts", url.PathEscape(repo), jobId)
			req, err := http.NewRequest("GET", downloadUrl, nil)
			lerror(err)
			req.Header.Add("PRIVATE-TOKEN", privateToken)
			resp, err := http.DefaultClient.Do(req)
			lerror(err)
			if resp.StatusCode != 200 {
				fmt.Printf("Download error %s: %d\n", downloadUrl, resp.StatusCode)
				return
			}

			fmt.Printf("Saving artifacts to %s\n", localFileName)
			localFile, err := os.Create(localFileName)
			lerror(err)
			defer localFile.Close()
			bar := pb.Full.Start64(resp.ContentLength)
			barReader := bar.NewProxyReader(resp.Body)
			_, err = io.Copy(localFile, barReader)
			lerror(err)
			bar.Finish()
		},
	})

	ci.AddCommand(&cobra.Command{
		Use:  "keep <user/repo> <Job ID>",
		Args: cobra.ExactArgs(2),
		Run: func(_ *cobra.Command, args []string) {
			repo := args[0]
			jobId, err := strconv.ParseInt(args[1], 10, 32)
			lerror(err)
			_, _, err = client.Jobs.KeepArtifacts(repo, int(jobId))
			lerror(err)
		},
	})

	//ci.AddCommand(&cobra.Command{
	//	Use:  "cat <user/repo> <Job ID>",
	//	Args: cobra.ExactArgs(2),
	//	Run: func(_ *cobra.Command, args []string) {
	//		repo := args[0]
	//		jobId, err := strconv.ParseInt(args[1], 10, 32)
	//		lerror(err)
	//		//https://gitlab.com/pasotan/jisaku/-/jobs/1574016564/raw
	//		logUrl := fmt.Sprintf("https://gitlab.com/%s/-/jobs/%d/raw", repo, jobId)
	//		println(logUrl)
	//		req, err := http.NewRequest("GET", logUrl, nil)
	//		lerror(err)
	//		req.Header.Add("PRIVATE-TOKEN", privateToken)
	//		resp, err := http.DefaultClient.Do(req)
	//		lerror(err)
	//		if resp.StatusCode != 200 {
	//			fmt.Printf("Download error %s: %d\n", logUrl, resp.StatusCode)
	//			return
	//		}
	//		localFileName := fmt.Sprintf("job-%s-%d.log", strings.ReplaceAll(repo, "/", "-"), jobId)
	//		fmt.Printf("Saving artifacts to %s\n", localFileName)
	//		localFile, err := os.Create(localFileName)
	//		lerror(err)
	//		defer localFile.Close()
	//		bar := pb.Full.Start64(resp.ContentLength)
	//		barReader := bar.NewProxyReader(resp.Body)
	//		_, err = io.Copy(localFile, barReader)
	//		lerror(err)
	//		bar.Finish()
	//	},
	//})

	err = cmd.Execute()
	lerror(err)
}

func readToken() string {
	token := os.Getenv("GITLAB_TOKEN")
	if len(token) > 0 {
		return token
	}
	u, err := user.Current()
	lerror(err)
	content, err := ioutil.ReadFile(path.Join(u.HomeDir, ".gitlab_token"))
	lerror(err)
	return strings.TrimSpace(string(content))
}
