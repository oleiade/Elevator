package main

import (
	"log"
	"errors"
	"fmt"
	leveldb "github.com/jmhodges/levigo"
)

type Db struct {
	Name				string		`json:"-"`
	Uid 				string 		`json:"uid"`
	Path				string 		`json:"path"`
	Status				int  		`json:"-"`
	Connector 			*leveldb.DB	`json:"-"`
}


// Mount sets the database status to DB_STATUS_MOUNTED
// and instantiates the according leveldb connector
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

// Unmount sets the database status to DB_STATUS_UNMOUNTED
// and deletes the according leveldb connector
func (db *Db) Unmount() (err error) {
	if db.Status == DB_STATUS_MOUNTED {
		db.Status = DB_STATUS_UNMOUNTED
		db.Connector = nil
	} else {
		return errors.New("Database already unmounted")
	}

	return nil
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


}