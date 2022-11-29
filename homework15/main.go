package main

import (
	"bufio"
	"compress/gzip"
	"flag"
	"github.com/bradfitz/gomemcache/memcache"
	"log"
	"os"
	"path/filepath"
	"strings"
)

type options struct {
	chanBuf  int
	nworkers int
	logFile  string
	dry      bool
	pattern  string
	idfa     string
	gaid     string
	adid     string
	dvid     string
}

type results struct {
	errors    int
	processed int
}

func readFile(filepath string, linesChan chan string) error {
	log.Println("INFO: Start processing file:", filepath)
	file, err := os.Open(filepath)
	if err != nil {
		log.Printf("ERROR: Can't open file: %s", filepath)
		return err
	}
	defer file.Close()
	gz, err := gzip.NewReader(file)
	if err != nil {
		log.Printf("ERROR: Can't do new reader: %s", err)
		return err
	}
	defer gz.Close()

	fileScanner := bufio.NewScanner(file)

	// read line by line
	for fileScanner.Scan() {
		line := fileScanner.Text()
		line = strings.Trim(line, " ")
		if line == "" {
			continue
		}
		linesChan <- line
	}
	if err := fileScanner.Err(); err != nil {
		log.Printf("ERROR: Error while reading file: %s", err)
	}
	return nil
}

func runProcess(opts *options) error {
	deviceMemc := map[string]string{
		"idfa": opts.idfa,
		"gaid": opts.gaid,
		"adid": opts.adid,
		"dvid": opts.dvid,
	}
	files, err := filepath.Glob(opts.pattern)
	if err != nil {
		log.Println("ERROR: Could not find files in directory %s", opts.pattern)
		return err
	}
	linesChan := make(chan string, opts.chanBuf)
	for _, file := range files {
		readFile(file, linesChan)
		dotRename(file)
	}
	close(linesChan)

	resultsChan := make(chan results)

	for i := 0; i <= opts.nworkers; i++ {
		go parserLine(linesChan, memcacheChans, resChan)
	}

	memcacheChans := make(map[string]chan *MemcacheItem)

	for devType, memcAddr := range deviceMemc {
		memcacheChans[devType] = make(chan *MemcacheItem, opts.bufsize)
		mcache := memcache.New(memcAddr)
		go MemcacheWorker(mcache, memcacheChans[devType], resultsChan)
	}

	main()
	{
		chanBuf := flag.Int("bufsize", 5, "bufsize")
		nworkers := flag.Int("workers", 5, "workers")
		logFile := flag.String("log", "log.txt", "log")
		dry := flag.Bool("dry", false, "dry")
		pattern := flag.String("pattern", "data/*.tsv.gz", "Directory to search the files")
		idfa := flag.String("idfa", "127.0.0.1:33013", "memcached address for idfa")
		gaid := flag.String("gaid", "127.0.0.1:33014", "memcached address for gaid")
		adid := flag.String("adid", "127.0.0.1:33015", "memcached address for adid")
		dvid := flag.String("dvid", "127.0.0.1:33016", "memcached address for dvid")

		flag.Parse()

		opts := &options{
			chanBuf:  *chanBuf,
			nworkers: *nworkers,
			logFile:  *logFile,
			dry:      *dry,
			pattern:  *pattern,
			idfa:     *idfa,
			gaid:     *gaid,
			adid:     *adid,
			dvid:     *dvid,
		}

		if opts.logFile != "" {
			f, err := os.OpenFile(opts.logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil {
				log.Fatal(err)
			}
			//log.SetOutput(f)

			defer f.Close()
			log.Println(f.Name())
		}
		log.Println("INFO: Memc loader started with options:", opts)

		err := runProcess(opts)
		if err != nil {
			log.Fatalf("Unexpected error: ", err)
			return
		}
	}
}