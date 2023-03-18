# fibonacci.py
# this program computes the nth Fibonacci number from user input
while True:
    print("lets compute the nth Fibonacci number")
    n = input("enter a positive integer: ")

    answer = fibonacci(int(n))
    print("the", n, "th Fibonacci number is", answer)
