def func(number1: int, number2: int) -> list[int]:
    return [number1 + number2, number1 * number2, number1 - number2,
            number1 // number2 if number2 != 0 else 0]
