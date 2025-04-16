class Messages:
    class User:
        CREATED = "User created successfully"
        NOT_CREATED = "User could not be created"
        NOT_FOUND = "User not found"
        UPDATED = "User updated successfully"
        DELETED = "User deleted successfully"
        USERNAME_IN_USE = "Username already in use"
        EMAIL_IN_USE = "Email already in use"
        REGISTRATION_SUCCESSFUL = "Registration successful! Please log in."
        ALREADY_ACTIVE = "User is already active"
        RECOVERED = "User recovered successfully"

    class Auth:
        INVALID_CREDENTIALS = "Invalid username or password"
        FORBIDDEN = "You do not permission to perform this action"

    class Password:
        INVALID = "Password is invalid"

        class Validation:
            LENGTH = "Password must be at least 8 characters long"
            DIGIT = "Password must contain at least one digit"
            UPPERCASE = "Password must contain at least one uppercase letter"
            LOWERCASE = "Password must contain at least one lowercase letter"
            SPECIAL_CHARACTER = "Password must contain at least one special character"

    class General:
        INTERNAL_ERROR = "An unexpected error occurred"

    class Account:
        CREATED = "Account created successfully"
        UPDATED = "Account updated successfully"
        DELETED = "Account deleted successfully"
        NOT_FOUND = "Account not found"

    class Security:
        CREATED = "Security created successfully"
        UPDATED = "Security udpated successfully"
        DELETED = "Security deleted successfully"
        FETCHING = "Fetching securities data..."
        NOT_FOUND = "Security not found"

        @staticmethod
        def could_not_fetch_symbol(symbol: str):
            return f"Could not fetch data for {symbol}"

    class Trade:
        CREATED = "Trade created successfully"
        DELETED = "Trade deleted successfully"
        NOT_FOUND = "Trade not found"

    class Ledger:
        CREATED = "Ledger entry created successfully"
        DELETED = "Ledger entry deleted successfully"
        NOT_FOUND = "Ledger entry not found"

    class Allocation:
        CREATING = "Generating allocation plan..."
        CREATED = "Allocation plan generated successfully"

        class Validation:
            MAX_TARGET_ALLOCATION = (
                "Total target allocations cannot exceed 100% in an account"
            )
            AT_LEAST_ONE_GREATER_THAN_ZERO = "You need to specify a target allocation greater than 0 for at least one security"
            ALLOCATION_STRATEGY_REQUIRED = "The total allocation target must sum to 1 (100%) or an allocation strategy must be specified"

    class Transaction:
        PROCESSED = "Transaction processed successfully"
        REPROCESSING_ALL = "Reprocessing all transactions..."
        REPROCESSED_ALL = "All transactions reprocessed successfully"

        @staticmethod
        def processing(type: str):
            return f"Processing '{type}' transaction..."

        class Validation:
            WITHDRAWN_AMOUNT_CANNOT_BE_GREATER_THAN_BUYING_POWER = (
                "Withdrawn amount cannot be greater than account buying power"
            )

            @staticmethod
            def value_cannot_be_greater_than_buying_power(type: str):
                return f"Total value cannot be greater than account buying power for transaction of type '{type}'"

            @staticmethod
            def quantity_cannot_be_greater_than_position(type: str):
                return f"Quantity cannot be greater than current position for transaction of type '{type}'"
