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

'''