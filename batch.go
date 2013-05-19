package elevator


type BatchOperations []BatchOperation

type BatchOperation struct {
    OpCode string
    OpArgs []string
}

// NewBatchOperation builds a BatchOperation from batch operation
// code and batch operation args
func NewBatchOperation(op_code string, op_args []string) *BatchOperation {
    return &BatchOperation{
        OpCode: op_code,
        OpArgs: op_args,
    }
}

// BatchOperationFromSlice builds a BatchOperation from
// a string slice containing the batch operation code and
// arguments
func BatchOperationFromSlice(slice []string) *BatchOperation {
    return NewBatchOperation(slice[0], slice[1:])
}

// BatchOperationsFromRequestArgs builds a BatchOperations from
// a string slice resprensenting a sequence of batch operations
func BatchOperationsFromRequestArgs(args []string) *BatchOperations {
    var ops BatchOperations
    var cur_index int = 0
    var last_index int = 0

    for index, elem := range args {
        cur_index = index
        if index > 0 {
            if elem == SIGNAL_BATCH_PUT || elem == SIGNAL_BATCH_DELETE {
                ops = append(ops, *BatchOperationFromSlice(args[last_index:index]))
                last_index = index
            }
        }
    }

    // Add the rest
    if cur_index > 0 {
        ops = append(ops, *BatchOperationFromSlice(args[last_index : cur_index+1]))
    }

    return &ops
}
