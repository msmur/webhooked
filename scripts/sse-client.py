import requests
import uuid


def sse_client(hook_id: str):
    url = f"http://localhost:8000/api/hooks/{hook_id}/webhooks/events"

    try:
        with requests.get(
            url, headers={"X-Client-ID": str(uuid.uuid4())}, stream=True
        ) as response:
            print(f"Connected to {url}")
            for line in response.iter_lines():
                if line:
                    print(f"Received: {line.decode('utf-8')}")
    except KeyboardInterrupt:
        print("\nClient disconnected. Exiting gracefully.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    sse_client(
        "hook-54fee0d3-66c0-4b9e-9bc7-b602cae42b95"
    )  # Replace with an actual hook ID
