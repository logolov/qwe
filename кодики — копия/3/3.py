import heapq

def get_prime_factors_of_factorial(n):
    """
    Находит все простые множители и их степени для n! с помощью формулы Лежандра
    """
    # Сито Эратосфена для поиска простых чисел до n
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
                
    primes = [i for i, prime in enumerate(is_prime) if prime]
    
    # Считаем степени вхождения по формуле Лежандра
    counts = {}
    for p in primes:
        count = 0
        m = n
        while m > 0:
            count += m // p
            m //= p
        counts[p] = count
    return counts

# Мы выяснили, что ваше число — это 4500!
N = 4500
counts = get_prime_factors_of_factorial(N)
primes = sorted(counts.keys())

# Ограничение на генерацию делителей
LIMIT = 10000

# Очередь с приоритетами (минимальная куча) для генерации строго по возрастанию
# Храним кортеж: (значение_делителя, индекс_последнего_использованного_простого_числа)
heap = [(1, 0)]
visited = {1}
result = []

print("Началась моментальная генерация первых 10 000 делителей...")

while heap and len(result) < LIMIT:
    current_div, p_idx = heapq.heappop(heap)
    result.append(current_div)
    
    for i in range(p_idx, len(primes)):
        p = primes[i]
        nxt = current_div * p
        
        # Проверяем по степеням, может ли nxt быть делителем N!
        # Для этого разложим nxt на текущие степени (проверяем, не превысили ли лимит степени p)
        # Так как мы идем последовательным умножением, достаточно проверить, что в nxt 
        # степень p не превышает допустимую. Но эффективнее контролировать генерацию:
        # Поскольку куча выдает их по возрастанию, мы добавляем nxt, только если он прошел валидацию.
        
        # Быстрая проверка: nxt должен делиться на p, проверяем сколько раз nxt делится на p.
        # Чтобы не делить длинные числа, мы можем отслеживать степени прямо в куче, 
        # но для первых 10000 делителей числа будут очень маленькими (они состоят из двоек, троек и т.д.),
        # поэтому простая проверка nxt на вхождение по степеням не займет времени.
        
        # Проверим, корректен ли делитель (его степень p не должна превысить counts[p])
        temp = nxt
        p_pow = 0
        while temp % p == 0:
            p_pow += 1
            temp //= p
            
        if p_pow <= counts[p] and nxt not in visited:
            visited.add(nxt)
            heapq.heappush(heap, (nxt, i))

# Сохраняем в файл ans.txt в строго требуемом формате
with open('ans.txt', 'w', encoding='utf-8') as f:
    f.write(f"{len(result)}\n")
    f.write('\n'.join(map(str, result)) + '\n')

print(f"Успешно! Файл ans.txt создан. Записано делителей: {len(result)}")
