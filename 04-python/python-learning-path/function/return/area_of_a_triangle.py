#Write a Python program that calculates the area of two different triangles and finds their combined total.

def area_triangle(base, height):
    return base*height/2


area_a = area_triangle(5,4)
#print("Check area_a  " + str(area_a ))


area_b = area_triangle(30,3)
#print("Check area_b  " + str(area_b ))
total_area = area_a + area_b
print("The sum of both areas is: " + str(total_area))
