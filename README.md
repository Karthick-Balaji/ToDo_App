# ToDo_App

This is a python based ToDo Application that provides APIs to handle tasks.

## End Points
* `/login` POST API that takes `email` and `password` as payload and gives a `JWT token` as response. This should be passed as Authorization in headers for other APIs. For testing, use `test@test.com`, `test123` as email and password respectively.
* `/addTask` POST API that takes `task` and `priority` as mandatory payload data and `dueDate` as option.
* `/editTask` POST API that takes `taskID, description, dueDate` and `priorityID`as payload data. `taskID` is mandatory.
* `/completeTask` POST API where taskID is given as a parameter. This API toggles between Completed and Active statuses.
* `/cancelTask` POST API where taskID is given as a parameter. This API toggles between Cancelled and Active statuses.
* `/getAllTasks` GET API to list all tasks. Optional parameters are `dueDateBreached` , `priorityID` and `sortBy`.
  - `dueDateBreached` Boolean parameter to filter tasks for which the due date is breached.
  - `priorityID` this takes either `1,2 or 3` for `High, Medium or Low` to filter based on priority.
  - `sortBy` to sort based on `dueDate` or `priority`.
