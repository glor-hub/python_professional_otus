package main

import (
	"bufio"
	"compress/gzip"
	"flag"
	"fmt"
	"github.com/bradfitz/gomemcache/memcache"
	"log"
	"os"
	"path/filepath"
	"strconv"
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

type appsInstalled struct {
	devType string
	devId   string
	lat     float32
	lon     float32
	apps    []uint32
}

type results struct {
	errors    int
	processed int
}

type memcacheItem struct {
	key  string
	data []byte
}

func parseAppsInstalled(line string) (*appsInstalled, error) {
	lineParts := strings.Split(line, "\t")
	if len(lineParts) < 5 {
		log.Printf("ERROR: Not all parts was found in line")
		return nil, nil
	}
	devType := lineParts[0]
	devId := lineParts[1]
	if devType == "" || devId == "" {
		log.Printf("ERROR: devType or devId was not found")
		return nil, nil
	}

	lat, err := strconv.ParseFloat(lineParts[2], 32)
	if err != nil {
		return nil, err
	}

	lon, err := strconv.ParseFloat(lineParts[3], 32)
	if err != nil {
		return nil, err
	}
	raw_apps := lineParts[4]
	apps := make([]uint32, 0)
	for _, app := range strings.Split(raw_apps, ",") {
		app_id, err := strconv.Atoi(app)
		if err != nil {
			return nil, err
		}
		apps = append(apps, uint32(app_id))
	}

	return &appsInstalled{
		devType: devType,
		devId:   devId,
		lat:     lat,
		lon:     lon,
		apps:    apps,
	}, nil
}

func packedAppsInstalled(appsInstalled *AppsInstalled) (*memcacheItem, error) {
	ua := &appsinstalled.UserApps{
		Lat:  proto.Float32(appsInstalled.lat),
		Lon:  proto.Float32(appsInstalled.lon),
		Apps: appsInstalled.apps,
	}
	key := fmt.Sprintf("%s:%s", appsInstalled.devType, appsInstalled.devId)
	packed, err := proto.Marshal(ua)
	if err != nil {
		// TODO: Log error
		return nil, err
	}
	return &MemcacheItem{key, packed}, nil
}

func memcacheStore(mcClient *memcache.Client, ItemsChan chan *memcacheItem, resultsChan chan results) {
	processed := 0
	errors := 0
	for item := range ItemsChan {
		err := mcClient.Set(&memcache.Item{
			Key:   item.key,
			Value: item.data,
		})
		if err != nil {
			errors += 1
		} else {
			processed += 1
		}
	}
	resultsChan <- results{errors, processed}
}

func dotRename(filepath string) {
	head, filename = filepath.Split(filepath)
	newfilename = filepath.Join(head, '.', filename)
	os.Rename(filename, newfilename)
}

func parserLine(linesChan chan string, memcacheChans map[string]chan *MemcacheItem, resChan chan results) {
	errors := 0
	for line := range linesChan {
		appsInstalled, err := parseAppsInstalled(line)
		if err != nil {
			errors += 1
			continue
		}
		item, err := packedAppsInstalled(appsInstalled)
		if err != nil {
			errors += 1
			continue
		}
		queue, opened := memcacheChans[appsInstalled.devType]
		if !opened {
			log.Println("ERROR: Unknown device type:", appsInstalled.devType)
			errors += 1
			continue
		}
		queue <- item
	}
	resChan <- results{errors: errors}
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

	memcacheChans := make(map[string]chan *MemcacheItem)

	for devType, memcAddr := range deviceMemc {
		memcacheChans[devType] = make(chan *MemcacheItem, opts.bufsize)
		mcache := memcache.New(memcAddr)
		go memcacheStore(mcache, memcacheChans[devType], resultsChan)
	}
	for i := 0; i <= opts.nworkers; i++ {
		go parserLine(linesChan, memcacheChans, resChan)
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
