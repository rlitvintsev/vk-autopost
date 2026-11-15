import urllib.parse
import requests

# Вставь сюда скопированную строку VERIFIER из прошлого лога GitHub:
VERIFIER = "2MZsR9Qf7PSO7i4HkxJS0xUIWQkxffBu-0h4c5J0UwU"

# Вставь сюда скопированную целиком адресную строку со страницы OAuth Blank:
REDIRECTED_URL = "https://oauth.vk.com/blank.html?code=vk2.a.nHcCKSeze9YRwffwsWRl84-h_28OfjDV3vRjHsPKKSI-FgrTc15NWD4WVc3bvvq39KSIZK_S29sSk__Re_VhNjd2Pc8Zqdtm5mpzuka3H4I9H5NZTZf-LgMLiQLWfS27q-4UlRO5bg66C6-sS6C2yKgtz_i-2XAO71Z-aHvwJspbrEr5Jm1Z5P8fmr2a0gMdcc0LHyg3Vfqt1Bw3taDo4A&expires_in=600&device_id=KypzO5-gCAS1RQ0hCRTBCMiuwbsdTIGx0ZadhzQmjeyM9gIGhKtN-8n_c1GJzKip3nQo3IWiaVpcJGqIzIufow&state=mysecretstate12345678901234567890&ext_id=KFa06miiKlta8SzXEyZULQp%2BaSN69964o8yNdOEjthH%2FRB6TgzN4rPRaxwhpd5Uf2Tr4PgCwR8ZjVFVQFbZRPvbyrCG5WQp89l8LrRWMUZMM%2B9%2BqtE2eT25zKCtNhmKpqIJ29w%2FNr2QZjlwbGdYVWUgPCcFqozT3%2Bl%2FZt31slvqYFazs&type=code_v2"

parsed = urllib.parse.urlparse(REDIRECTED_URL)
params = urllib.parse.parse_qs(parsed.query)

code = params.get("code", [""])
device_id = params.get("device_id", [""])

id_host = ".".join(["id", "vk", "com"])
oauth_host = ".".join(["oauth", "vk", "com"])

resp = requests.post(
    f"https://{id_host}/oauth2/auth",
    data={
        "grant_type": "authorization_code",
        "code_verifier": VERIFIER,
        "redirect_uri": f"https://{oauth_host}/blank.html",
        "code": code,
        "client_id": "54898631",
        "device_id": device_id,
        "state": "mysecretstate12345678901234567890"
    }
).json()

print("ОТВЕТ VK ID:", resp)
