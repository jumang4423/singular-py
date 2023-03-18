# this program is for showing todo, adding todo or deleting todo
todos = []

while True:
    print("here is current todo list:")
    show_todo(todos)

    print("a to add todo, r to remove todo, q to quit")
    choice = input("what do you want to do? ")
    if choice == "a":
        add_todo(todos)
    elif choice == "r":
        remove_todo(todos)
    else:
        break
