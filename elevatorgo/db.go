package main

import (
	"log"
	"errors"
	"fmt"
	"io/ioutil"

	json 	"encoding/json"
	leveldb "github.com/jmhodges/levigo"
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
	Connector 			*leveldb.DB	`json:"-"`
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


func (db *Db) Mount() (err error) {
	if db.Status == DB_STATUS_UNMOUNTED {
		opts := leveldb.NewOptions()
		opts.SetCache(leveldb.NewLRUCache(512))
		opts.SetCreateIfMissing(true)
		
		db.Connector, err = leveldb.Open(db.Name, opts)
		if err != nil { return err }

		db.Status = DB_STATUS_MOUNTED
	} else {
		return errors.New("Database already mounted")
	}

	return nil
}


func (db *Db) Unmount() (err error) {
	if db.Status == DB_STATUS_MOUNTED {
		db.Status = DB_STATUS_UNMOUNTED
		db.Connector = nil
	} else {
		return errors.New("Database already unmounted")
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


func (store *DbStore) Load() (err error) {
	err = store.ReadFromFile()
	if err != nil { return err }

	for k, v := range store.Container {
		store.NameToUid[k] = v.Uid
	}

	return nil
}

func (store *DbStore) Mount() {}

func (store *DbStore) Unmount() {}

func (store *DbStore) Add() {}

func (store *DbStore) Drop() {}

func (store *DbStore) Status() {}


func (store *DbStore) Exists(db_name string) (bool, error) {
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


func (store *DbStore) List() ([]string) {
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
	db.Mount()

	ro := leveldb.NewReadOptions()
	wo := leveldb.NewWriteOptions()

	db.Connector.Put(wo, []byte("1"), []byte("a"))
	data, err := db.Connector.Get(ro, []byte("1"))
	if err != nil { log.Fatal(err) }

	fmt.Println(string(data))
	fmt.Println(db.Status)

	db.Unmount()
	// store := NewDbStore("/tmp/test.json")
	// store.load()
	
	// fmt.Println(store.list())
	// exists, err := store.exists("default")
	// if err != nil { log.Fatal(err) }

	// fmt.Println(exists)
	// err := store.update(db)
	// if err != nil { log.Fatal(err) }

}