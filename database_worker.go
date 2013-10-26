package elevator

import (
    "log"
    "sync"
)

type DatabaseWorker struct {
    Worker
    Database    *Database
}

func NewDatabaseWorker(db *Database, wg *sync.WaitGroup) *DatabaseWorker {
    name := db.Name + "-" + "dbworker"

    return &DatabaseWorker{
        Worker: *NewWorker(name, wg),
        Database: db,
    }
}

// StartRoutine listens on the Database channel awaiting
// for incoming messages to execute. Willingly
// blocking on each Exec call received through the
// channel in order to protect messages.
func (dbw *DatabaseWorker) StartRoutine() {
    for {
        select {
        case message := <-dbw.Database.Channel:
            response, err := processMessage(dbw.Database, message)
            if err == nil {
                forwardResponse(response, message)
            }
        case <- dbw.ExitChannel:
            log.Printf("Closing database channel")
            return
        }
    }
}

func (dbw *DatabaseWorker) Start() {
    log.Printf("Starting %s worker", dbw.name)
    dbw.Worker.Start()
    go dbw.StartRoutine()
}

func (dbw *DatabaseWorker) Stop() {
    log.Printf("Stopping %s worker", dbw.name)
    dbw.ExitChannel <- true
    dbw.Worker.Stop()
}
