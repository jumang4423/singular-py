# this program adds two numbers based on user input.
while True:
    print("lets add two numbers")
    left = input("Enter a number: ")
    right = input("Enter another number: ")

    calc_result = add(left, right)
    print("add result: " + str(calc_result))
