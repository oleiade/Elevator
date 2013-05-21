package elevator

import (
	goconfig "github.com/msbranco/goconfig"
	"reflect"
)

type Config struct {
	Core 		*CoreConfig
	Storage 	*StorageConfig
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

type StorageConfig struct {
	Compression 	bool 	`ini:"compression"`  		// default: true
	BlockSize 		int 	`ini:"block_size"` 		// default: 4096
	CacheSize 		int     `ini:"cache_size"` 		// default: 128 * 1048576 (128MB)
	BloomFilterBits int 	`ini:"bloom_filter_bits"`	// default: 100
	MaxOpenFiles 	int 	`ini:"max_open_files"`		// default: 150
	VerifyChecksums	bool 	`ini:"verify_checksums"` 	// default: false
	WriteBufferSize int 	`ini:"write_buffer_size"` 	// default: 64 * 1048576 (64MB)
}

func NewConfig() *CoreConfig {
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

func (c *Config) FromFile(path string) error {
	c.Core = new(CoreConfig)
	err := loadConfigFromFile(path, c.Core, "core")
	if err != nil {
		return err
	}

	c.Storage = new(StorageConfig)
	err = loadConfigFromFile(path, c.Storage, "storage_engine")
	if err != nil {
		return err
	}

	return nil
}

func loadConfigFromFile(path string, obj interface{}, section string) error {
	ini_config, err := goconfig.ReadConfigFile(path)
	if err != nil {
		return err
	}

	config := reflect.ValueOf(obj).Elem()
	config_type := config.Type()

	for i := 0; i < config.NumField(); i++ {
		struct_field := config.Field(i)
		field_tag := config_type.Field(i).Tag.Get("ini")

		switch {
		case struct_field.Type().Kind() == reflect.Bool:
			config_value, err := ini_config.GetBool(section, field_tag)
			if err == nil {
				struct_field.SetBool(config_value)
			}
		case struct_field.Type().Kind() == reflect.String:
			config_value, err := ini_config.GetString(section, field_tag)
			if err == nil {
				struct_field.SetString(config_value)
			}
		case struct_field.Type().Kind() == reflect.Int:
			config_value, err := ini_config.GetInt64(section, field_tag)
			if err == nil {
				struct_field.SetInt(config_value)
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
