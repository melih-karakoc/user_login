from circuitbreaker import CircuitBreaker

class SocialAuthCircuitBreaker(CircuitBreaker):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 10
    EXPECTED_EXCEPTION = Exception
