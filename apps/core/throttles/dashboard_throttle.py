from rest_framework.throttling import SimpleRateThrottle


class InstructorAuthBurstThrottle(SimpleRateThrottle):
    scope = "instructor_auth"

    def get_cache_key(self, request, view):
        ident = request.META.get("REMOTE_ADDR")
        return f"instructor_auth:{ident}"


class InstructorRateThrottle(SimpleRateThrottle):
    scope = "instructor"

    def get_cache_key(self, request, view):
        instructor = getattr(request, "user", None)
        if not instructor:
            return None
        return f"instructor:{instructor.id}"
