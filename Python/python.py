print("Let's print something!")  # Basic print statement

# Single-line comment: This script demonstrates basic print functionality in Python.

"""
Multi-line comment:
This script covers examples of print statements, variables, data types, and collections in Python.
"""

# Print a string
print("hi")

# Variables and printing
name = "Variable"
age = 20
print("Name:", name)
print("Age:", age)

# Print with end parameter
print("hello", end="!!!\n")  # Prints 'hello!!!' and then a newline

# Data Types Examples

# String
my_name = "John"
print("My name is", my_name)
print("Type of my_name:", type(my_name))

# Integer
my_roll_no = 123
print("My roll number is", my_roll_no)
print("Type of my_roll_no:", type(my_roll_no))

# Float
a = 10.4
print("Float value:", a)
print("Type of a:", type(a))

# Boolean
is_true = True
print("Boolean value:", is_true)
print("Type of is_true:", type(is_true))

# List
my_list = [1, 2, 3]
print("List:", my_list)
print("Type of my_list:", type(my_list))

# Tuple
my_tuple = (1, 2, 3)
print("Tuple:", my_tuple)
print("Type of my_tuple:", type(my_tuple))

# Dictionary
my_dict = {"name": "John", "age": 30}
print("Dictionary:", my_dict)
print("Type of my_dict:", type(my_dict))

# Set
my_set = {"apple", "banana", "cherry"}
print("Set:", my_set)
print("Type of my_set:", type(my_set))

# String operations
name = "Alice"
print("Name:", name)
print("Length of name:", len(name))  # Length of the string

# List operations
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")  # Add item
fruits.remove("banana")  # Remove item
print("Updated list:", fruits)

# Dictionary operations
person = {"name": "Alice", "age": 25}
print("Value of 'name' in dictionary:", person["name"])
print("Length of dictionary:", len(person))

# Set operations
colors = {"red", "green", "blue"}
colors.add("yellow")
colors.remove("green")
print("Updated set:", colors)

# Formatted string
print(f"My name is {name} and I am {age} years old.")


# Dictionary example with basic operations

# Create a dictionary with some initial values
menu = {
    "burger": 5.99,
    "fries": 2.49,
    "soda": 1.99
}
print("Initial menu:", menu)  # Print the initial menu

# Remove an item from the dictionary
del menu["burger"]
print("Menu after removing burger:", menu)

# Add a new item to the dictionary
menu["salad"] = 4.99
print("Menu after adding salad:", menu)

# Update the price of an existing item
menu["salad"] = 5.49
print("Menu after updating salad price:", menu)

# Access the price of an item
price = menu["salad"]
print("Price of salad:", price)

# Print the length of the dictionary
print("Length of menu dictionary:", len(menu))

# Clear all items from the dictionary
menu.clear()
print("Menu after clearing:", menu)

age = input("Enter your age: ")
print("Your age is:", age)
# This code prompts the user to enter their age and then prints it.



num_1 = input("Enter first number: ")
num_2 = input("Enter second number: ")
print(int(num_1) + int(num_2))
print(num_1 + num_2)  # This will concatenate the strings
num_1 = int(input("Enter first number: "))
num_2 = int(input("Enter second number: "))

print(num_1 + num_2)  # This will concatenate the strings


"""operators are special symbols that perform operations on variables and values
5*5 = 25
Operands
1- Arithmetic operators +,-,*,/,//,%,**
2- Assignment operators =,+=,-=,*=,/=,//=,%=,**=
3- Comparison operators ==,!=,>,<,>=,<=
4- Logical operators and,or,not
5- Bitwise operators  &,|,^,~,<<,>>
6- Identity operators is,is not
7- Membership operators in,not in
"""

# Arithmetic operators
a = 20
b = 5

print(a + b)   # Addition: Adds two operands (20 + 5 = 25)
print(a - b)   # Subtraction: Subtracts right operand from left (20 - 5 = 15)
print(a * b)   # Multiplication: Multiplies two operands (20 * 5 = 100)
print(a / b)   # Division: Divides left operand by right (20 / 5 = 4.0)
print(a // b)  # Floor Division: Divides and rounds down (20 // 5 = 4)
print(a % b)   # Modulus: Returns remainder (20 % 5 = 0)
print(a ** b)  # Exponentiation: Raises left to power of right (20 ** 5 = 3200000)

# Comparison operators
x = 10
y = 20

print(x == y)   # Equal to: True if x equals y (False)
print(x != y)   # Not equal to: True if x does not equal y (True)
print(x > y)    # Greater than: True if x is greater than y (False)
print(x < y)    # Less than: True if x is less than y (True)
print(x >= y)   # Greater than or equal to: True if x >= y (False)
print(x <= y)   # Less than or equal to: True if x <= y (True)

# Assignment operators
c = 5
print(c)    # 5

c += 5      # c = c + 5 (10)
print(c)

c -= 3      # c = c - 3 (7)
print(c)

c *= 2      # c = c * 2 (14)
print(c)

c /= 4      # c = c / 4 (3.5)
print(c)

c //= 2     # c = c // 2 (1.0)
print(c)

c %= 2      # c = c % 2 (1.0)
print(c)

c **= 3     # c = c ** 3 (1.0)
print(c)

# Logical operators
p = True
q = False

print(p and q)  # and: True if both are True (False)
print(p or q)   # or: True if at least one is True (True)
print(not p)    # not: True if operand is False (False)

# Identity operators
m = [1, 2, 3]
n = [1, 2, 3]
o = m

print(m is n)      # is: True if both refer to same object (False)
print(m is o)      # is: True if both refer to same object (True)
print(m is not n)  # is not: True if not same object (True)

# Membership operators
numbers = [1, 2, 3, 4, 5]

print(3 in numbers)      # in: True if 3 is in the list (True)
print(10 not in numbers) # not in: True if 10 is not in the list (True)
print(3 not in numbers)  # not in: True if 3 is not in the list (False)

# Bitwise operators
x = 6   # 6 in binary: 110
y = 3   # 3 in binary: 011

print(x & y)   # AND: 110 & 011 = 010 (2)
print(x | y)   # OR:  110 | 011 = 111 (7)
print(x ^ y)   # XOR: 110 ^ 011 = 101 (5)
print(~x)      # NOT: ~110 = -(110 + 1) = -7
print(x << 1)  # Left shift: 110 << 1 = 1100 (12)
print(x >> 1)  # Right shift: 110 >> 1 = 011 (3)Q

# 1. if statement
num = 5
if num > 0:
    print("Number is positive")  # Output: Number is positive

# 2. if-elif statement
num = 0
if num > 0:
    print("Positive")
elif num == 0:
    print("Zero")  # Output: Zero

# 3. if-elif-else statement
num = -3
if num > 0:
    print("Positive")
elif num == 0:
    print("Zero")
else:
    print("Negative")  # Output: Negative

# 4. while loop
count = 0
while count < 3:
    print("Count is:", count)
    count += 1  # Output: 0, 1, 2

# 5. for loop
for i in range(5):
    print("Iteration:", i)  # Output: 0, 1, 2

# 6. break statement
for i in range(5):
    if i == 3:
        break  # Exits the loop when i is 3
    print("Break example:", i)  # Output: 0, 1, 2

# 7. continue statement
for i in range(5):
    if i == 2:
        continue  # Skips the rest of the loop when i is 2
    print("Continue example:", i)  # Output: 0, 1, 3, 4

# 8. pass statement
for i in range(3):
    if i == 1:
        pass  # Does nothing, placeholder
    print("Pass example:", i)  # Output: 0, 1, 2

# 9. assert statement
x = 10
assert x > 0, "x should be positive"  # No error since x > 0

# 10. return statement
def add(a, b):
    return a + b  # Returns the sum of a and b

result = add(2, 3)
print("Return example:", result)  # Output:

#MENU
menu = {
    'Pizza': 8.99,
    'Burger': 5.99,
    'Pasta': 7.49,
    'Salad': 4.99,
    'Soda': 1.99,
    'Tea': 2.49,
    'coffee': 2.99,
    'tea': 1.49,
    'juice': 3.49  
}

print("Welcome to the restaurant!")
print("Here is the menu:")
for item, price in menu.items():
    print(f"{item}: RS{price:.2f}")

# Taking user input for multiple items (comma separated)
order_total = 0.0
order_items = input("Enter the items you want to order (comma separated): ").split(',')

found_any = False
for item in order_items:
    item = item.strip()
    found = False
    for menu_item in menu:
        if item.lower() == menu_item.lower():
            order_total += menu[menu_item]
            print(f"{menu_item} added to your order. Price: RS{menu[menu_item]:.2f}")
            found = True
            found_any = True
            break
    if not found:
        print(f"Sorry, '{item}' is not on the menu.")

print("Your current order total is: RS", order_total)

anotherorder = input("Would you like to add more items to your order? (yes/no): ")
if anotherorder.lower() == 'yes':
    additional_items = input("Enter the additional items you want to order (comma separated): ").split(',')
    for item in additional_items:
        item = item.strip()
        found = False
        for menu_item in menu:
            if item.lower() == menu_item.lower():
                order_total += menu[menu_item]
                print(f"{menu_item} added to your order. Price: RS{menu[menu_item]:.2f}")
                found = True
                break
        if not found:
            print(f"Sorry, '{item}' is not on the menu.")

print("Your final order total is: RS", order_total)            

x = int(input("Enter a number: "))
y = int(input("Enter another number: "))

if x > y:
    for i in range(x, y - 1, -1):
        print(i)
else:
    for i in range(x, y + 1):
        print(i)            
        


for i in range(1,6):
    for j in range(1,6):
        print("*" ,end="")
    print()  # Output: 5 rows of 5 asterisks each

print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability
r = 5
for i in range(1, r + 1):
    for j in range(1, i + 1):
        print("*", end=" ")
    print()  # Output: Right-angled triangle of asterisks    

print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability

n = 5
for i in range(n , 0, -1):
    for j in range(i):
        print("*", end=" ")
    print()  # Output: Inverted right-angled triangle of asterisks

print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability

c = 6
for i in range(1, 6):
    for j in range(1, i + 1):
        print(j, end=" ")
    print()  # Output: Hollow square of asterisks    


d = 6
for i in range(d, 0, -1):
    for j in range(1, i + 1):
        print(j, end=" ")
    print()  # Output: Hollow inverted square of asterisks
print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability
print()  # Print a newline for better readability

e = 5
for i in range(e , 0, -1):
    for j in range(i, 0, -1):
        print(j, end=" ")
    print()  # Output: Hollow inverted right-angled triangle of asterisks


f = 9
for i in range(1, f + 1):
    for j in range(1, f + 1):
        if j == 5:
            print("*", end=" ")
        else:            
            print(" ", end=" ") 
    for j in range(1, f + 1):
        if j == 5 or j ==4 or j == 6:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()  # Output: Hollow cross pattern of asterisks        

print()  # Print a newline for better readability
print()  # Print a newline for better readability           

# Q6 - Pyramid Pattern
rows = 5
for i in range(1, rows + 1):
    print(" " * (rows - i) + "* " * i)


# Q7 - Diamond Pattern
rows = 5
# Upper part
for i in range(1, rows + 1):
    print(" " * (rows - i) + "* " * i)
# Lower part
for i in range(rows - 1, 0, -1):
    print(" " * (rows - i) + "* "* i)

# Q6 - Inverted Pyramid Pattern
dd = 5
for i in range(dd):
    stars = 2 * (dd - i) - 1
    spaces = i
    print(" " * spaces + "* " * stars)

""""
    *
   ***
  *****
 *******
********* 
"""

st = 5
for i in range(st):
    for j in range(st - i - 1):
        print(" ", end="")
    for j in range(2 * i + 1):
        print("*", end="")
    print()  # Output: Centered pyramid pattern of asterisks


# diamongrows = 5
# for i in range(1, diamongrows + 1):

diamond = 5
for i in range(1, diamond + 1):
    print(" " * (diamond - i) + "* " * i)
for i in range(diamond - 1, 0, -1):
    print(" " * (diamond - i) + "* " * i)
# Output: Diamond pattern of asterisks
print()  # Print a newline for better readability

rows = 5
for i in range(1, rows + 1):
    print(" " * (rows - i) + "* " * i)

'''
add
update
delete
view
exit
'''

Student = {
    'gopal': 100,

}

def add_student(name, marks):
    Student[name] = marks
    print(f"Student {name} added with marks {marks}.")


def update_student(name, marks):
        if name in Student:
            Student[name] = marks
            print(f"Student {name} updated with marks {marks}.")
        else:
            print(f"Student {name} not found.")

def delete_student(name):
    if name in Student:
        del Student[name]
        print(f"Student {name} deleted.")
    else:
        print(f"Student {name} not found.")

def view_students():
    if Student:
        print("Current students and their marks:")
        for name, marks in Student.items():
            print(f"{name}: {marks}")
    else:
        print("No students found.")

def main():
    while True:
        print("\nOptions:")
        print("1. Add Student")
        print("2. Update Student")
        print("3. Delete Student")
        print("4. View Students")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter student name: ")
            marks = int(input("Enter student marks: "))
            add_student(name, marks)
        elif choice == '2':
            name = input("Enter student name to update: ")
            marks = int(input("Enter new marks: "))
            update_student(name, marks)
        elif choice == '3':
            name = input("Enter student name to delete: ")
            delete_student(name)
        elif choice == '4':
            view_students()
        elif choice == '5':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice, please try again.")

main()
# This code provides a simple command-line interface to manage student records.            


file = open('shwet.doc', 'w')
file.write('Hello, World!\n')
file.write('This is a file handling example.\n')
file.write('We are writing to a file in Python.\n')
file.close()

file= open('python.txt', 'r')
content = file.read()
print(content)
file.close()


import os
os.remove('shwet.doc')
print("File 'shwet.doc' has been deleted.")
os.remove('python.txt')
os.remove("pythonn.txt")