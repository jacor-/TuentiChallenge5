
import fileinput

def solve(quantity):
    return quantity/2 + (quantity-(quantity/2)*2)

inp = fileinput.input()
cases = int(inp.next()[:-1])
for case in range(cases):
    quantity = int(inp.next())
    output_result = solve(quantity)
    print output_result
