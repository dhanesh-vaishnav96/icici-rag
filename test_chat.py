import urllib.request, json

def post(q):
    data = json.dumps({"question": q}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8000/chat", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    return resp["answer"]

cases = [
    ("GREETING",     "hello"),
    ("GREETING2",    "hi, what can you do?"),
    ("NOISE",        "^ #$%# asdasd 123456"),
    ("NOISE2",       "!!!"),
    ("OUT-OF-SCOPE", "What is the weather in Mumbai?"),
    ("DOCUMENT Q",   "What is ICICI Pru iProtect Smart Plus?"),
]

for label, q in cases:
    ans = post(q)
    print(f"[{label}] Q: {q}")
    print(f"         A: {ans[:200]}")
    print()
