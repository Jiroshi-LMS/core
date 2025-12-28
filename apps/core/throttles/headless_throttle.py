from rest_framework.throttling import SimpleRateThrottle


class StudentAuthBurstThrottle(SimpleRateThrottle):
    scope = "student_auth"

    def get_cache_key(self, request, view):
        ident = request.META.get("REMOTE_ADDR")
        return f"student_auth:{ident}"


class StudentRateThrottle(SimpleRateThrottle):
    scope = "student"

    def get_cache_key(self, request, view):
        student = getattr(request, "student", None)
        if not student:
            return None
        return f"student:{student.id}"


class StudentOpenRateThrottle(SimpleRateThrottle):
    scope = "student_public"

    def get_cache_key(self, request, view):
        ident = request.META.get("REMOTE_ADDR")
        return f"student_public:{ident}"