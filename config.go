package elevator

import (
	"fmt"
	"reflect"
	goconfig "github.com/msbranco/goconfig"
)

type Config struct {
	Daemon			bool	`ini:"daemonize"`
	Port 			int		`ini:"port"`
	Endpoint		string	`ini:"endpoint"`
	Pidfile			string	`ini:"pidfile"`
	StorePath		string	`ini:"database_store_path"`
	StoragePath		string	`ini:"databases_storage_path"`
	DefaultDb		string	`ini:"default_db"`
	ActivityLog		string	`ini:"activity_log"`
	ErrorsLog		string	`ini:"errors_log"`
	Unixsocket		string	`ini:"unixsocket"`
}

func NewConfig() *Config {
	return &Config{
		Daemon: false,
		Port: 4141,
		Endpoint: "tcp://127.0.0.1",
		Pidfile: "/var/run/elevator.pid",
		StorePath: "/var/lib/elevator/store",
		StoragePath: "/var/lib/elevator",
		DefaultDb: "sandbox",
		ActivityLog: "/var/log/elevator/activity.log",
		ErrorsLog: "/var/log/elevator/errors.log",
		Unixsocket: "",
	}
}

func (c *Config) FromFile(filepath string) error {
	config, err := goconfig.ReadConfigFile(filepath)
	if err != nil { return err }

	indexslice := []int{0}
	fields_count := reflect.TypeOf(c).Elem().NumField()

	for i := 0; i < fields_count; i++ {
		indexslice[0] = i
		field := reflect.TypeOf(c).Elem().FieldByIndex(indexslice)
		field_value := reflect.ValueOf(&field)

		switch {
		case field.Type.Kind() == reflect.Bool:
			config_value, err := config.GetBool("core", field.Tag.Get("ini"))
			fmt.Println(config_value)
			

			if err == nil {
				field_value.SetBool(config_value)
			}
		case field.Type.Kind() == reflect.Int64:
			config_value, err := config.GetInt64("core", field.Tag.Get("ini"))
			fmt.Println(config_value)
			if err == nil { 
				field_value.SetInt(config_value)
			}
		case field.Type.Kind() == reflect.String:
			config_value, err := config.GetString("core", field.Tag.Get("ini"))
			fmt.Println(config_value)
			fmt.Println(reflect.TypeOf(config_value))
			if err == nil {
				field_value.Elem().SetString(config_value)
			}
		}
	}

	return nil
}