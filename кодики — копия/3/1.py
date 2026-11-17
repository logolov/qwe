def get_divisors(n):
    divisors = set()
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divisors.add(i)
            divisors.add(n // i)
    return sorted(divisors)

x = 2792599493716575
ans = get_divisors(x)

print(len(ans))
print(*ans, sep='\n')
