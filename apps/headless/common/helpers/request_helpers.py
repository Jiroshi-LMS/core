from apps.headless.common.constants import TokenTransportMode


def get_refresh_transport_mode(request):
    """
    Returns:
        "cookie"  -> HttpOnly cookie
        "json"    -> JSON response
    """

    origin = request.headers.get("Origin")
    sec_fetch = request.headers.get("Sec-Fetch-Site")

    # HARD SECURITY RULE:
    # If browser context is detected → FORCE cookie
    if origin or sec_fetch or request.COOKIES.get("refresh_token"):
        return TokenTransportMode.COOKIE

    # DX OVERRIDE FOR NON-BROWSER CLIENTS
    client_type = request.headers.get("X-Client-Type")
    if client_type == TokenTransportMode.API:
        return TokenTransportMode.JSON

    # DEFAULT FALLBACK
    return TokenTransportMode.JSON
