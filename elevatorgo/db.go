package main

import (
	// "log"
	"fmt"
	"io/ioutil"

	json 	"encoding/json"
	leveldb "code.google.com/p/leveldb-go/leveldb/db"
)

type DbOptions struct {
    Create_if_missing 	bool
    Error_if_exists		bool
    Bloom_filter_bits	int
    Paranoid_checks		bool
    Lru_cache_size		int
    Write_buffer_size	int
    Block_size			int
    Max_open_files		int
}

type Db struct {
	Name				string		`json:"-"`
	Uid 				string 		`json:"uid"`
	Path				string 		`json:"path"`
	Status				int  		`json:"-"`
	Connector 			leveldb 	`json:"-"`
	// options				DbOptions
}

type DbStore struct {
	FilePath			string
	NameToUid 			map[string]string
	Container			map[string]Db
}


func NewDbStore(filepath string) (*DbStore) {
	return &DbStore{
		FilePath: filepath,
		NameToUid: make(map[string]string),
		Container: make(map[string]Db),
	}
}


func (db *Db) mount() (error) {
	if db.Status == DB_STATUS_UNMOUNTED {
		options = leveldb.Options
		db.Connector, err = leveldb.Open(db.Name, options)
		if err != nil { return err }

		db.Status = DB_STATUS_MOUNTED
	} else {
		return error.New("Database already mounted")
	}

	return nil
}

func (store *DbStore) ReadFromFile() (err error) {
	data, err := ioutil.ReadFile(store.FilePath)
	if err != nil { return err }

	err = json.Unmarshal(data, &store.Container)
	if err != nil { return err }

	return nil
}


func (store *DbStore) WriteToFile() (err error) {
	var data []byte
	
	data, err = json.Marshal(store.Container)
	if err != nil { return err }

	err = ioutil.WriteFile(store.FilePath, data, 0777)
	if err != nil { return err }

	return nil
}


func (store *DbStore) load() (err error) {
	err = store.ReadFromFile()
	if err != nil { return err }

	for k, v := range store.Container {
		store.NameToUid[k] = v.Uid
	}

	return nil
}

func (store *DbStore) mount() {}

func (store *DbStore) unmount() {}

func (store *DbStore) add() {}

func (store *DbStore) drop() {}

func (store *DbStore) status() {}


func (store *DbStore) exists(db_name string) (bool, error) {
	if _,ok := store.Container[db_name]; ok {
		exists, err := DirExists(store.Container[db_name].Path)
		if err != nil { return false, err}

		if exists == true {
			return exists, nil
		} else {
			// store.drop(db_name)
			fmt.Println("Dropping")
		}
	}

	return false, nil
}


func (store *DbStore) list() ([]string) {
	db_names := make([]string, len(store.NameToUid))

	i := 0
	for k, _ := range store.NameToUid {
		db_names[i] = k
		i++
	}

	return db_names
}

func main() {
	db := Db {
		Name: "default",
		Path: "/var/lib/elevator/default",
		Status: DB_STATUS_UNMOUNTED,
	}
	// store := NewDbStore("/tmp/test.json")
	// store.load()
	
	// fmt.Println(store.list())
	// exists, err := store.exists("default")
	// if err != nil { log.Fatal(err) }

	// fmt.Println(exists)
	// err := store.update(db)
	// if err != nil { log.Fatal(err) }

}