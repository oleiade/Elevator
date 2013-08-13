package elevator

import (
	"reflect"
	goconfig "github.com/msbranco/goconfig"
	leveldb "github.com/jmhodges/levigo"
)

type Config struct {
	Core 		*CoreConfig
	Storage 	*StorageEngineConfig
}

type CoreConfig struct {
	Daemon      bool   `ini:"daemonize"`
	Endpoint    string `ini:"endpoint"`
	Pidfile     string `ini:"pidfile"`
	StorePath   string `ini:"database_store"`
	StoragePath string `ini:"databases_storage_path"`
	DefaultDb   string `ini:"default_db"`
	LogFile     string `ini:"log_file"`
	LogLevel    string `ini:"log_level"`
}

type StorageEngineConfig struct {
	Compression 	bool 	`ini:"compression"`  		// default: true
	BlockSize 		int 	`ini:"block_size"` 			// default: 4096
	CacheSize 		int     `ini:"cache_size"` 			// default: 128 * 1048576 (128MB)
	BloomFilterBits int 	`ini:"bloom_filter_bits"`	// default: 100
	MaxOpenFiles 	int 	`ini:"max_open_files"`		// default: 150
	VerifyChecksums	bool 	`ini:"verify_checksums"` 	// default: false
	WriteBufferSize int 	`ini:"write_buffer_size"` 	// default: 64 * 1048576 (64MB)
}

func NewConfig() *Config {
	return &Config{
		Core: NewCoreConfig(),
		Storage: NewStorageEngineConfig(),
	}
}

func NewCoreConfig() *CoreConfig {
	return &CoreConfig{
		Daemon:      false,
		Endpoint:    "tcp://127.0.0.1:4141",
		Pidfile:     "/var/run/elevator.pid",
		StorePath:   "/var/lib/elevator/store",
		StoragePath: "/var/lib/elevator",
		DefaultDb:   "default",
		LogFile:     "/var/log/elevator.log",
		LogLevel:    "INFO",
	}
}

func NewStorageEngineConfig() *StorageEngineConfig {
	return &StorageEngineConfig{
		Compression: true,
		BlockSize: 4096,
		CacheSize: 512 * 1048576,
		BloomFilterBits: 100,
		MaxOpenFiles: 150,
		VerifyChecksums: false,
		WriteBufferSize: 64 * 1048576,
	}
}

func (opts *StorageEngineConfig) ToLeveldbOptions() *leveldb.Options {
	options := leveldb.NewOptions()

	options.SetCreateIfMissing(true)
	options.SetCompression(leveldb.CompressionOpt(Btoi(opts.Compression)))
	options.SetBlockSize(opts.BlockSize)
	options.SetCache(leveldb.NewLRUCache(opts.CacheSize))
	options.SetFilterPolicy(leveldb.NewBloomFilter(opts.BloomFilterBits))
	options.SetMaxOpenFiles(opts.MaxOpenFiles)
	options.SetParanoidChecks(opts.VerifyChecksums)
	options.SetWriteBufferSize(opts.WriteBufferSize)

	return options
}

func (opts *StorageEngineConfig) UpdateFromConfig(config *Config) {
	opts.Compression = config.Storage.Compression
	opts.BlockSize = config.Storage.BlockSize
	opts.CacheSize = config.Storage.CacheSize
	opts.BloomFilterBits = config.Storage.BloomFilterBits
	opts.MaxOpenFiles = config.Storage.MaxOpenFiles
	opts.VerifyChecksums = config.Storage.VerifyChecksums
	opts.WriteBufferSize = config.Storage.WriteBufferSize
}

func (c *Config) FromFile(path string) error {
	err := loadConfigFromFile(path, c.Core, "core")
	if err != nil {
		return err
	}

	err = loadConfigFromFile(path, c.Storage, "storage_engine")
	if err != nil {
		return err
	}

	return nil
}

func loadConfigFromFile(path string, obj interface{}, section string) error {
	iniConfig, err := goconfig.ReadConfigFile(path)
	if err != nil {
		return err
	}

	config := reflect.ValueOf(obj).Elem()
	configType := config.Type()

	for i := 0; i < config.NumField(); i++ {
		structField := config.Field(i)
		fieldTag := configType.Field(i).Tag.Get("ini")

		switch {
		case structField.Type().Kind() == reflect.Bool:
			configValue, err := iniConfig.GetBool(section, fieldTag)
			if err == nil {
				structField.SetBool(configValue)
			}
		case structField.Type().Kind() == reflect.String:
			configValue, err := iniConfig.GetString(section, fieldTag)
			if err == nil {
				structField.SetString(configValue)
			}
		case structField.Type().Kind() == reflect.Int:
			configValue, err := iniConfig.GetInt64(section, fieldTag)
			if err == nil {
				structField.SetInt(configValue)
			}
		}
	}

	return nil
}

// A bit verbose, and not that dry, but could not find
// more clever for now.
func (c *CoreConfig) UpdateFromCmdline(cmdline *Cmdline) {
	if *cmdline.DaemonMode != DEFAULT_DAEMON_MODE {
		c.Daemon = *cmdline.DaemonMode
	}

	if *cmdline.Endpoint != DEFAULT_ENDPOINT {
		c.Endpoint = *cmdline.Endpoint
	}

	if *cmdline.LogLevel != DEFAULT_LOG_LEVEL {
		c.LogLevel = *cmdline.LogLevel
	}
}
