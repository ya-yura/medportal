'''import asyncio
from backend.auth.mailer import send_verification_email


async def some_async_function():
    result = await send_verification_email(email='3201888@mail.ru', token='test', name='Sergey')
    print(result)
    return result


async def main():
    result = await send_verification_email(email='3201888@maili.rut', token='test', name='Sergey')
    print(f"Email sent: {result}")

if __name__ == "__main__":
    asyncio.run(main())

import pprint
from dataclasses import dataclass


@dataclass
class MyClass:
    name: str
    value: int


obj = MyClass(name='Sergey', value=42)


def element_generator(list):
    for item in list:
        yield item


list = dir(obj)

dir_list = element_generator(list)

for item in dir_list:
    print(item)'''



a = 1000000888
b = int(1000000888)

print(a is b)
