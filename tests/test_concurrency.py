
import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"
TOTAL_REQUESTS = 50
INITIAL_BALANCE_PAISE = 300


async def main():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=60,
    ) as client:
        # 1. Create a fresh account
        response = await client.post("/accounts")
        response.raise_for_status()
        account_id = response.json()["account_id"]

        # 2. Add ₹3.00 to the wallet
        response = await client.post(
            f"/accounts/{account_id}/topup",
            json={"amount_paise": INITIAL_BALANCE_PAISE},
        )
        response.raise_for_status()

        print(f"Account ID: {account_id}")
        print("Starting balance: ₹3.00")
        print("Sending 50 simultaneous consume requests...")

        # 3. Send all consume requests concurrently
        responses = await asyncio.gather(
            *[
                client.post(f"/accounts/{account_id}/consume")
                for _ in range(TOTAL_REQUESTS)
            ],
            return_exceptions=True,
        )

        successful = 0
        rejected = 0
        errors = []

        for result in responses:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif result.status_code == 200:
                successful += 1
            elif result.status_code == 409:
                rejected += 1
            else:
                errors.append(
                    f"Unexpected status {result.status_code}: "
                    f"{result.text}"
                )

        # 4. Check the final balance
        balance_response = await client.get(
            f"/accounts/{account_id}/balance"
        )
        balance_response.raise_for_status()
        final_balance = balance_response.json()["balance_paise"]

        print("\n--- Concurrency Test Results ---")
        print(f"Total requests: {TOTAL_REQUESTS}")
        print(f"Successful: {successful}")
        print(f"Rejected: {rejected}")
        print(f"Errors: {len(errors)}")
        print(f"Final balance: {final_balance} paise")

        # 5. Verify the expected results
        assert successful == 30, f"Expected 30 successes, got {successful}"
        assert rejected == 20, f"Expected 20 rejections, got {rejected}"
        assert not errors, f"Unexpected errors: {errors}"
        assert final_balance == 0, (
            f"Expected 0 balance, got {final_balance}"
        )

        print("\nPASS: All concurrency checks succeeded!")


if __name__ == "__main__":
    asyncio.run(main())