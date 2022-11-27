package main

import (
	"flag"
	"log"
	"os"
)

type options struct {
	logFile string
	dry     bool
	pattern string
	idfa    string
	gaid    string
	adid    string
	dvid    string
}

func main() {

	logFile := flag.String("log", "log.txt", "log")
	dry := flag.Bool("dry", false, "dry")
	pattern := flag.String("pattern", "data/*.tsv.gz", "Directory to search the files")
	idfa := flag.String("idfa", "127.0.0.1:33013", "memcached address for idfa")
	gaid := flag.String("gaid", "127.0.0.1:33014", "memcached address for gaid")
	adid := flag.String("adid", "127.0.0.1:33015", "memcached address for adid")
	dvid := flag.String("dvid", "127.0.0.1:33016", "memcached address for dvid")

	flag.Parse()

	opts := options{
		logFile: *logFile,
		dry:     *dry,
		pattern: *pattern,
		idfa:    *idfa,
		gaid:    *gaid,
		adid:    *adid,
		dvid:    *dvid,
	}

	if opts.logFile != "" {
		f, err := os.OpenFile(opts.logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		log.SetOutput(f)

		defer f.Close()
		log.Println(f.Name())
	}
}
