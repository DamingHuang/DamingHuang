#Write a program that reads in the user's salary and divides the number by 12 months. 
#The monthly salary should be output to the console with 0 decimal places rounded up.
#For example, if the user enters 60000 the program should display 5000

import math


salary = input("Enter your salary: ")


salary = float(salary)
monthly_salary = salary / 12


# always round UP
monthly_salary = math.ceil(monthly_salary)


print("Your monthly salary is:", monthly_salary)
