from rest_framework.throttling import SimpleRateThrottle

class InstructorRateThrottle(SimpleRateThrottle):
    scope = "instructor"

    def get_cache_key(self, request, view):
        instructor = getattr(request, "instructor", None)
        if not instructor:
            return None
        return f"instructor:{instructor.id}"
    

class AuthBurstThrottle(SimpleRateThrottle):
    scope = "auth"

    def get_cache_key(self, request, view):
        ident = request.META.get("REMOTE_ADDR")
        return f"auth:{ident}"


class StudentRateThrottle(SimpleRateThrottle):
    scope = "student"

    def get_cache_key(self, request, view):
        student = getattr(request, "student", None)
        if not student:
            return None
        return f"student:{student.id}"
