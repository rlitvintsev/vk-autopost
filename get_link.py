import base64
import hashlib
import os
import urllib.parse

verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest()).rstrip(b"=").decode("utf-8")

oauth_host = ".".join(["oauth", "vk", "com"])
id_host = ".".join(["id", "vk", "com"])

redirect_uri = f"https://{oauth_host}/blank.html"

params = {
    "response_type": "code",
    "client_id": "54898631",
    "redirect_uri": redirect_uri,
    "state": "mysecretstate12345678901234567890",
    "code_challenge": challenge,
    "code_challenge_method": "S256",
    "scope": "wall photos groups"
}

auth_url = f"https://{id_host}/authorize?" + urllib.parse.urlencode(params)
print("VERIFIER:", verifier)
print("LINK:", auth_url)
